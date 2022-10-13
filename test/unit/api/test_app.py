import json
import botocore.stub

from service_responses import EFS, CFN, LAMBDA, EC2

test_filesystem_id = 'fs-01234567'


##############################

# POSITIVE TEST CASES

##############################

def test_list_filesystems(test_client, efs_client_stub, cfn_client_stub):
    print('GET /filesystems')

    efs_client_stub.add_response(
        'describe_file_systems',
        expected_params={'MaxItems': 10},
        service_response=EFS['describe_file_systems_no_marker']
    )

    cfn_client_stub.add_response(
        'describe_stacks',
        expected_params={'StackName': f'testStackPrefix-ManagedResources-{test_filesystem_id}'},
        service_response=CFN['describe_stacks']
    )
    response = test_client.http.get('/filesystems')

    formatted_response = json.loads(response.body)
    
    print(formatted_response)

    expected_response_keys = ['filesystems']

    assert all(item in formatted_response.keys() for item in expected_response_keys)
    
    filesystems = formatted_response['filesystems']

    assert isinstance(filesystems, list)
    assert filesystems[0]['name'] == 'MyFileSystem'
    assert filesystems[0]['managed'] is True
    assert filesystems[0]['file_system_id'] == f'{test_filesystem_id}'

    print('PASS')


def test_list_filesystems_paginated(test_client, efs_client_stub, cfn_client_stub):
    print('GET /filesystems')

    efs_client_stub.add_response(
        'describe_file_systems',
        expected_params={'MaxItems': 10, 'Marker': 'xyz'},
        service_response=EFS['describe_file_systems_marker']
    )

    cfn_client_stub.add_response(
        'describe_stacks',
        expected_params={'StackName': f'testStackPrefix-ManagedResources-{test_filesystem_id}'},
        service_response=CFN['describe_stacks']
    )
    response = test_client.http.get('/filesystems?cursor=xyz')

    formatted_response = json.loads(response.body)
    
    print(formatted_response)

    expected_response_keys = ['filesystems']

    assert all(item in formatted_response.keys() for item in expected_response_keys)
    
    filesystems = formatted_response['filesystems']

    assert isinstance(filesystems, list)
    assert filesystems[0]['name'] == 'MyFileSystem'
    assert filesystems[0]['managed'] is True
    assert filesystems[0]['file_system_id'] == f'{test_filesystem_id}'

    print('PASS')


def test_get_netinfo_for_filesystem(test_client, efs_client_stub, ec2_client_stub):
    print(f'GET /filesystems/{test_filesystem_id}/netinfo')

    efs_client_stub.add_response(
        'describe_mount_targets',
        expected_params={'FileSystemId': f'{test_filesystem_id}'},
        service_response=EFS['describe_mount_targets']
    )

    efs_client_stub.add_response(
        'describe_mount_target_security_groups',
        expected_params={'MountTargetId': 'fsmt-12340abc'},
        service_response=EFS['describe_mount_target_security_groups']
    )

    ec2_client_stub.add_response(
        'describe_security_group_rules',
        expected_params={'Filters': [{'Name': 'group-id', 'Values': ['sg-4567abcd']}]},
        service_response=EC2['describe_sec_rules']
    )

    response = test_client.http.get(f'/filesystems/{test_filesystem_id}/netinfo')

    formatted_response = json.loads(response.body)
    
    print(formatted_response)

    assert formatted_response == [{'fsmt-12340abc': {'security_groups': ['sg-4567abcd'], 'subnet_id': 'subnet-1234abcd'}}]

    print('PASS')

def test_create_filesystem_lambda(test_client, cfn_client_stub):
    print(f'POST /filesystems/{test_filesystem_id}/lambda')

    cfn_client_stub.add_response(
        'create_stack',
        service_response=CFN['create_stack']
    )

    response = test_client.http.post(f'/filesystems/{test_filesystem_id}/lambda', body=json.dumps({'subnetIds': ['subnet-1234abcd'], 'securityGroups': ['sg-4567abcd'], 'gid': '1000', 'uid': '1000', 'path': '/efs'}),
    headers={'Content-Type':'application/json'})

    formatted_response = json.loads(response.body)
    
    print(formatted_response)

    expected_response_keys = ['StackId']

    assert all(item in formatted_response.keys() for item in expected_response_keys)

    assert formatted_response['StackId'] == 'testStackPrefix-ManagedResources-fs-01234567'

    print('PASS')

