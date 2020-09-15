import boto3
import base64
import botocore
import os
import yaml
import json
import logging
import time
from requests_toolbelt import MultipartDecoder
import zipfile
from chalice import Chalice, Response, ChaliceViewError, BadRequestError, UnauthorizedError, ForbiddenError, NotFoundError, ConflictError, TooManyRequestsError


# Misc global variables


app = Chalice(app_name='api')
app.log.setLevel(logging.DEBUG)
app.api.binary_types.append('multipart/form-data')
efs_lambda = os.path.join(
    os.path.dirname(__file__), 'chalicelib', 'efs_lambda.py')

# AWS Clients

efs = boto3.client('efs')
serverless = boto3.client('lambda')
iam = boto3.client('iam')


# Helper functions
def parse_multipart_object(headers, content):
    for header in headers.split(';'):
        # Only get the specific dropzone form values we need
        if header == 'form-data':
            continue
        elif 'filename' in header:
            filename_object = {"filename": header.split('"')[1::2][0], "content": content}
            return filename_object
        elif 'name="file"' in header:
            continue
        else:
            header_name = header.split('"')[1::2][0]
            metadata_object = {header_name: content}
            return metadata_object


def proxy_operation_to_efs_lambda(filesystem_id, event):
    lambda_name = '{filesystem}-manager-lambda'.format(filesystem=filesystem_id)
    try:
        response = serverless.invoke(
            InvocationType='RequestResponse',
            FunctionName=lambda_name,
            Payload=bytes(json.dumps(event), encoding='utf-8')
        )
    except botocore.exceptions.ClientError as error:
        app.log.error(error)
        raise ChaliceViewError(error)
    else:
        return response


def create_filesystem_access_point(filesystem_id):
    try:
        response = efs.create_access_point(
        FileSystemId=filesystem_id,
        PosixUser={
            'Uid': 1000,
            'Gid': 1000
        },
        RootDirectory={
            'Path': '/efs',
            'CreationInfo': {
                'OwnerUid': 1000,
                'OwnerGid': 1000,
                'Permissions': '777'
            }
        }
    )
    except botocore.exceptions.ClientError as error:
        return ChaliceViewError(error)
    else:
        access_point_arn = response['AccessPointArn']
        return access_point_arn


def delete_access_point(access_point_arn):
    try:
        efs.delete_access_point(
            AccessPointId=access_point_arn)
    except botocore.exceptions.ClientError as error:
        app.log.error(error)
        raise BadRequestError(error)


def format_filesystem_response(filesystem):
    filesystem_id = filesystem['FileSystemId']

    is_managed = has_manager_lambda(filesystem_id)

    lifecycle_state = filesystem['LifeCycleState']
    # TODO: BUG - Serialize datetime object to json properly
    #size_in_bytes = filesystem['SizeInBytes']

    # TODO: BUG - Serialize datetime object to json properly

    #creation_time = filesystem['CreationTime']

    new_filesystem_object = dict()

    if is_managed is True:
        new_filesystem_object["managed"] = True
    else:
        new_filesystem_object["managed"] = False

    new_filesystem_object["file_system_id"] = filesystem_id
    new_filesystem_object["lifecycle_state"] = lifecycle_state
    #new_filesystem_object["size_in_bytes"] = size_in_bytes
    #new_filesystem_object["creation_time"] = creation_time

    return new_filesystem_object


def create_function_zip():
    # TODO: Should this be a unique name / path based on give filesystem?
    zip_path = "/tmp/lambda.zip"
    with zipfile.ZipFile(zip_path, 'w') as z:
        z.write(efs_lambda)
    with open(zip_path, 'rb') as f:
        code = f.read()
    return code


def create_function_role(filesystem_name):
    # TODO: This will need to be updated to allow actual operations
    basic_role = """
        Version: '2012-10-17'
        Statement:
            - Effect: Allow
              Principal: 
                Service: lambda.amazonaws.com
              Action: sts:AssumeRole
        """
    # TODO: Add try / except / else blocks and handle errors
    # lambda.awazonaws.com can assume this role.
    role_response = iam.create_role(RoleName='{filesystem}-manager-role'.format(filesystem=filesystem_name),
                    AssumeRolePolicyDocument=json.dumps(yaml.load(basic_role)))

    # TODO: Change these to a least privilege role defined in the cloudformation
    # This role has the AWSLambdaBasicExecutionRole managed policy.
    iam.attach_role_policy(RoleName='{filesystem}-manager-role'.format(filesystem=filesystem_name),
                           PolicyArn='arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole')
    iam.attach_role_policy(RoleName='{filesystem}-manager-role'.format(filesystem=filesystem_name),
                           PolicyArn='arn:aws:iam::aws:policy/AdministratorAccess')
    app.log.debug(role_response)
    role_arn = role_response['Role']['Arn']
    return role_arn


