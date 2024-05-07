from google_workspace_posture.services.service import Service
from google_workspace_posture.config import config
from googleapiclient.discovery import build
from google.oauth2 import service_account
import json
import os   
import logging


class AdminDirectoryUsers(Service):

    SCOPES = [
        'https://www.googleapis.com/auth/admin.directory.user.readonly',
        'https://www.googleapis.com/auth/admin.directory.userschema.readonly',
    ]
    
    def setup(self):
        try:
            c = config['google']
            key = json.loads(c['api_key'])
            credentials = service_account.Credentials\
                    .from_service_account_info(
                        key, scopes=self.SCOPES)
            delegated_creds = credentials.with_subject(
                    c['admin_email'])
            service = build('admin', 'directory_v1',
                    credentials=delegated_creds)
            self.service = service
        except Exception as e:
            logging.error(e)
            msg = '''
            Error loading AdminDirectory service.
            Likely causes:
                - API scopes are not correct
                - env vars incorrect or missing:
                    - GOOGLE_CUSTOMER_ID
                    - GOOGLE_ADMIN_EMAIL
                    - GOOGLE_API_KEY
            '''

            raise Exception(msg, "\n\n", e)


    def teardown(self):
        return True


    def load_data(self):

        if not self.service:
            self.setup()

        customer_id = config['google']['customer_id']
        request = self.service.users().list(customer=customer_id,
                projection='full', maxResults=100)
        while request is not None:
            response = request.execute()
            for user in response.get('users', []):
                yield user
            request = self.service.users().list_next(request, response)