def test_delete_filesystem_lambda(test_client, cfn_client_stub):
    print(f'DELETE /filesystems/{test_filesystem_id}/lambda')

    cfn_client_stub.add_response(
        'describe_stacks',
        expected_params={'StackName': f'testStackPrefix-ManagedResources-{test_filesystem_id}'},
        service_response=CFN['describe_stacks']
    )

    cfn_client_stub.add_response(
        'delete_stack',
        service_response={}
    )

    response = test_client.http.delete(f'/filesystems/{test_filesystem_id}/lambda')

    formatted_response = json.loads(response.body)

    print(formatted_response)

    assert formatted_response is None

    print('PASS')

def test_upload(test_client, lambda_client_stub):
    
    test_upload_payload = json.dumps({
        'dzchunkindex': 0,
        'dztotalfilesize': 4,
        'dztotalchunkcount': 1,
        'dzchunkbyteoffset': 0,
        'content': 'test'
    })
    
    lambda_client_stub.add_response(
        'invoke',
        expected_params={
            'InvocationType': 'RequestResponse',
            'FunctionName': 'fs-01234567-manager-lambda',
            'Payload': botocore.stub.ANY
        },
        service_response=LAMBDA['upload']
    )

    response = test_client.http.post(f'/objects/{test_filesystem_id}/upload?filename=test.txt&path=/mnt/efs/', body=test_upload_payload, headers={'Content-Type':'application/json'})
    
    formatted_response = json.loads(response.body)

    print(formatted_response)

    expected_response_keys = ['message', 'statusCode']

    assert all(item in formatted_response.keys() for item in expected_response_keys)

    status_code = formatted_response['statusCode']

    assert status_code == 200

    print('PASS')

def test_download(test_client, lambda_client_stub):
    lambda_client_stub.add_response(
        'invoke',
        expected_params={
            'InvocationType': 'RequestResponse',
            'FunctionName': 'fs-01234567-manager-lambda',
            'Payload': botocore.stub.ANY
        },
        service_response=LAMBDA['download']
    )

    response = test_client.http.get(f'/objects/{test_filesystem_id}/download?filename=test.txt&path=/mnt/efs/')

    formatted_response = json.loads(response.body)

    print(formatted_response)

    expected_response_keys = ['dzchunkindex', 'dztotalchunkcount', 'dzchunkbyteoffset', 'chunk_data', 'dztotalfilesize']

    assert all(item in formatted_response.keys() for item in expected_response_keys)

    print('PASS')

def test_make_dir(test_client, lambda_client_stub):
    lambda_client_stub.add_response(
        'invoke',
        expected_params={
            'InvocationType': 'RequestResponse',
            'FunctionName': 'fs-01234567-manager-lambda',
            'Payload': botocore.stub.ANY
        },
        service_response=LAMBDA['make_dir']
    )

    dir_data = {'name': 'test', 'path': '/mnt/efs'}

    response = test_client.http.post(f'/objects/{test_filesystem_id}/dir', body=json.dumps(dir_data), headers={'Content-Type':'application/json'})

    formatted_response = json.loads(response.body)

    print(formatted_response)

    expected_response_keys = ['statusCode', 'message']

    assert all(item in formatted_response.keys() for item in expected_response_keys)

    status_code = formatted_response['statusCode']

    assert status_code == 200

    print('PASS')

def test_delete(test_client, lambda_client_stub):
    lambda_client_stub.add_response(
        'invoke',
        expected_params={
            'InvocationType': 'RequestResponse',
            'FunctionName': 'fs-01234567-manager-lambda',
            'Payload': botocore.stub.ANY
        },
        service_response=LAMBDA['delete']
    )

    response = test_client.http.delete(f'/objects/{test_filesystem_id}?name=test.txt&path=/mnt/efs/')

    formatted_response = json.loads(response.body)

    print(formatted_response)

    expected_response_keys = ['message', 'statusCode']

    assert all(item in formatted_response.keys() for item in expected_response_keys)

    status_code = formatted_response['statusCode']

    assert status_code == 200

    print('PASS')

def test_list(test_client, lambda_client_stub):
    lambda_client_stub.add_response(
        'invoke',
        expected_params={
            'InvocationType': 'RequestResponse',
            'FunctionName': 'fs-01234567-manager-lambda',
            'Payload': botocore.stub.ANY
        },
        service_response=LAMBDA['list']
    )

    response = test_client.http.get(f'/objects/{test_filesystem_id}?path=/mnt/efs/')

    formatted_response = json.loads(response.body)

    print(formatted_response)

    expected_response_keys = ['statusCode', 'files', 'directories', 'path']

    assert all(item in formatted_response.keys() for item in expected_response_keys)

    status_code = formatted_response['statusCode']

    assert status_code == 200

    print('PASS')

##############################

# NEGATIVE TEST CASES

##############################