def create_function(filesystem_id, access_point_arn, vpc):
    code = create_function_zip()
    # TODO: Figure out whats up here
    #role = create_function_role(filesystem_id)
    try:
        response = serverless.create_function(
            FunctionName='{filesystem}-manager-lambda'.format(filesystem=filesystem_id),
            Runtime='python3.8',
            Role='arn:aws:iam::764127651952:role/RootAccessLambdaRole', #TODO: remove
            #Role=role,
            Handler='var/task/chalicelib/efs_lambda.lambda_handler',
            Code={
                'ZipFile': code
            },
            Description='Lambda function to process file manager operations for filesystem: {filesystem}'.format(filesystem=filesystem_id),
            Timeout=60,
            MemorySize=512,
            Publish=True,
            VpcConfig=vpc,
            # TODO: Add tags to identify this is managed by the file system manager app
            # Environment={
            #     'Variables': {
            #         'string': 'string'
            #     }
            # },
            # Tags={
            #     'string': 'string'
            # },
            FileSystemConfigs=[
                {
                    'Arn': access_point_arn,
                    'LocalMountPath': '/mnt/efs'
                },
            ]
        )
    except botocore.exceptions.ClientError as error:
        app.log.error(error)
        app.log.debug('failed to create lambda, deleting access point')
        delete_access_point(access_point_arn)
        raise ChaliceViewError("Check API logs")
    else:
        return response


# Routes
@app.route('/')
def index():
    return {'hello': 'world'}


def has_manager_lambda(filesystem_id):
    try:
        serverless.get_function(
            FunctionName='{filesystem}-manager-lambda'.format(filesystem=filesystem_id)
        )
    except botocore.exceptions.ClientError as error:
        if error.response['Error']['Code'] == 'ResourceNotFoundException':
            return False
        else:
            app.log.error(error)
            return False
    else:
        return True


@app.route('/filesystems', methods=["GET"], cors=True)
def list_filesystems():
    try:
        response = efs.describe_file_systems()
    except botocore.exceptions.ClientError as error:
        app.log.error(error)
        raise ChaliceViewError("Check API logs")
    else:
        filesystems = response['FileSystems']
        #app.log.debug(filesystems)
        formatted_filesystems = []
        for filesystem in filesystems:
            formatted = format_filesystem_response(filesystem)
            formatted_filesystems.append(formatted)
        return formatted_filesystems


@app.route('/filesystems/{filesystem_id}', methods=['GET'], cors=True)
def describe_filesystem(filesystem_id):
    try:
        response = efs.describe_file_systems(
            FileSystemId=filesystem_id
        )
    except botocore.exceptions.ClientError as error:
        app.log.error(error)
        raise ChaliceViewError("Check API logs")
    else:
        return json.dumps(response, indent=4, sort_keys=True, default=str)


@app.route('/filesystems/{filesystem_id}/netinfo', methods=['GET'], cors=True)
def get_netinfo_for_filesystem(filesystem_id):
    netinfo = []
    try:
        response = efs.describe_mount_targets(
            FileSystemId=filesystem_id
        )
    except botocore.exceptions.ClientError as error:
        app.log.debug(error)
        raise ChaliceViewError
    else:
        mount_targets = response['MountTargets']
        app.log.debug(mount_targets)
        for target in mount_targets:
            mount_target_id = target['MountTargetId']
            try:
                response = efs.describe_mount_target_security_groups(
                    MountTargetId=mount_target_id
                )
            except botocore.exceptions.ClientError as error:
                app.log.debug(error)
                raise ChaliceViewError
            else:
                security_groups = response['SecurityGroups']
                vpc_item = {'{id}'.format(id=mount_target_id): {'security_groups': security_groups, 'subnet_id': target['SubnetId']}}
                netinfo.append(vpc_item)

    return netinfo


