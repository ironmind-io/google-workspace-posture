from google_workspace_posture.services.service import Service, ServiceError
from google_workspace_posture.config import config
from googleapiclient.discovery import build
from google.oauth2 import service_account
import json
import os   
import logging
import datetime


class AdminReports(Service):

    SCOPES = ['https://www.googleapis.com/auth/admin.reports.usage.readonly']
    
    def setup(self):
        try:
            cfg = config['google']
            service_account_info = json.loads(cfg['api_key']) 
            credentials = service_account.Credentials\
                    .from_service_account_info(
                        service_account_info, scopes=self.SCOPES)
            delegated_creds = credentials.with_subject(
                cfg['admin_email'])
            service = build('admin', 'reports_v1',
                    credentials=delegated_creds)
            self.reports_service = service
        except Exception as e:
            logging.error(e)
            msg = '''
            Error loading AdminReports service.
            Likely causes:
                - API scopes are not correct
                - env vars incorrect or missing:
                    - GOOGLE_CUSTOMER_ID
                    - GOOGLE_ADMIN_EMAIL
                    - GOOGLE_API_KEY
            '''

            raise ServiceError(msg)

    def teardown(self):
        return True

    def load_data(self, report_params, report_date = None):

        if report_date==None:
            report_date = datetime.datetime.now() - datetime.timedelta(days=7)

        results = self.reports_service.userUsageReport().get(
            userKey='all', 
            date=report_date.strftime('%Y-%m-%d'),
            parameters=report_params
        ).execute()

        data = results.get('usageReports', [])
        for i in data:
            yield i


