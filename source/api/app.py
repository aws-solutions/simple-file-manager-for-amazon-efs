######################################################################################################################
#  Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.                                                #
#                                                                                                                    #
#  Licensed under the Apache License, Version 2.0 (the "License"). You may not use this file except in compliance    #
#  with the License. A copy of the License is located at                                                             #
#                                                                                                                    #
#      http://www.apache.org/licenses/LICENSE-2.0                                                                    #
#                                                                                                                    #
#  or in the 'license' file accompanying this file. This file is distributed on an 'AS IS' BASIS, WITHOUT WARRANTIES #
#  OR CONDITIONS OF ANY KIND, express or implied. See the License for the specific language governing permissions    #
#  and limitations under the License.                                                                                #
######################################################################################################################
"""API for Simple File Manager for Amazon EFS"""
import os
import logging
import json
import botocore
from botocore.config import Config
import boto3
from chalice import Chalice, ChaliceViewError, BadRequestError, IAMAuthorizer


# Misc global variables

app = Chalice(app_name='api')
app.log.setLevel(logging.DEBUG)
TEMPLATE_PATH = os.path.join(
    os.path.dirname(__file__), 'chalicelib', 'file-manager-ap-lambda.template')

SFM_CONFIG = json.loads(os.environ['botoConfig'])
CONFIG = Config(**SFM_CONFIG)
STACK_PREFIX = os.environ['stackPrefix']

# Cognito resources
# From cloudformation stack

AUTHORIZER = IAMAuthorizer()

# AWS Clients

EFS = boto3.client('efs', config=CONFIG)
SERVERLESS = boto3.client('lambda', config=CONFIG)
CFN = boto3.client('cloudformation', config=CONFIG)


# Helper functions

def proxy_operation_to_efs_lambda(filesystem_id, operation):
    """
    Proxies file system operations to the file manager lambda associated to a
    given filesystem

    :param filesystem_id: The id of the filesystem
    :param operation: The filesystem operation
    :returns: The filesystem operation result
    :raises ChaliceViewError
    """
    lambda_name = '{filesystem}-manager-lambda'.format(filesystem=filesystem_id)
    try:
        response = SERVERLESS.invoke(
            InvocationType='RequestResponse',
            FunctionName=lambda_name,
            Payload=bytes(json.dumps(operation), encoding='utf-8')
        )
    except botocore.exceptions.ClientError as error:
        app.log.error(error)
        raise ChaliceViewError(error)
    else:
        return response


def format_filesystem_response(filesystem):
    """
    Formats the response from EFS for a filesystem description

    :param filesystem: The filesystem response to format
    :returns: The formatted filesystem response
    """
    filesystem_id = filesystem['FileSystemId']
    new_filesystem_object = dict()
    try:
        name = filesystem["Name"]
        new_filesystem_object["name"] = name
    except KeyError:
        pass

    stack_status = describe_manager_stack(filesystem_id)

    lifecycle_state = filesystem['LifeCycleState']

    if stack_status['Stacks'][0]['StackStatus'] is False:
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
    """
    Loads file manager managed resources template file
    """
    with open(TEMPLATE_PATH, 'r') as template_file:
        template = template_file.read()
    return template


def describe_manager_stack(filesystem_id):
    """
    Describes the file manager managed fresources stack for a given filesystem

    :param filesystem_id: The id of the filesystem to describe
    :returns: File manager stack details
    :raises ChaliceViewError
    """
    stack_name = '{prefix}-ManagedResources-{filesystem}'.format(prefix=STACK_PREFIX, \
        filesystem=filesystem_id)
    try:
        response = CFN.describe_stacks(
            StackName=stack_name,
        )
    except botocore.exceptions.ClientError as error:
        app.log.error(error)
        stack_status = {'Stacks': [{
            'StackStatus': False
        }]}
        return stack_status if error.response['Error']['Code'] == 'ValidationError' \
            else ChaliceViewError(error)
    else:
        return response


def delete_manager_stack(filesystem_id):
    """
    Deletes a file manager managed resources stack

    :param filesystem_id: The id of the filesystem to delete
    :returns: Deletion status
    :raises ChaliceViewError
    """
    stack_name = '{prefix}-ManagedResources-{filesystem}'.format(prefix=STACK_PREFIX, \
        filesystem=filesystem_id)
    try:
        response = CFN.delete_stack(
            StackName=stack_name,
        )
    except botocore.exceptions.ClientError as error:
        app.log.error(error)
        raise ChaliceViewError(error)
    else:
        return response


