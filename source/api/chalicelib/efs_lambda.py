## Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
## SPDX-License-Identifier: Apache-2.0

import os
import base64
import math
# File manager operation events:
# list: {"operation": "list", "path": "$dir"}
# upload: {"operation": "upload", "path": "$dir", "form_data": "$form_data"}


def delete(event):
    print(event)
    path = event['path']
    name = event['name']

    file_path = path + '/' + name

    try:
        os.remove(file_path)
    except OSError:
        return {"message": "couldn't delete the file", "statusCode": 500}
    else:
        return {"message": "file deletion successful", "statusCode": 200}


def make_dir(event):
    print(event)
    path = event['path']
    name = event['name']

    new_dir = path + '/' + name

    try:
        os.mkdir(new_dir)
    except OSError:
        return {"message": "couldn't create the directory", "statusCode": 500}
    else:
        return {"message": "directory creation successful", "statusCode": 200}


def upload(event):
    print(event)
    "{'operation': 'upload', 'path': '/mnt/efs', 'chunk_data': {'dzuuid': '10f726ea-ae1d-4363-9a97-4bf6772cd4df', 'dzchunkindex': '0', 'dzchunksize': '1000000', 'dztotalchunkcount': '1', 'dzchunkbyteoffset': '0', 'filename': 'Log at 2020-08-11 12-17-21 PM.txt', 'content': '(Emitted value instead of an instance of Error)'}}"
    path = event['path']
    filename = event['chunk_data']['filename']
    file_content_decoded = base64.b64decode(event['chunk_data']['content'])
    current_chunk = int(event['chunk_data']['dzchunkindex'])
    save_path = os.path.join(path, filename)

    if os.path.exists(save_path) and current_chunk == 0:
        return {"message": "File already exists", "statusCode": 400}

    try:
        with open(save_path, 'ab') as f:
            f.seek(int(event['chunk_data']['dzchunkbyteoffset']))
            f.write(file_content_decoded)
    except OSError as error:
        print('Could not write to file: {error}'.format(error=error))
        return {"message": "couldn't write the file to disk", "statusCode": 500}

    total_chunks = int(event['chunk_data']['dztotalchunkcount'])

    if current_chunk + 1 == total_chunks:
        if int(os.path.getsize(save_path)) != int(event['chunk_data']['dztotalfilesize']):
            print("File {filename} was completed, but there is a size mismatch. Was {size} but expected {total}".format(filename=filename, size=os.path.getsize(save_path), total=event['chunk_data']['dztotalfilesize']))
            return {"message": "Size mismatch", "statusCode": 500}
        else:
            print("file {filename} has been uploaded successfully".format(filename=filename))
            return {"message": "File uploaded successfuly", "statusCode": 200}
    else:
        print("Chunk {current_chunk} of {total_chunks} for file {filename} complete".format(current_chunk=current_chunk + 1 , total_chunks=total_chunks, filename=filename))
        return {"message": "Chunk upload successful", "statusCode": 200}


def download(event):
    # first call {"path": "./", "filename": "test.txt"}
    # successive calls
    # {"path": "./", "filename": "test_video.mp4", "chunk_data": {'dzchunkindex': chunk['dzchunkindex'],
    # 'dzchunkbyteoffset': chunk['dzchunkbyteoffset']}}
    path = event['path']
    filename = event['filename']
    file_path = os.path.join(path, filename)
    chunk_size = 2000000  # bytes
    file_size = os.path.getsize(file_path)
    chunks = math.ceil(file_size / chunk_size)

    if "chunk_data" in event:
        start_index = event['chunk_data']['dzchunkbyteoffset']
        current_chunk = event['chunk_data']['dzchunkindex']
        try:
            with open(file_path, 'rb') as f:
                f.seek(start_index)
                file_content = f.read(chunk_size)
                encoded_chunk_content = str(base64.b64encode(file_content), 'utf-8')
                chunk_offset = start_index + chunk_size
                chunk_number = current_chunk + 1

                return {"dzchunkindex": chunk_number, "dztotalchunkcount": chunks, "dzchunkbyteoffset": chunk_offset,
                        "chunk_data": encoded_chunk_content, "dztotalfilesize": file_size}
        except OSError as error:
            print('Could not read file: {error}'.format(error=error))
            return {"message": "couldn't read the file from disk", "statusCode": 500}

    else:
        start_index = 0
        try:
            with open(file_path, 'rb') as f:
                f.seek(start_index)
                file_content = f.read(chunk_size)
                encoded_chunk_content = str(base64.b64encode(file_content), 'utf-8')
                chunk_number = 0
                chunk_offset = chunk_size

                return {"dzchunkindex": chunk_number, "dztotalchunkcount": chunks, "dzchunkbyteoffset": chunk_offset,
                        "chunk_data": encoded_chunk_content, "dztotalfilesize": file_size}

        except OSError as error:
            print('Could not read file: {error}'.format(error=error))
            return {"message": "couldn't read the file from disk", "statusCode": 500}


def list(event):
    # get path to list
    try:
        path = event['path']
    except KeyError:
        return {"message": "missing required parameter: path", "statusCode": 400}

    try:
        dir_items = []
        file_items = []
        for (dirpath, dirnames, filenames) in os.walk(path):
            dir_items.extend(dirnames)
            file_items.extend(filenames)
            break
    except Exception as error:
        print(error)
        return {"message": "unable to list files", "statusCode": 500}
    else:
        return {"path": path, "directiories": dir_items, "files": file_items, "statusCode": 200}


def lambda_handler(event, _context):
    # get operation type
    try:
        operation_type = event['operation']
    except KeyError:
        return {"message": "missing required parameter: operation", "statusCode": 400}
    else:
        if operation_type == 'upload':
            upload_result = upload(event)
            return upload_result
        if operation_type == 'list':
            list_result = list(event)
            return list_result
        if operation_type == 'delete':
            delete_result = delete(event)
            return delete_result
        if operation_type == 'make_dir':
            make_dir_result = make_dir(event)
            return make_dir_result
        if operation_type == 'download':
            download_result = download(event)
            return download_result
