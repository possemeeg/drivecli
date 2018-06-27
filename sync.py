"""
Shows basic usage of the Drive v3 API.

Creates a Drive v3 API service and prints the names and ids of the last 10 files
the user has access to.
"""
from __future__ import print_function
from apiclient.discovery import build
from apiclient.http import MediaIoBaseDownload
from httplib2 import Http
from oauth2client import file, client, tools
import io
import re
import contextlib
import os
import pathlib
import filecmp

# Setup the Drive v3 API
#SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly', 'https://www.googleapis.com/auth/drive.file']
SCOPES = 'https://www.googleapis.com/auth/drive'
store = file.Storage('credentials.json')
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets('client_secret.json', SCOPES)
    creds = tools.run_flow(flow, store)
service = build('drive', 'v3', http=creds.authorize(Http()))

def download_file(service, file_id, local_fd):
  """Download a Drive file's content to the local filesystem.

  Args:
    service: Drive API Service instance.
    file_id: ID of the Drive file that will downloaded.
    local_fd: io.Base or file object, the stream that the Drive file's
        contents will be written to.
  """
  request = service.files().get_media(fileId=file_id)
  media_request = MediaIoBaseDownload(local_fd, request)

  while True:
    try:
      download_progress, done = media_request.next_chunk()
    except error:
      print('An error occurred: {}'.format(error))
      return
    if download_progress:
      print('Download Progress: %d%%' % int(download_progress.progress() * 100))
    if done:
      print('Download Complete')
      return

def find_old_files(name):
    regex = '^' + name + '\\.2[0-9]{3}[0-1][0-9][0-3][0-9]$'
    
    for x in [x for x in pathlib.Path('.').iterdir() if x.is_file() and re.match(regex, x.name)]:
        print(x)
        print(filecmp.cmp(x, name))


@contextlib.contextmanager
def pushd(new_dir):
    old_dir = os.getcwd()
    os.chdir(new_dir)
    try:
        yield
    finally:
        os.chdir(old_dir)



def proc_items(items):
    with pushd('download'):
        for item in items:
            proc_item(item)

def proc_item(item):
    print('Downloading {}'.format(item))
    with open(item['name'], 'wb') as f:
        download_file(service, item['id'], f)
    find_old_files(item['name'])


def list_files():
    # Call the Drive v3 API
    page_token = None
    while True:
        results = service.files().list(
                #q="parents contans '1CdgEScQdvcyx1UAnmYGnj4vFvpbC_c9w'",
                q="'1CdgEScQdvcyx1UAnmYGnj4vFvpbC_c9w' in parents and mimeType='text/x-tex'",
                #q="mimeType='application/vnd.google-apps.folder'",
                pageSize=10, fields="nextPageToken, files(id, name, parents, mimeType, modifiedTime)", pageToken=page_token).execute()
        items = results.get('files', [])
        if not items:
            print('no files')
            break
        else:
            proc_items(items);

        
        page_token = results.get('nextPageToken', None)
        if page_token is None:
            break

list_files()
#file_id = '0BwwA4oUTeiV1UVNwOHItT0xfa2M'
#request = service.files().get_media(fileId=file_id)
#fh = io.BytesIO()
#downloader = MediaIoBaseDownload(fh, request)
#done = False
#while done is False:
#    status, done = downloader.next_chunk()
#    print "Download %d%%." % int(status.progress() * 100)

