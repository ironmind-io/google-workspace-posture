from google_workspace_posture.services.service import Service
from google_workspace_posture.config import config
from googleapiclient.discovery import build
from google.oauth2 import service_account
import json
import os   
import logging


class AdminDirectoryOU(Service):
    SCOPES = [
        'https://www.googleapis.com/auth/admin.directory.orgunit.readonly',
    ]
    
    def setup(self):
        try:
            c = config['google'] 
            k = json.loads(c['api_key'])
            credentials = service_account.Credentials\
                    .from_service_account_info(
                        k, scopes=self.SCOPES)
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

        if not hasattr(self, 'service'):
            self.setup()
    
        customer_id = config['google']['customer_id']

        request = self.service.orgunits().list(
            customerId=customer_id, type='all')

        while request is not None:
            response = request.execute()                                    
            for ou in response.get('organizationUnits', []):                
                yield ou
            
            # Check if there's a nextPageToken provided in the response
            page_token = response.get('nextPageToken')
            if page_token:
                request = self.service.orgunits()\
                        .list(customerId=customer_id, type='all', 
                                pageToken=page_token)
            else:
                request = None

        #dirty hack to get the root OU
        root_ou = self.service.orgunits().get(
            customerId=customer_id, orgUnitPath='/').execute()
        parent_ou =  root_ou.get('organizationUnits', [])
        if parent_ou:
            yield {"orgUnitPath": parent_ou[0]['parentOrgUnitPath'],
                    "orgUnitId": parent_ou[0]['parentOrgUnitId']}