def test_bad_input_create_filesystem_lambda(test_client):
    response = test_client.http.post(f'/filesystems/{test_filesystem_id}/lambda', body=json.dumps({'subnetIds': ['subnet-1234abcd'], 'gid': '1000', 'uid': '1000', 'path': '/efs'}),
    headers={'Content-Type':'application/json'})

    formatted_response = json.loads(response.body)

    print(formatted_response)

    expected_response_keys = ['Code', 'Message']

    assert all(item in formatted_response.keys() for item in expected_response_keys)

    status_code = formatted_response['Code']

    assert status_code == 'BadRequestError'

def test_no_managed_stack_delete_filesystem_lambda(test_client, cfn_client_stub):
    cfn_client_stub.add_client_error(
        'describe_stacks',
        expected_params={'StackName': f'testStackPrefix-ManagedResources-{test_filesystem_id}'},
        service_error_code='ValidationError'
    )

    response = test_client.http.delete(f'/filesystems/{test_filesystem_id}/lambda')

    formatted_response = json.loads(response.body)

    print(formatted_response)

    expected_response_keys = ['Code', 'Message']

    assert all(item in formatted_response.keys() for item in expected_response_keys)

    status_code = formatted_response['Code']

    assert status_code == 'BadRequestError'

    print('PASS')

def test_bad_input_upload(test_client):
    response = test_client.http.post(f'/objects/{test_filesystem_id}/upload?filename=test.txt')

    formatted_response = json.loads(response.body)

    print(formatted_response)

    expected_response_keys = ['Code', 'Message']

    assert all(item in formatted_response.keys() for item in expected_response_keys)

    status_code = formatted_response['Code']

    assert status_code == 'BadRequestError'

    print('PASS')

def test_bad_input_download(test_client):
    response = test_client.http.get(f'/objects/{test_filesystem_id}/download?filename=test.txt')

    formatted_response = json.loads(response.body)

    print(formatted_response)

    expected_response_keys = ['Code', 'Message']

    assert all(item in formatted_response.keys() for item in expected_response_keys)

    status_code = formatted_response['Code']

    assert status_code == 'BadRequestError'

    print('PASS')

def test_bad_input_make_dir(test_client):
    dir_data = {'path': '/mnt/efs'}
    
    response = test_client.http.post(f'/objects/{test_filesystem_id}/dir', body=json.dumps(dir_data), headers={'Content-Type':'application/json'})

    formatted_response = json.loads(response.body)

    print(formatted_response)

    expected_response_keys = ['Code', 'Message']

    assert all(item in formatted_response.keys() for item in expected_response_keys)

    status_code = formatted_response['Code']

    assert status_code == 'BadRequestError'

    print('PASS')

def test_bad_input_delete(test_client):
    response = test_client.http.delete(f'/objects/{test_filesystem_id}?path=/mnt/efs/')

    formatted_response = json.loads(response.body)

    print(formatted_response)

    expected_response_keys = ['Code', 'Message']

    assert all(item in formatted_response.keys() for item in expected_response_keys)

    status_code = formatted_response['Code']

    assert status_code == 'BadRequestError'

    print('PASS')

def test_bad_input_list(test_client):
    response = test_client.http.get(f'/objects/{test_filesystem_id}?p=test')

    formatted_response = json.loads(response.body)

    print(formatted_response)

    expected_response_keys = ['Code', 'Message']

    assert all(item in formatted_response.keys() for item in expected_response_keys)

    status_code = formatted_response['Code']

    assert status_code == 'BadRequestError'

    print('PASS')

def test_efs_error_get_netinfo_for_filesystem(test_client, efs_client_stub):
    efs_client_stub.add_client_error(
        'describe_mount_targets',
        expected_params={'FileSystemId': f'{test_filesystem_id}'},
        service_error_code='BadRequest'
    )

    response = test_client.http.get(f'/filesystems/{test_filesystem_id}/netinfo')

    formatted_response = json.loads(response.body)

    print(formatted_response)

    expected_response_keys = ['Code', 'Message']

    assert all(item in formatted_response.keys() for item in expected_response_keys)

    status_code = formatted_response['Code']

    assert status_code == 'ChaliceViewError'

    print('PASS')


def test_efs_error_describe_filesystem(test_client, efs_client_stub):
    efs_client_stub.add_client_error(
        'describe_file_systems',
        expected_params={'FileSystemId': f'{test_filesystem_id}'},
        service_error_code='BadRequest'
    )

    response = test_client.http.get(f'/filesystems/{test_filesystem_id}')

    formatted_response = json.loads(response.body)

    print(formatted_response)

    expected_response_keys = ['Code', 'Message']

    assert all(item in formatted_response.keys() for item in expected_response_keys)

    status_code = formatted_response['Code']

    assert status_code == 'ChaliceViewError'

    print('PASS')