def create_manager_stack(filesystem_id, uid, gid, path, subnet_ids, security_groups):
    """
    Creates a file manager managed resources stack

    :param filesystem_id: The id of the filesystem to create resources for
    :param uid: UID that will be used in the EFS access point
    :param gid: GID that will be used in the EFS access point
    :param path: Path that will be used in the EFS access point
    :param subnet_ids: Subnet IDs that the lambda function will use
    :param security_groups: Security groups that the lambda function will use
    :returns: Create status
    :raises ChaliceViewError
    """
    stack_name = '{prefix}-ManagedResources-{filesystem}'.format(prefix=STACK_PREFIX, \
        filesystem=filesystem_id)

    template_body = read_template_file()

    try:
        response = CFN.create_stack(
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
                    'ParameterKey': 'VpcConfigSubnetIds',
                    'ParameterValue': ','.join(subnet_ids),
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


def format_operation_response(result, error_message):
    """
    Formats filesystem operation results from file manager lambda

    :param result: The filesystem operation result
    :param error_message: Custom error message to format response with
    :returns: Formatted filesystem operation response
    :raises ChaliceViewError
    """
    response = {}

    status = result['StatusCode']
    payload_encoded = result['Payload']
    payload = json.loads(payload_encoded.read().decode("utf-8"))

    if status == 200:
        response = payload
    else:
        app.log.error(payload)
        response = ChaliceViewError('{message}: \
            {payload}'.format(message=error_message, payload=payload))

    return response


# Routes

@app.route('/filesystems', methods=["GET"], cors=True, authorizer=AUTHORIZER)
def list_filesystems():
    """
    Lists all EFS filesystems in the account

    :returns: Object containing filesystems
    :raises ChaliceViewError
    """
    try:
        response = EFS.describe_file_systems()
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


@app.route('/filesystems/{filesystem_id}', methods=['GET'], cors=True, authorizer=AUTHORIZER)
def describe_filesystem(filesystem_id):
    """
    Retrieves details for a specified filesystem

    :param filesystem_id: The filesystem to describe
    :returns: Filesystem details
    :raises ChaliceViewError
    """
    try:
        response = EFS.describe_file_systems(
            FileSystemId=filesystem_id
        )
    except botocore.exceptions.ClientError as error:
        app.log.error(error)
        raise ChaliceViewError("Check API logs")
    else:
        return json.dumps(response, indent=4, sort_keys=True, default=str)


@app.route('/filesystems/{filesystem_id}/netinfo', methods=['GET'], cors=True, \
    authorizer=AUTHORIZER)
def get_netinfo_for_filesystem(filesystem_id):
    """
    Retrieves network info for a specified filesystem

    :param filesystem_id: The filesystem to get net info for
    :returns: Filesystem network info
    :raises ChaliceViewError
    """
    netinfo = []
    try:
        response = EFS.describe_mount_targets(
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
                response = EFS.describe_mount_target_security_groups(
                    MountTargetId=mount_target_id
                )
            except botocore.exceptions.ClientError as error:
                app.log.debug(error)
                raise ChaliceViewError
            else:
                security_groups = response['SecurityGroups']
                vpc_item = {'{id}'.format(id=mount_target_id): {'security_groups': \
                    security_groups, 'subnet_id': target['SubnetId']}}
                netinfo.append(vpc_item)

    return netinfo


@app.route('/filesystems/{filesystem_id}/lambda', methods=['POST'], cors=True, \
    authorizer=AUTHORIZER)
def create_filesystem_lambda(filesystem_id):
    """
    Proxies the filesystem manager creation to the create_manager_stack
    helper function

    :param filesystem_id: The filesystem to create resources for
    :returns: Creation response
    :raises ChaliceViewError, BadRequestError
    """
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


@app.route('/filesystems/{filesystem_id}/lambda', methods=['DELETE'], cors=True, \
    authorizer=AUTHORIZER)
def delete_filesystem_lambda(filesystem_id):
    """
    Proxies the filesystem manager deletion to the delete_manager_stack
    helper function

    :param filesystem_id: The filesystem to delete resources for
    :returns: Deletion response
    :raises ChaliceViewError, BadRequestError
    """
    stack_status = describe_manager_stack(filesystem_id)
    if stack_status['Stacks'][0]['StackStatus'] == 'CREATE_COMPLETE':
        try:
            delete_stack = delete_manager_stack(filesystem_id)
            app.log.info(delete_stack)
        except Exception as error:
            raise ChaliceViewError(error)
    else:
        raise BadRequestError('No valid managed stack for this filesystem')


@app.route('/objects/{filesystem_id}/upload', methods=["POST"], cors=True, authorizer=AUTHORIZER)
def upload(filesystem_id):
    """
    Uploads a file

    :param filesystem_id: The filesystem to perform operation on
    :param path: The path to upload the file
    :param filename: The name of the file
    :returns: Filesystem operation response
    :raises ChaliceViewError, BadRequestError
    """
    print(app.current_request.query_params)
    try:
        path = app.current_request.query_params['path']
        filename = app.current_request.query_params['filename']
    except KeyError as error:
        app.log.error('Missing required query param: {e}'.format(e=error))
        raise BadRequestError('Missing required query param: {e}'.format(e=error))

    request = app.current_request
    chunk_data = request.json_body
    chunk_data["filename"] = filename

    filemanager_event = {"operation": "upload", "path": path, "chunk_data": chunk_data}

    operation_result = proxy_operation_to_efs_lambda(filesystem_id, filemanager_event)
    error_message = "Error uploading file"

    return format_operation_response(operation_result, error_message)


@app.route('/objects/{filesystem_id}/download', methods=["GET"], cors=True, authorizer=AUTHORIZER)
def download(filesystem_id):
    """
    Downloads a file

    :param filesystem_id: The filesystem to perform operation on
    :param path: The path to download the file
    :param filename: The name of the file
    :returns: Filesystem operation response
    :raises ChaliceViewError, BadRequestError
    """
    print(app.current_request.query_params)
    try:
        path = app.current_request.query_params['path']
        filename = app.current_request.query_params['filename']
    except KeyError as error:
        app.log.error('Missing required query param: {e}'.format(e=error))
        raise BadRequestError('Missing required query param: {e}'.format(e=error))
    else:
        if 'dzchunkindex' and 'dzchunkbyteoffset' in app.current_request.query_params:
            chunk_index = app.current_request.query_params['dzchunkindex']
            chunk_offset = app.current_request.query_params['dzchunkbyteoffset']
            filemanager_event = {"operation": "download", "path": path, "filename": filename, \
                                 "chunk_data": {"dzchunkindex": int(chunk_index), \
                                     "dzchunkbyteoffset": int(chunk_offset)}}
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


@app.route('/objects/{filesystem_id}/dir', methods=['POST'], cors=True, authorizer=AUTHORIZER)
def make_dir(filesystem_id):
    """
    Make a directory

    :param filesystem_id: The filesystem to perform operation on
    :param path: The path to create a directory
    :param name: The name of the directory
    :returns: Filesystem operation response
    :raises ChaliceViewError, BadRequestError
    """
    request = app.current_request
    dir_data = request.json_body

    try:
        name = dir_data['name']
        path = dir_data['path']
    except KeyError as error:
        app.log.error('Missing required param: {e}'.format(e=error))
        raise BadRequestError('Missing required param: {e}'.format(e=error))
    else:
        filemanager_event = {"operation": "make_dir", "path": path, "name": name}
        operation_result = proxy_operation_to_efs_lambda(filesystem_id, filemanager_event)
        error_message = "Error creating dir"

        return format_operation_response(operation_result, error_message)


@app.route('/objects/{filesystem_id}', methods=['DELETE'], cors=True, authorizer=AUTHORIZER)
def delete_object(filesystem_id):
    """
    Deletes a file

    :param filesystem_id: The filesystem to perform operation on
    :param path: The path to delete the file
    :param filename: The name of the file
    :returns: Filesystem operation response
    :raises ChaliceViewError, BadRequestError
    """
    try:
        name = app.current_request.query_params['name']
        path = app.current_request.query_params['path']
    except KeyError as error:
        app.log.error('Missing required query param: {e}'.format(e=error))
        raise BadRequestError('Missing required query param: {e}'.format(e=error))
    else:
        filemanager_event = {"operation": "delete", "path": path, "name": name}
        operation_result = proxy_operation_to_efs_lambda(filesystem_id, filemanager_event)
        error_message = "Error deleting file"

        return format_operation_response(operation_result, error_message)


@app.route('/objects/{filesystem_id}', methods=['GET'], cors=True, authorizer=AUTHORIZER)
def list_objects(filesystem_id):
    """
    Lists files in a specifed path

    :param filesystem_id: The filesystem to perform operation on
    :param path: The path to list
    :returns: Filesystem operation response
    :raises ChaliceViewError, BadRequestError
    """
    if app.current_request.query_params['path']:
        path = app.current_request.query_params['path']
    else:
        app.log.error('Missing required query param: path')
        raise BadRequestError('Missing required query param: path')

    filemanager_event = {"operation": "list", "path": path}
    operation_result = proxy_operation_to_efs_lambda(filesystem_id, filemanager_event)
    error_message = "Error listing files"

    return format_operation_response(operation_result, error_message)
