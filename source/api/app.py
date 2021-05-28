import re
import boto3
import botocore
import os
import json
import logging
import time
import zipfile
from botocore.config import Config
from chalice import Chalice, Response, ChaliceViewError, BadRequestError, UnauthorizedError, ForbiddenError, NotFoundError, ConflictError, TooManyRequestsError, IAMAuthorizer


# Misc global variables

app = Chalice(app_name='api')
app.log.setLevel(logging.DEBUG)
efs_lambda = os.path.join(
    os.path.dirname(__file__), 'chalicelib', 'efs_lambda.py')

sfm_config = json.loads(os.environ['botoConfig'])
config = Config(**sfm_config)

# Cognito resources
# From cloudformation stack

authorizer = IAMAuthorizer()

# AWS Clients

efs = boto3.client('efs', config=config)
serverless = boto3.client('lambda', config=config)
iam = boto3.client('iam', config=config)


# Helper functions

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


def create_filesystem_access_point(filesystem_id, uid, gid, path):
    try:
        response = efs.create_access_point(
        FileSystemId=filesystem_id,
        Tags=[
            {
                'Key': 'Name',
                'Value': 'simple-file-manager-access-point'
            },
        ],
        PosixUser={
            'Uid': uid,
            'Gid': gid
        },
        RootDirectory={
            'Path': path,
            'CreationInfo': {
                'OwnerUid': uid,
                'OwnerGid': gid,
                'Permissions': '777'
            }
        }
    )
    except botocore.exceptions.ClientError as error:
        return ChaliceViewError(error)
    else:
        access_point_arn = response['AccessPointArn']
        access_point_id = response['AccessPointId']
        access_point = {"access_point_arn": access_point_arn, "access_point_id": access_point_id}
        return access_point


def delete_access_point(access_point_arn):
    try:
        efs.delete_access_point(
            AccessPointId=access_point_arn)
    except botocore.exceptions.ClientError as error:
        app.log.error(error)
        raise BadRequestError(error)


def get_access_point(filesystem_id):
    try:
        response = efs.describe_access_points(
            FileSystemId=filesystem_id
        )
    except botocore.exceptions.ClientError as error:
        raise Exception(error)
    else:
        access_point_id = ''
        access_points = response['AccessPoints']

        for access_point in access_points:
            tags = access_point['Tags']
            for tag in tags:
                key = tag['Key']
                if key == 'Name':
                    if tag['Value'] == 'simple-file-manager-access-point':
                        tmp_access_point_id = access_point['AccessPointId']
                        access_point_id = tmp_access_point_id
        if access_point_id == '':
            raise Exception('No file manager access point found')
        else:
            return access_point_id


def format_filesystem_response(filesystem):
    filesystem_id = filesystem['FileSystemId']
    new_filesystem_object = dict()
    try:
        name = filesystem["Name"]
        new_filesystem_object["name"] = name
    except KeyError:
        pass
    
    is_managed = has_manager_lambda(filesystem_id)

    lifecycle_state = filesystem['LifeCycleState']
    # TODO: BUG - Serialize datetime object to json properly
    #size_in_bytes = filesystem['SizeInBytes']

    # TODO: BUG - Serialize datetime object to json properly

    #creation_time = filesystem['CreationTime']

    if is_managed["Status"] is True:
        if is_managed["Message"] == "Active":
            new_filesystem_object["managed"] = True
        else:
            new_filesystem_object["managed"] = "Creating"
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


