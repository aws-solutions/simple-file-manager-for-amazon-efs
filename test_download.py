import os
import base64
import requests


# my_event = {"path": "./", "filename": "test_video.mp4", "form_data": {'dzchunkindex': chunk['dzchunkindex'],
# 'dzchunkbyteoffset': chunk['dzchunkbyteoffset']}}


#
# my_event = {"path": "./", "filename": "test.txt"}
#
# while True:
#     chunk = download(my_event)
#     if chunk['dzchunkindex'] == chunk["dztotalchunkcount"]:
#         break
#     form_data = {'dzchunkindex': chunk['dzchunkindex'], 'dzchunkbyteoffset': chunk['dzchunkbyteoffset']}
#     upload_event = {'path': './', 'form_data': {"dztotalfilesize": chunk["dztotalfilesize"],
#     'dzchunkindex': chunk['dzchunkindex'], 'dzchunkbyteoffset': chunk['dzchunkbyteoffset'],
#     'dztotalchunkcount': chunk["dztotalchunkcount"], 'filename': 'test_text_uploaded.txt',
#     'content': chunk["chunk_data"]}}
#     try:
#         print('uploading')
#         upload_response = upload(upload_event)
#         my_event["form_data"] = form_data
#     except Exception as e:
#         print('failed')
#         #print(e)
#         break



def write_chunk(event):
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
            print("file {filename} has been written successfully".format(filename=filename))
            return {"message": "File written successfuly", "statusCode": 200}
    else:
        print("Chunk {current_chunk} of {total_chunks} for file {filename} complete".format(current_chunk=current_chunk + 1 , total_chunks=total_chunks, filename=filename))
        return {"message": "Chunk write successful", "statusCode": 200}


def main():
    api = "https://i076sdxd27.execute-api.us-west-2.amazonaws.com/api/"
    download_uri = api + "download/fs-b44095b1"
    local_path = "./"

    remote_path = input("What is the file path?")
    filename = input("What is the file name?")

    file_params = "?path=" + remote_path + "&filename=" + filename

    def download_chunk(url):
        print(url)
        r = requests.get(url)
        return r.json()

    def download_file(chunk_data):
        if not chunk_data:
            request_url = download_uri + file_params
        else:
            download_query_params = "&dzchunkindex=" + str(chunk_data[0]) + "&dzchunkbyteoffset=" + str(chunk_data[1])
            request_url = download_uri + file_params + download_query_params

        chunk = download_chunk(request_url)

        if chunk['dzchunkindex'] == chunk["dztotalchunkcount"]:
            print('Done')
        else:
            write_event = {'path': local_path, 'form_data': {"dztotalfilesize": chunk["dztotalfilesize"],
                                                             'dzchunkindex': chunk['dzchunkindex'],
                                                             'dzchunkbyteoffset': chunk['dzchunkbyteoffset'],
                                                             'dztotalchunkcount': chunk["dztotalchunkcount"],
                                                             'filename': filename,
                                                             'content': chunk["chunk_data"]}}
            try:
                write_chunk(write_event)
            except Exception as e:
                print(e)
            else:
                chunk_index = chunk['dzchunkindex']
                chunk_offset = chunk['dzchunkbyteoffset']
                chunk_data = [chunk_index, chunk_offset]
                download_file(chunk_data)

    download_file([])


main()
