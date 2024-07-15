import os
import sys
import flask
from flask import Flask, flash, request, redirect, render_template
from apiclient.http import MediaIoBaseDownload, MediaFileUpload
import httplib2
from apiclient import discovery
from oauth2client import client
from oauth2client.file import Storage
import uuid

#set app and define template folder where html templates are stored
app = flask.Flask(__name__ , template_folder='templates')

#set file path after uploading file
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# define file upload folder
UPLOAD_FOLDER = 'files'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'



def get_credentials():
    credential_path = 'credentials.json'

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        print("Credentials not found.")
        return False
    else:
        print("Credentials fetched successfully.")
        return credentials

# fetch files from google drive
def fetch(query, sort='modifiedTime desc'):
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('drive', 'v3', http=http)
    result = service.files().list(q=query, orderBy=sort, pageSize=10, fields="nextPageToken, files(id, name)").execute()
    items = result.get('files', [])
    return items




@app.route('/', methods=['GET', 'POST'])
def index():

    # if there is problem with credentials, redirect to oauth2callback  function
    credentials = get_credentials()
    if credentials == False:
        return flask.redirect(flask.url_for('oauth2callback'))
    elif credentials.access_token_expired:
        return flask.redirect(flask.url_for('oauth2callback'))
    else:
        print('calling fetch')

        #fetch documents, files and folders from google drive and sort them according to modified time
        all_files = fetch("'root' in parents and (mimeType = 'application/vnd.google-apps.document' or"
                          " mimeType='application/vnd.google-apps.file' or"
                          " mimeType='application/vnd.google-apps.folder') ",sort='modifiedTime desc')
        s = []
        for file in all_files:
            s.append(file['name'])

        return render_template('interface.html',data=s,len=len(s))

#redirect uri
@app.route('/oauth2callback')
def oauth2callback():
    # access drive api using developer credentials
    client_flow = client.flow_from_clientsecrets('client_id.json',scope='https://www.googleapis.com/auth/drive',
                                                 redirect_uri=flask.url_for('oauth2callback',_external=True))
    client_flow.params['include_granted_scopes'] = 'true'
    if 'code' not in flask.request.args:
        authuri = client_flow.step1_get_authorize_url()
        return flask.redirect(authuri)
    else:
        authcode = flask.request.args.get('code')
        credentials = client_flow.step2_exchange(authcode)

        # write access token to credentials.json locally
        open('credentials.json', 'w').write(credentials.to_json())
        return flask.redirect(flask.url_for('index'))


# upload file to google drive
@app.route('/uploads', methods=['GET', 'POST'])
def upload():
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('drive', 'v3', http=http)

    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:

            print('no file part')
            return redirect(request.url)
        file = request.files['file']

        # if user does not select file, browser also submit a empty part without filename
        if file.filename == '':

            print('no selected file')
            return redirect(request.url)
        if file:
            filename = file.filename
            print(filename)

            #set write access to upload folder
            os.chmod(UPLOAD_FOLDER, 0o777)
            os.access('files', os.W_OK)  # Check for write access
            os.access('files', os.R_OK)

            #save file in upload folder
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            #get file path
            filepath=os.path.join(app.config['UPLOAD_FOLDER'], filename)

            #set file meta data
            file_metadata = {'name': filename}

            #set upload file mime type
            media = MediaFileUpload(filepath, mimetype='image/png')
            file = service.files().create(body=file_metadata,media_body=media,fields='id').execute()
            print ('File ID: %s' % file.get('id'))

    return render_template('success.html')




if __name__ == '__main__':
    if os.path.exists('client_id.json') == False:
        print('client_id.json not found in the app path. Download json file and save it in the file path')
        exit()

    app.secret_key = str(uuid.uuid4())
    app.run(debug=True)