def create_function_role(filesystem_id):
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "",
                "Effect": "Allow",
                "Principal": {
                    "Service": "lambda.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }

    role_name = f'{filesystem_id}-manager-role'
    path = '/'
    description = f'IAM Role for filesystem {filesystem_id} manager lambda'

    # TODO: Add IAM resource tags
    try:
        role_response = iam.create_role(
            Path=path,
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description=description,
            MaxSessionDuration=3600
        )
    except Exception as e:
        app.log.debug(e)
        return ChaliceViewError(e)
    

    iam.attach_role_policy(RoleName=role_name,
                           PolicyArn='arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole')
    iam.attach_role_policy(RoleName=role_name,
                           PolicyArn='arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole')
    iam.attach_role_policy(RoleName=role_name,
                           PolicyArn='arn:aws:iam::aws:policy/AmazonElasticFileSystemClientReadWriteAccess')
    
    
    role_arn = str(role_response['Role']['Arn'])
    
    return role_arn

def delete_function_role(filesystem_id):
    role_name = f'{filesystem_id}-manager-role'

    try:
        iam.detach_role_policy(
            RoleName=role_name,
            PolicyArn='arn:aws:iam::aws:policy/AmazonElasticFileSystemClientReadWriteAccess'
        )
        iam.detach_role_policy(
            RoleName=role_name,
            PolicyArn='arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole'
        )
        iam.detach_role_policy(
            RoleName=role_name,
            PolicyArn='arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole'
        )
        response = iam.delete_role(
            RoleName=role_name
        )
    except botocore.exceptions.ClientError as error:
        raise Exception(error)
    else:
        return response

def create_function(filesystem_id, access_point_arn, vpc):
    code = create_function_zip()
    role = create_function_role(filesystem_id)
    # TODO: Add retry logic instead of relying on sleep
    time.sleep(15)
    try:
        response = serverless.create_function(
            FunctionName='{filesystem}-manager-lambda'.format(filesystem=filesystem_id),
            Runtime='python3.8',
            Role=role,
            Handler='var/task/chalicelib/efs_lambda.lambda_handler',
            Code={
                'ZipFile': code
            },
            Description='Lambda function to process file manager operations for filesystem: {filesystem}'.format(filesystem=filesystem_id),
            Timeout=60,
            MemorySize=512,
            Publish=True,
            VpcConfig=vpc,
            FileSystemConfigs=[
                {
                    'Arn': access_point_arn,
                    'LocalMountPath': '/mnt/efs'
                },
            ]
        )
    except botocore.exceptions.ClientError as error:
        raise Exception(error)
    else:
        return response

def delete_function(filesystem_id):
    try:
        response = serverless.delete_function(
            FunctionName='{filesystem}-manager-lambda'.format(filesystem=filesystem_id)
        )
    except botocore.exceptions.ClientError as error:
        raise Exception(error)
    else:
        return response

def has_manager_lambda(filesystem_id):
    try:
        response = serverless.get_function(
            FunctionName='{filesystem}-manager-lambda'.format(filesystem=filesystem_id)
        )
    except botocore.exceptions.ClientError as error:
        if error.response['Error']['Code'] == 'ResourceNotFoundException':
            return {"Status": False}
        else:
            app.log.error(error)
            return {"Status": False}
    else:
        function_state = response['Configuration']['State']
        if function_state == 'Active':
            return {"Status": True, "Message": "Active"}

        elif function_state == 'Pending':
            return {"Status": True, "Message": "Creating"}

        else:
            return {"Status": False}


# Routes
@app.route('/')
def index():
    return {'hello': 'world'}


@app.route('/filesystems', methods=["GET"], cors=True, authorizer=authorizer)
def list_filesystems():
    try:
        response = efs.describe_file_systems()
    except botocore.exceptions.ClientError as error:
        app.log.error(error)
        raise ChaliceViewError("Check API logs")
    else:
        filesystems = response['FileSystems']
        formatted_filesystems = []
        for filesystem in filesystems:
            formatted = format_filesystem_response(filesystem)
            formatted_filesystems.append(formatted)
        return formatted_filesystems


@app.route('/filesystems/{filesystem_id}', methods=['GET'], cors=True, authorizer=authorizer)
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


@app.route('/filesystems/{filesystem_id}/netinfo', methods=['GET'], cors=True, authorizer=authorizer)
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


@app.route('/filesystems/{filesystem_id}/lambda', methods=['POST'], cors=True, authorizer=authorizer)
def create_filesystem_lambda(filesystem_id):
    request = app.current_request
    json_body = request.json_body

    try:
        subnet_ids = json_body['subnetIds']
        security_groups = json_body['securityGroups']
        uid = int(json_body['uid'])
        gid = int(json_body['gid'])
        path = json_body['path']
    except KeyError as error:
        app.log.error(error)
        raise BadRequestError("Check API logs")
    else:
        vpc_config = {
            'SubnetIds': subnet_ids,
            'SecurityGroupIds': security_groups
        }

    try:
        access_point = create_filesystem_access_point(filesystem_id, uid, gid, path)
    except Exception as error:
        app.log.error(error)
        raise ChaliceViewError('Check API Logs')

    # TODO: Add retry logic instead of relying on sleep
    time.sleep(10)

    try:
        response = create_function(filesystem_id, access_point["access_point_arn"], vpc_config)
    except Exception as error:
        app.log.error(error)
        app.log.debug('Failed to create lambda, deleting access point')
        delete_access_point(access_point["access_point_id"])
        raise ChaliceViewError('Check API Logs')
    else:
        return response


@app.route('/filesystems/{filesystem_id}/lambda', methods=['DELETE'], cors=True, authorizer=authorizer)
def delete_filesystem_lambda(filesystem_id):
    file_manager_lambda = has_manager_lambda(filesystem_id)
    if file_manager_lambda['Status'] is True and file_manager_lambda['Message'] == 'Active':
        try:
            delete_lambda = delete_function(filesystem_id)
            app.log.info(delete_lambda)
            access_point_id = get_access_point(filesystem_id)
            delete_ap = delete_access_point(access_point_id)
            app.log.info(delete_ap)
            delete_role = delete_function_role(filesystem_id)
            app.log.info(delete_role)
        except Exception as error:
            raise ChaliceViewError(error)
    else:
        raise BadRequestError('No valid file manager lambda for this filesystem')


@app.route('/objects/{filesystem_id}/upload', methods=["POST"], cors=True, authorizer=authorizer)
def upload(filesystem_id):
    print(app.current_request.query_params)
    try:
        path = app.current_request.query_params['path']
        filename = app.current_request.query_params['filename']
    except KeyError as e:
        app.log.error('Missing required query param: {e}'.format(e=e))
        raise BadRequestError('Missing required query param: {e}'.format(e=e))

    request = app.current_request
    chunk_data = request.json_body
    chunk_data["filename"] = filename

    filemanager_event = {"operation": "upload", "path": path, "chunk_data": chunk_data}

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


@app.route('/objects/{filesystem_id}/download', methods=["GET"], cors=True, authorizer=authorizer)
def download(filesystem_id):
    print(app.current_request.query_params)
    try:
        path = app.current_request.query_params['path']
        filename = app.current_request.query_params['filename']
    except KeyError as e:
        app.log.error('Missing required query param: {e}'.format(e=e))
        raise BadRequestError('Missing required query param: {e}'.format(e=e))
    else:
        if 'dzchunkindex' and 'dzchunkbyteoffset' in app.current_request.query_params:
            chunk_index = app.current_request.query_params['dzchunkindex']
            chunk_offset = app.current_request.query_params['dzchunkbyteoffset']
            filemanager_event = {"operation": "download", "path": path, "filename": filename,
                                 "chunk_data": {"dzchunkindex": int(chunk_index), "dzchunkbyteoffset": int(chunk_offset)}}
            operation_result = proxy_operation_to_efs_lambda(filesystem_id, filemanager_event)
            payload_encoded = operation_result['Payload']
            payload = json.loads(payload_encoded.read().decode("utf-8"))
            return payload
        elif 'dzchunkindex' and 'dzchunkbyteoffset' not in app.current_request.query_params:
            filemanager_event = {"operation": "download", "path": path, "filename": filename}
            operation_result = proxy_operation_to_efs_lambda(filesystem_id, filemanager_event)
            payload_encoded = operation_result['Payload']
            payload = json.loads(payload_encoded.read().decode("utf-8"))
            return payload
        else:
            raise BadRequestError('Unsupported or missing query params')


@app.route('/objects/{filesystem_id}/dir', methods=['POST'], cors=True, authorizer=authorizer)
def make_dir(filesystem_id):
    request = app.current_request
    dir_data = request.json_body

    try:
        name = dir_data['name']
        path = dir_data['path']
    except KeyError as e:
        app.log.error('Missing required param: {e}'.format(e=e))
        raise BadRequestError('Missing required param: {e}'.format(e=e))
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


@app.route('/objects/{filesystem_id}', methods=['DELETE'], cors=True, authorizer=authorizer)
def delete_object(filesystem_id):
    try:
        name = app.current_request.query_params['name']
        path = app.current_request.query_params['path']
    except KeyError as e:
        app.log.error('Missing required query param: {e}'.format(e=e))
        raise BadRequestError('Missing required query param: {e}'.format(e=e))
    else:
        filemanager_event = {"operation": "delete", "path": path, "name": name}
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


@app.route('/objects/{filesystem_id}', methods=['GET'], cors=True, authorizer=authorizer)
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

