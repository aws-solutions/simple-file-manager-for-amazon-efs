## Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
## SPDX-License-Identifier: Apache-2.0
"""API for Simple File Manager for Amazon EFS"""
import os
import logging
import ipaddress
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
MANAGER_STACK_PREFIX = '{prefix}-ManagedResources-'.format(prefix=STACK_PREFIX)

DEFAULT_ERROR_MESSAGE = 'Check API logs for more information'

DEFAULT_MISSING_PARAMS_ERROR_MESSAGE = 'Missing required query param: {e}'

# Cognito resources
# From cloudformation stack

AUTHORIZER = IAMAuthorizer()

# AWS Clients

EFS = boto3.client('efs', config=CONFIG)
SERVERLESS = boto3.client('lambda', config=CONFIG)
CFN = boto3.client('cloudformation', config=CONFIG)
EC2 = boto3.client('ec2', config=CONFIG)


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
    elif stack_status['Stacks'][0]['StackStatus'] == 'UPDATE_IN_PROGRESS':
        new_filesystem_object["managed"] = "Updating"
    elif stack_status['Stacks'][0]['StackStatus'] in ['CREATE_COMPLETE', 'UPDATE_COMPLETE', 'UPDATE_ROLLBACK_COMPLETE']:
        new_filesystem_object["managed"] = True

    new_filesystem_object["file_system_id"] = filesystem_id
    new_filesystem_object["lifecycle_state"] = lifecycle_state

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
    stack_name = MANAGER_STACK_PREFIX + filesystem_id

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
    
    return response


def delete_manager_stack(filesystem_id):
    """
    Deletes a file manager managed resources stack

    :param filesystem_id: The id of the filesystem to delete
    :returns: Deletion status
    :raises ChaliceViewError
    """
    stack_name = MANAGER_STACK_PREFIX + filesystem_id

    try:
        response = CFN.delete_stack(
            StackName=stack_name,
        )
    except botocore.exceptions.ClientError as error:
        app.log.error(error)
        raise ChaliceViewError(error)
    
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
    stack_name = MANAGER_STACK_PREFIX + filesystem_id

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

def check_rule_ports(rule):
    if rule['IpProtocol'] == '-1' or rule['IpProtocol'] == 'tcp':
            if rule['FromPort'] and rule['ToPort'] == 2049 or rule['FromPort'] and rule['ToPort'] == -1:
                return True
            elif rule['FromPort'] <= 2049 <= rule['ToPort']:
                return True
            else:
                return False
    
    return False

def check_ipv4_rule(rule, mount_target_ip):
    subnet = rule['CidrIpv4']
    if ipaddress.ip_address(mount_target_ip) in ipaddress.ip_network(subnet):
        valid_port_access = check_rule_ports(rule)
        return valid_port_access
    
    return False

def check_sg_rule(rule):
    ref_group_id = rule['ReferencedGroupInfo']['GroupId']
    if ref_group_id == rule['GroupId']:
        valid_port_access = check_rule_ports(rule)
        
        return valid_port_access
    
    return False

def test_nfs_access(group, mount_target_ip):
    rules = EC2.describe_security_group_rules(
        Filters=[
                {
                    'Name': 'group-id',
                    'Values': [group]
                }
            ]
        )

    contains_valid_rule = False

    for rule in rules['SecurityGroupRules']:
        if contains_valid_rule:
            break
        else:
            # check if rule is inbound
            if rule['IsEgress'] is False:
                if 'ReferencedGroupInfo' in rule:
                    # references a sg in the rule
                    contains_valid_rule = check_sg_rule(rule)
                if 'CidrIpv4' in rule:
                    # references an ipv4 subnet
                    contains_valid_rule = check_ipv4_rule(rule, mount_target_ip)

    return contains_valid_rule

# Routes

@app.route('/filesystems', methods=["GET"], cors=True, authorizer=AUTHORIZER)
def list_filesystems():
    """
    Lists all EFS filesystems in the account

    :returns: Object containing filesystems
    :raises ChaliceViewError
    """
    

    query_params = app.current_request.query_params

    cursor = None

    if query_params is not None:
        try:
            cursor = query_params['cursor']
        except KeyError:
            pass
    
    try:
        if cursor:
            response = EFS.describe_file_systems(
                MaxItems=10,
                Marker=cursor
            )
        else:
            response = EFS.describe_file_systems(
                MaxItems=10
            )
    except botocore.exceptions.ClientError as error:
        app.log.error(error)
        raise ChaliceViewError(DEFAULT_ERROR_MESSAGE)

    filesystems = response['FileSystems']
    formatted_filesystems = []
    for filesystem in filesystems:
        try:
            formatted = format_filesystem_response(filesystem)
        except botocore.exceptions.ClientError as error:
            app.log.error(error)
            raise ChaliceViewError(DEFAULT_ERROR_MESSAGE)

        formatted_filesystems.append(formatted)
    
    if 'NextMarker' in response:
        pagination_token = response['NextMarker']
        return {"filesystems": formatted_filesystems, "paginationToken": pagination_token}

    return {"filesystems": formatted_filesystems}


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
        raise ChaliceViewError(DEFAULT_ERROR_MESSAGE)

    return json.dumps(response, indent=4, sort_keys=True, default=str)


