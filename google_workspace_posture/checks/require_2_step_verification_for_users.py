from google_workspace_posture.check import Check, CheckPriority,\
        CheckStatus, CheckResult



def get_users(service, customer_id):
    request = service.users().list(customer=customer_id, projection='full',
            maxResults=100)
    while request is not None:
        response = request.execute()
        for user in response.get('users', []):
            yield user
        request = service.users().list_next(request, response)
    


class require_2_step_verification_for_users(Check):
    '''
    This check identifies users who are not enrolled in 2SV.
    It lists users who are not enrolled.  It does NOT report the status
    of 2SV enforcement as this is not available via the API.
    '''

    check_id = "require_2_step_verification_for_users"
    check_name = "Require 2-Step Verification for Users"
    check_description = '''
        Require 2-Step Verification for Users.  
        2-Step Verification (a.k.a. 2FA, MFA) is one of the best ways
        to protect your account.  It requires a second verification step
        in addition to your password.  This check will identify users
        who are not enrolled in 2-Step Verification.
        Enforce 2SV as described here:
        https://support.google.com/a/answer/9176657
        '''
    check_priority = CheckPriority.CRITICAL

    
    def __init__(self, config):
        #check that service and customer_id are in the config
        if 'service' not in config:
            raise ValueError('service is required')
        if 'customer_id' not in config:
            raise ValueError('customer_id is required')

        self.config = config
        self.customer_id = config['customer_id']
        self.service = config['service']
        

    def check(self):
        missing_2sv = []
        for user in get_users(self.service, self.customer_id):
            if 'isEnrolledIn2Sv' not in user:
                missing_2sv.append(user['primaryEmail'])

        if len(missing_2sv) > 0:
            return CheckResult(
                    check_id = self.check_id,
                    check_result = CheckStatus.FAIL,
                    check_message = \
                        'These user are not enrolled in 2SV: {}'.format(
                        ', '.join(missing_2sv)))
        else:
            return CheckResult(
                    check_id = self.check_id,
                    check_result = CheckStatus.PASS,
                    check_message = 'All users are enrolled in 2SV')


        

    



