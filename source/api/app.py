import re
import boto3
import botocore
import os
import json
import logging
import time
from botocore.config import Config
from chalice import Chalice, Response, ChaliceViewError, BadRequestError, UnauthorizedError, ForbiddenError, NotFoundError, ConflictError, TooManyRequestsError, IAMAuthorizer


# Misc global variables

app = Chalice(app_name='api')
app.log.setLevel(logging.DEBUG)
template_path = os.path.join(
    os.path.dirname(__file__), 'chalicelib', 'file-manager-ap-lambda.template')

sfm_config = json.loads(os.environ['botoConfig'])
config = Config(**sfm_config)
stack_prefix = os.environ['stackPrefix']

# Cognito resources
# From cloudformation stack

authorizer = IAMAuthorizer()

# AWS Clients

efs = boto3.client('efs', config=config)
serverless = boto3.client('lambda', config=config)
cfn = boto3.client('cloudformation', config=config)


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


def format_filesystem_response(filesystem):
    filesystem_id = filesystem['FileSystemId']
    new_filesystem_object = dict()
    try:
        name = filesystem["Name"]
        new_filesystem_object["name"] = name
    except KeyError:
        pass
    
    stack_status = describe_manager_stack(filesystem_id)

    lifecycle_state = filesystem['LifeCycleState']
    # TODO: BUG - Serialize datetime object to json properly
    #size_in_bytes = filesystem['SizeInBytes']

    # TODO: BUG - Serialize datetime object to json properly

    #creation_time = filesystem['CreationTime']

    if stack_status['Stacks'][0]['StackStatus'] == False:
        new_filesystem_object["managed"] = False
    elif stack_status['Stacks'][0]['StackStatus'] == 'DELETE_IN_PROGRESS':
        new_filesystem_object["managed"] = "Deleting"
    elif stack_status['Stacks'][0]['StackStatus'] == 'CREATE_IN_PROGRESS':
        new_filesystem_object["managed"] = "Creating"
    elif stack_status['Stacks'][0]['StackStatus'] == 'CREATE_COMPLETE':
        new_filesystem_object["managed"] = True
    
    new_filesystem_object["file_system_id"] = filesystem_id
    new_filesystem_object["lifecycle_state"] = lifecycle_state
    #new_filesystem_object["size_in_bytes"] = size_in_bytes
    #new_filesystem_object["creation_time"] = creation_time

    return new_filesystem_object


def read_template_file():
    with open(template_path, 'r') as f:
        template = f.read()
    return template


def describe_manager_stack(filesystem_id):
    stack_name = '{prefix}-ManagedResources-{filesystem}'.format(prefix=stack_prefix, filesystem=filesystem_id)
    try:
        response = cfn.describe_stacks(
            StackName=stack_name,
        )
    except botocore.exceptions.ClientError as error:
        app.log.error(error)
        if error.response['Error']['Code'] == 'ValidationError':
            return {
                'Stacks': [{
                    'StackStatus': False
                }]
            }
        else:
            raise ChaliceViewError(error)
    else:
        return response


def delete_manager_stack(filesystem_id):
    stack_name = '{prefix}-ManagedResources-{filesystem}'.format(prefix=stack_prefix, filesystem=filesystem_id)
    try:
        response = cfn.delete_stack(
            StackName=stack_name,
        )
    except botocore.exceptions.ClientError as error:
        app.log.error(error)
        raise ChaliceViewError(error)
    else:
        return response


def create_manager_stack(filesystem_id, uid, gid, path, subnet_ids, security_groups):
    stack_name = '{prefix}-ManagedResources-{filesystem}'.format(prefix=stack_prefix, filesystem=filesystem_id)
    template_body = read_template_file()
    try:
        response = cfn.create_stack(
            StackName=stack_name,
            TemplateBody=template_body,
            Parameters=[
                {
                    'ParameterKey': 'FileSystemId',
                    'ParameterValue': filesystem_id,
                },
                {
                    'ParameterKey': 'PosixUserUid',
                    'ParameterValue': uid,
                },
                {
                    'ParameterKey': 'PosixUserGid',
                    'ParameterValue': gid,
                },
                {
                    'ParameterKey': 'RootDirectoryPath',
                    'ParameterValue': path,
                },
                {
                    'ParameterKey': 'VpcConfigSgIds',
                    'ParameterValue': ','.join(security_groups),
                },
                {
                    'ParameterKey': 'VpcConfigSubnetId',
                    'ParameterValue': subnet_ids[0],
                },
            ],
            TimeoutInMinutes=15,
            Capabilities=[
                'CAPABILITY_NAMED_IAM',
            ],
            OnFailure='DELETE',
        )
    except botocore.exceptions.ClientError as error:
        app.log.error(error)
        raise ChaliceViewError(error)
    else:
        return response


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
            try:
                formatted = format_filesystem_response(filesystem)
            except botocore.exceptions.ClientError as error:
                app.log.error(error)
                raise ChaliceViewError("Check API logs")
            else:
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
        uid = json_body['uid']
        gid = json_body['gid']
        path = json_body['path']
    except KeyError as error:
        app.log.error(error)
        raise BadRequestError("Check API logs")

    try:
        response = create_manager_stack(filesystem_id, uid, gid, path, subnet_ids, security_groups)
    except Exception as error:
        app.log.error(error)
        app.log.debug('Failed to create stack, deleting it.')
        raise ChaliceViewError('Check API Logs')
    else:
        return response


@app.route('/filesystems/{filesystem_id}/lambda', methods=['DELETE'], cors=True, authorizer=authorizer)
def delete_filesystem_lambda(filesystem_id):
    stack_status = describe_manager_stack(filesystem_id)
    if stack_status['Stacks'][0]['StackStatus'] == 'CREATE_COMPLETE':
        try:
            delete_stack = delete_manager_stack(filesystem_id)
            app.log.info(delete_stack)
        except Exception as error:
            raise ChaliceViewError(error)
    else:
        raise BadRequestError('No valid managed stack for this filesystem')


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