@app.route('/filesystems/{filesystem_id}/netinfo', methods=['GET'], cors=True, \
    authorizer=AUTHORIZER)
def get_netinfo_for_filesystem(filesystem_id):
    """
    Retrieves mount target network info for a specified filesystem

    :param filesystem_id: The filesystem to get net info for
    :returns: Filesystem mount target network info
    :raises ChaliceViewError
    """
    mount_target_info = []
    try:
        response = EFS.describe_mount_targets(
            FileSystemId=filesystem_id
        )
    except botocore.exceptions.ClientError as error:
        app.log.debug(error)
        raise ChaliceViewError
    mount_targets = response['MountTargets']
    app.log.debug(mount_targets)
    for target in mount_targets:
        mount_target_id = target['MountTargetId']
        mount_target_ip = target['IpAddress']

        try:
            response = EFS.describe_mount_target_security_groups(
                MountTargetId=mount_target_id
            )
        except botocore.exceptions.ClientError as error:
            app.log.debug(error)
            raise ChaliceViewError
        
        security_groups = response['SecurityGroups']
        
        # test security groups to see if the mount target can be used
        valid_security_groups = []
        for group in security_groups:
            is_valid_group = test_nfs_access(group, mount_target_ip)
            if is_valid_group:
                valid_security_groups.append(group)
        
        mount_target_item = {'{id}'.format(id=mount_target_id): {'security_groups': \
            valid_security_groups, 'subnet_id': target['SubnetId']}}
        
        mount_target_info.append(mount_target_item)
    
    if len(mount_target_info) == 0:
        raise BadRequestError('No mount target available with required network configuration. See the deployment guide for configuration details.')

    return mount_target_info


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
        raise BadRequestError(DEFAULT_ERROR_MESSAGE)

    try:
        response = create_manager_stack(filesystem_id, uid, gid, path, subnet_ids, security_groups)
    except Exception as error:
        app.log.error(error)
        app.log.debug('Failed to create stack, deleting it.')
        raise ChaliceViewError('Check API Logs')

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
    if stack_status['Stacks'][0]['StackStatus'] in ['CREATE_COMPLETE', 'UPDATE_COMPLETE', 'UPDATE_ROLLBACK_COMPLETE']:
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
        app.log.error(DEFAULT_MISSING_PARAMS_ERROR_MESSAGE.format(e=error))
        raise BadRequestError(DEFAULT_MISSING_PARAMS_ERROR_MESSAGE.format(e=error))

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
    app.log.debug(app.current_request.query_params)

    query_params = app.current_request.query_params

    try:
        path = query_params['path']
        filename = query_params['filename']
    except KeyError as error:
        app.log.error(DEFAULT_MISSING_PARAMS_ERROR_MESSAGE.format(e=error))
        raise BadRequestError(DEFAULT_MISSING_PARAMS_ERROR_MESSAGE.format(e=error))

    try:
        chunk_index = query_params['dzchunkindex']
        chunk_offset = query_params['dzchunkbyteoffset']
    except KeyError:
        filemanager_event = {"operation": "download", "path": path, "filename": filename}
        operation_result = proxy_operation_to_efs_lambda(filesystem_id, filemanager_event)
        payload_encoded = operation_result['Payload']
        payload = json.loads(payload_encoded.read().decode("utf-8"))
        return payload

    filemanager_event = {"operation": "download", "path": path, "filename": filename, \
                            "chunk_data": {"dzchunkindex": int(chunk_index), \
                                "dzchunkbyteoffset": int(chunk_offset)}}
    operation_result = proxy_operation_to_efs_lambda(filesystem_id, filemanager_event)
    payload_encoded = operation_result['Payload']
    payload = json.loads(payload_encoded.read().decode("utf-8"))
    
    return payload


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
        app.log.error(DEFAULT_MISSING_PARAMS_ERROR_MESSAGE.format(e=error))
        raise BadRequestError(DEFAULT_MISSING_PARAMS_ERROR_MESSAGE.format(e=error))
    
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
    try:
        path = app.current_request.query_params['path']
    except KeyError as error:
        app.log.error(DEFAULT_MISSING_PARAMS_ERROR_MESSAGE.format(e=error))
        raise BadRequestError(DEFAULT_MISSING_PARAMS_ERROR_MESSAGE.format(e=error))

    filemanager_event = {"operation": "list", "path": path}
    operation_result = proxy_operation_to_efs_lambda(filesystem_id, filemanager_event)
    error_message = "Error listing files"

    return format_operation_response(operation_result, error_message)
