## Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
## SPDX-License-Identifier: Apache-2.0
import base64


def test_delete(manager_lambda, mocker):
    mock_delete = mocker.patch('os.remove', return_value=[])
    test_event = {'operation': 'delete', 'path': './test', 'name': 'tmp.txt'}
    delete_response = manager_lambda.lambda_handler(test_event, None)
    print(delete_response)
    mock_delete.assert_called()

    assert delete_response['statusCode'] == 200

def test_bad_delete(manager_lambda, mocker):
    mock_delete = mocker.patch('os.remove', side_effect=OSError)
    test_event = {'operation': 'delete', 'path': './test', 'name': 'tmp.txt'}
    delete_response = manager_lambda.lambda_handler(test_event, None)
    print(delete_response)
    mock_delete.assert_called()
    assert delete_response['statusCode'] == 500

def test_make_dir(manager_lambda, mocker):
    mock_mkdir = mocker.patch('os.mkdir', return_value=[])
    test_event = {'operation': 'make_dir', 'path': './test', 'name': 'tmp'}
    mkdir_response = manager_lambda.lambda_handler(test_event, None)
    print(mkdir_response)
    mock_mkdir.assert_called()
    assert mkdir_response['statusCode'] == 200

def test_bad_make_dir(manager_lambda, mocker):
    mock_mkdir = mocker.patch('os.mkdir', side_effect=OSError)
    test_event = {'operation': 'make_dir', 'path': './test', 'name': 'tmp'}
    mkdir_response = manager_lambda.lambda_handler(test_event, None)
    print(mkdir_response)
    mock_mkdir.assert_called()
    assert mkdir_response['statusCode'] == 500


def test_upload_file_exists(manager_lambda, mocker):
    chunk_data = base64.b64encode(b'test')
    test_event = {'operation': 'upload', 'path': '/mnt/efs', 'chunk_data': {'dzuuid': '10f726ea-ae1d-4363-9a97-4bf6772cd4df', 'dzchunkindex': '0', 'dzchunksize': '4', 'dztotalchunkcount': '1', 'dzchunkbyteoffset': '0', 'filename': 'test.txt', 'content': chunk_data}}
    mock_path_join = mocker.patch('os.path.join', return_value='/mnt/efs/test.txt')
    mock_path_exists = mocker.patch('os.path.exists', return_value=True)
    upload_response = manager_lambda.lambda_handler(test_event, None)
    print(upload_response)
    mock_path_join.assert_called()
    mock_path_exists.assert_called()
    assert upload_response['statusCode'] == 400

def test_upload_write_error(manager_lambda, mocker):
    chunk_data = base64.b64encode(b'test')
    test_event = {'operation': 'upload', 'path': '/mnt/efs', 'chunk_data': {'dzuuid': '10f726ea-ae1d-4363-9a97-4bf6772cd4df', 'dzchunkindex': '0', 'dzchunksize': '4', 'dztotalchunkcount': '1', 'dzchunkbyteoffset': '0', 'filename': 'test.txt', 'content': chunk_data}}
    mock_path_join = mocker.patch('os.path.join', return_value='/mnt/efs/test.txt')
    mock_path_exists = mocker.patch('os.path.exists', return_value=False)
    mock_file_open = mocker.patch('builtins.open', side_effect=OSError)
    upload_response = manager_lambda.lambda_handler(test_event, None)
    print(upload_response)
    mock_path_join.assert_called()
    mock_path_exists.assert_called()
    mock_file_open.assert_called()

    assert upload_response['statusCode'] == 500


def test_download_read_error_first_call(manager_lambda, mocker):
    test_event = {'operation': 'download', 'path': '/mnt/efs/', 'filename': 'test.txt'}
    mock_path_join = mocker.patch('os.path.join', return_value='/mnt/efs/test.txt')
    mock_path_get_size = mocker.patch('os.path.getsize', return_value=4)
    mock_file_open = mocker.patch('builtins.open', side_effect=OSError)
    download_response = manager_lambda.lambda_handler(test_event, None)
    print(download_response)
    mock_path_join.assert_called()
    mock_path_get_size.assert_called()
    mock_file_open.assert_called()

    assert download_response['statusCode'] == 500

def test_download_read_error_successive_call(manager_lambda, mocker):
    test_event = {'operation': 'download', 'path': '/mnt/efs/', 'filename': 'test.txt', 'chunk_data': {'dzchunkindex': '0', 'dzchunkbyteoffset': '0'}}
    mock_path_join = mocker.patch('os.path.join', return_value='/mnt/efs/test.txt')
    mock_path_get_size = mocker.patch('os.path.getsize', return_value=4)
    mock_file_open = mocker.patch('builtins.open', side_effect=OSError)
    download_response = manager_lambda.lambda_handler(test_event, None)
    print(download_response)
    mock_path_join.assert_called()
    mock_path_get_size.assert_called()
    mock_file_open.assert_called()

    assert download_response['statusCode'] == 500

def test_list_missing_path(manager_lambda, mocker):
    test_event = {'operation': 'list'}
    list_response = manager_lambda.lambda_handler(test_event, None)
    assert list_response['statusCode'] == 400


def test_list_walk_error(manager_lambda, mocker):
    test_event = {'operation': 'list', 'path': '/mnt/efs/'}
    mock_os_walk = mocker.patch('os.walk', side_effect=OSError)
    list_response = manager_lambda.lambda_handler(test_event, None)
    print(list_response)
    mock_os_walk.assert_called()
    assert list_response['statusCode'] == 500

def test_list(manager_lambda, mocker):
    test_event = {'operation': 'list', 'path': '/mnt/efs/'}
    mock_os_walk = mocker.patch('os.walk', return_value=[])
    list_response = manager_lambda.lambda_handler(test_event, None)
    print(list_response)
    mock_os_walk.assert_called()
    assert list_response['statusCode'] == 200

def test_missing_operation(manager_lambda):
    test_event = {}
    response = manager_lambda.lambda_handler(test_event, None)
    assert response['statusCode'] == 400
