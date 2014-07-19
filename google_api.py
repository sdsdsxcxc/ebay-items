import logging

import httplib2
import io
from os.path import join, dirname, abspath

from googleapiclient import http as api_http
from googleapiclient import errors as api_errors
from googleapiclient.discovery import build
from oauth2client.client import SignedJwtAssertionCredentials
from oauth2client.appengine import CredentialsNDBModel
from oauth2client.appengine import StorageByKeyName
from ConfigParser import ConfigParser
import settings


class GoogleAPI(object):
    """
        Base class for working with Google API
    """
    def __init__(self):
        self.read_settings()

    def get_credentials(self, api_type, **params):
        storage_ndb = StorageByKeyName(
            CredentialsNDBModel, api_type, 'credentials')

        credentials = storage_ndb.get()
        if credentials is None:
            # self.read_settings()
            with open(join(dirname(abspath(__file__)), self.ApiSettings["private_key_file"])) as f:
                private_key = f.read()

            credentials = SignedJwtAssertionCredentials(
                self.ApiSettings["service_account_name"],
                private_key,
                # sub=self.ApiSettings["google_account_owner_email"],  # before commenting this line,
                # I got "AccessTokenRefreshError: unauthorized_client" error
                **params
            )

            storage_ndb.put(credentials)
        return credentials

    def read_settings(self):
        self.ApiSettings = {}
        CONFIG_STORE = ConfigParser()
        CONFIG_STORE.read(join(dirname(abspath(__file__)), settings.GOOGLE_API_SETTINGS_FILE))
        self.ApiSettings["google_storage_bucket"] = CONFIG_STORE.get("keys", "google_storage_bucket")
        self.ApiSettings["private_key_file"] = CONFIG_STORE.get("keys", "private_key_file")
        self.ApiSettings["service_account_name"] = CONFIG_STORE.get("keys", "service_account_name")


class GoogleCloudStorageAPI(GoogleAPI):
    def __init__(self):
        super(GoogleCloudStorageAPI, self).__init__()
        if self.ApiSettings:
            self.bucket = self.ApiSettings["google_storage_bucket"]
            self.create_service()
            self.json_get_list()

    def create_service(self):
        params = {
            'scope': ['https://www.googleapis.com/auth/devstorage.full_control',
                      'https://www.googleapis.com/auth/devstorage.read_only',
                      'https://www.googleapis.com/auth/devstorage.read_write'],
            # 'developerKey': self.ApiSettings.public_key,
        }
        api_type = 'storage'
        credentials = self.get_credentials(api_type, **params)

        http = httplib2.Http()
        # without this option, test will not work, but in GAE environment - you must uncomment it
        if settings.TESTING:
            http.disable_ssl_certificate_validation = True
        self.http = credentials.authorize(http)

        self.service = build("storage", "v1beta2", http=self.http)

    def json_get_list(self):
        nextPageToken = None
        self.items = {}
        while True:
            resp = self.service.objects().list(bucket=self.bucket,
                                               maxResults=100,
                                               fields='items(name,updated),nextPageToken',
                                               pageToken=nextPageToken).execute()

            # if bucket is clean
            if resp == {}:
                break
            [self.items.update({item["name"]: item["updated"]}) for item in resp["items"]]
            nextPageToken = resp.get("nextPageToken", None)
            if nextPageToken is None:
                break
        if len(self.items) >= 0:
            # logging.info(self.items_list)
            logging.info(str(len(self.items)) + " files on Storage")
            return True
        else:
            return False

    def json_upload(self, filename, content, content_type='image/jpeg'):
        media = api_http.MediaIoBaseUpload(io.BytesIO(content), content_type)
        req = self.service.objects().insert(bucket=self.bucket,
                                            name=filename,
                                            media_body=media)
        repeat = 5  # repeat several times only when we get 503 "Backend Error"
        while repeat:
            try:
                resp = req.execute()
            except api_errors.HttpError as e:
                logging.info(str(e))
                if "Backend Error" in str(e):
                    repeat -= 1
                    logging.info("backend" + str(repeat))
                else:
                    logging.info("other")
                    raise e
            else:
                logging.info(resp)
                return resp

    def json_read(self, filename):
        # Get Payload Data
        req = self.service.objects().get_media(bucket=self.bucket,
                                               object=filename)
        fh = io.BytesIO()
        downloader = api_http.MediaIoBaseDownload(fh, req, chunksize=1024*1024)
        done = False
        while not done:
            status, done = downloader.next_chunk()
        return fh.getvalue()

    def json_delete(self, filename):
        try:
            resp = self.service.objects().delete(bucket=self.bucket,
                                                 object=filename).execute()
        except api_errors.HttpError as e:
            logging.error(e)
            resp = False

        return resp