@app.route('/filesystems/{filesystem_id}/lambda', methods=['POST'], cors=True)
def create_filesystem_lambda(filesystem_id):
    request = app.current_request
    json_body = request.json_body

    try:
        subnet_id = json_body['subnetId']
        security_groups = json_body['securityGroups']
    except KeyError as error:
        app.log.error(error)
        raise BadRequestError("Check API logs")
    else:
        vpc_config = {
            'SubnetIds': [
                subnet_id,
            ],
            'SecurityGroupIds': security_groups
        }

    try:
        access_point_arn = create_filesystem_access_point(filesystem_id)
    except Exception as error:
        app.log.error(error)
        raise ChaliceViewError('Check API Logs')

    # TODO: 100% should not do this, keeping until I look into a better method to ensure access point is available
    time.sleep(10)

    try:
        response = create_function(filesystem_id, access_point_arn, vpc_config)
    except Exception as error:
        app.log.error(error)
        raise ChaliceViewError('Check API Logs')
    else:
        return response


@app.route('/upload/{filesystem_id}', methods=["POST"], content_types=['multipart/form-data'], cors=True)
def upload(filesystem_id):
    if app.current_request.query_params['path']:
        path = app.current_request.query_params['path']
    else:
        app.log.error('Missing required query param: path')
        raise BadRequestError('Missing required query param: path')

    #app.log.debug((app.current_request.raw_body)
    #app.log.debug((app.current_request.headers['content-type'])

    parsed_form_object = {}
    for part in MultipartDecoder(app.current_request.raw_body, app.current_request.headers['content-type']).parts:
        raw_name = str(part.headers[b'Content-Disposition'], 'utf-8')
        if "filename" in raw_name:
            b64_content = str(base64.b64encode(part.content), 'utf-8')
            parsed_object = parse_multipart_object(raw_name, b64_content)
        else:
            parsed_object = parse_multipart_object(raw_name, part.content.decode())

        if parsed_object is None:
            pass
        else:
            parsed_form_object.update(parsed_object)

    app.log.debug(parsed_form_object)

    filemanager_event = {"operation": "upload", "path": path, "form_data": parsed_form_object}

    operation_result = proxy_operation_to_efs_lambda(filesystem_id, filemanager_event)

    # TODO: Fix this to also parse payload for status code

    if operation_result['StatusCode'] == 200:
        payload_encoded = operation_result['Payload']
        payload = json.loads(payload_encoded.read().decode("utf-8"))
        return payload
    else:
        payload_encoded = operation_result['Payload']
        payload = json.loads(payload_encoded.read().decode("utf-8"))
        app.log.error(payload)
        raise ChaliceViewError('Error uploading file: {payload}'.format(payload=payload))


@app.route('/objects/{filesystem_id}/dir', methods=['POST'], content_types=['application/x-www-form-urlencoded'], cors=True)
def make_dir(filesystem_id):
    try:
        name = app.current_request.query_params['name']
        path = app.current_request.query_params['path']
    except KeyError as e:
        app.log.error('Missing required query param: {e}'.format(e=e))
        raise BadRequestError('Missing required query param: {e}'.format(e=e))
    else:
        filemanager_event = {"operation": "make_dir", "path": path, "name": name}
        operation_result = proxy_operation_to_efs_lambda(filesystem_id, filemanager_event)
        # TODO: Fix this to also parse payload for status code

        if operation_result['StatusCode'] == 200:
            payload_encoded = operation_result['Payload']
            payload = json.loads(payload_encoded.read().decode("utf-8"))
            return payload
        else:
            payload_encoded = operation_result['Payload']
            payload = json.loads(payload_encoded.read().decode("utf-8"))
            app.log.error(payload)
            raise ChaliceViewError('Error creating dir: {payload}'.format(payload=payload))


@app.route('/objects/{filesystem_id}', methods=['GET'], cors=True)
def list_objects(filesystem_id):
    if app.current_request.query_params['path']:
        path = app.current_request.query_params['path']
    else:
        app.log.error('Missing required query param: path')
        raise BadRequestError('Missing required query param: path')

    filemanager_event = {"operation": "list", "path": path}
    operation_result = proxy_operation_to_efs_lambda(filesystem_id, filemanager_event)

    if operation_result['StatusCode'] == 200:
        payload_encoded = operation_result['Payload']
        payload = json.loads(payload_encoded.read().decode("utf-8"))
        return payload
    else:
        payload_encoded = operation_result['Payload']
        payload = json.loads(payload_encoded.read().decode("utf-8"))
        app.log.error(payload)
        raise ChaliceViewError('Error listing objects: {payload}'.format(payload=payload))

