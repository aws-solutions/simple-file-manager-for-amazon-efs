import os
from os import walk
import base64
# File manager operation events:
# list: {"operation": "list", "path": "$dir"}
# upload: {"operation": "upload", "path": "$dir", "form_data": "$form_data"}


def modify(event):
    return None


def delete(event):
    return None


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
    "{'operation': 'upload', 'path': '/mnt/efs', 'form_data': {'dzuuid': '10f726ea-ae1d-4363-9a97-4bf6772cd4df', 'dzchunkindex': '0', 'dzchunksize': '1000000', 'dztotalchunkcount': '1', 'dzchunkbyteoffset': '0', 'filename': 'Log at 2020-08-11 12-17-21 PM.txt', 'content': '(Emitted value instead of an instance of Error)'}}"
    path = event['path']
    filename = event['form_data']['filename']
    file_content_decoded = base64.b64decode(event['form_data']['content'])
    current_chunk = int(event['form_data']['dzchunkindex'])
    save_path = os.path.join(path, filename)

    if os.path.exists(save_path) and current_chunk == 0:
        return {"message": "File already exists", "statusCode": 400}

    try:
        with open(save_path, 'ab') as f:
            f.seek(int(event['form_data']['dzchunkbyteoffset']))
            f.write(file_content_decoded)
    except OSError as error:
        print('Could not write to file: {error}'.format(error=error))
        return {"message": "couldn't write the file to disk", "statusCode": 500}

    total_chunks = int(event['form_data']['dztotalchunkcount'])

    if current_chunk + 1 == total_chunks:
        if int(os.path.getsize(save_path)) != int(event['form_data']['dztotalfilesize']):
            print("File {filename} was completed, but there is a size mismatch. Was {size} but expected {total}".format(filename=filename, size=os.path.getsize(save_path), total=event['form_data']['dztotalfilesize']))
            return {"message": "Size mismatch", "statusCode": 500}
        else:
            print("file {filename} has been uploaded successfully".format(filename=filename))
            return {"message": "File uploaded successfuly", "statusCode": 200}
    else:
        print("Chunk {current_chunk} of {total_chunks} for file {filename} complete".format(current_chunk=current_chunk + 1 , total_chunks=total_chunks, filename=filename))
        return {"message": "Chunk upload successful", "statusCode": 200}



def list(event):
    # get path to list
    try:
        path = event['path']
    except KeyError:
        raise Exception('Missing required parameter in event: "path"')

    try:
        # TODO: Mucchhhh better thinking around listing directories
        dir_items = []
        file_items = []
        for (dirpath, dirnames, filenames) in walk(path):
            dir_items.extend(dirnames)
            file_items.extend(filenames)
            break
    # TODO: narrower exception scope and proper debug output
    except Exception as error:
        print(error)
        raise Exception(error)
    else:
        return {"path": path, "directiories": dir_items, "files": file_items, "statusCode": 200}


def lambda_handler(event, context):
    # get operation type
    try:
        operation_type = event['operation']
    except KeyError:
        raise Exception('Missing required parameter in event: "operation"')
    else:
        if operation_type == 'upload':
            upload_result = upload(event)
            return upload_result
        if operation_type == 'list':
            list_result = list(event)
            return list_result
        if operation_type == 'modify':
            modify(event)
        if operation_type == 'delete':
            delete(event)
        if operation_type == 'make_dir':
            make_dir_result = make_dir(event)
            return make_dir_result
