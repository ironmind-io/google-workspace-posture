from google_workspace_posture.check import Check, CheckPriority,\
        CheckStatus, CheckResult
from google_workspace_posture.services.admin_reports import AdminReports
from google_workspace_posture.services.admin_directory import AdminDirectory



class enforce_security_keys_for_admins(Check):
    '''
    This check identifies users who are not enrolled in 2SV.
    It lists users who are not enrolled.  It does NOT report the status
    of 2SV enforcement as this is not available via the API.
    '''

    id = "enforce_security_keys_for_admins"
    name = "Enforce Security Keys for Admins"
    description = '''
    This check identifies admin users who are not enrolled
    in 2SV using security keys. This places them at increased risk 
    of account compromise as security keys are resistant to 
    many phishing attacks.
    https://support.google.com/accounts/answer/6103523
    '''
    priority = CheckPriority.HIGH

    def check(self):
        params = 'accounts:is_super_admin,accounts:is_delegated_admin,accounts:num_security_keys'
        admins_missing_keys = []
        with AdminReports() as adm_rpt:
            data = adm_rpt.load_data(params)
            for i in data:
                report_data = i.get('parameters', [{}])
                is_admin = (report_data[0].get('boolValue', False)
                            or
                            report_data[1].get('boolValue', False))
                        
                has_keys = int(report_data[2].get('intValue', 0)) > 0
                if  is_admin and not has_keys:
                    admins_missing_keys.append(i['entity']['userEmail'])

        if len(admins_missing_keys) > 0:
            return CheckResult(
                id=self.id,
                result=CheckStatus.FAIL,
                message=f'{len(admins_missing_keys)} admin users are missing security keys: {", ".join(admins_missing_keys)}'
            )
        return CheckResult(
            id=self.id,
            result=CheckStatus.PASS,
            message='All admin users have security keys'   
        )


class require_2_step_verification_for_users(Check):
    '''
    This check identifies users who are not enrolled in 2SV.
    It lists users who are not enrolled.  It does NOT report the status
    of 2SV enforcement as this is not available via the API.
    '''

    id = "require_2_step_verification_for_users"
    name = "Require 2-Step Verification for Users"
    description = '''
        Require 2-Step Verification for Users.  
        2-Step Verification (a.k.a. 2FA, MFA) is one of the best ways
        to protect your account.  It requires a second verification step
        in addition to your password.  This check will identify users
        where the isEnforcedIn2Sv is False.
        Enforce 2SV as described here:
        https://support.google.com/a/answer/9176657
        '''
    priority = CheckPriority.CRITICAL

    def check(self):

        not_enforced_2sv = []
        not_enrolled_2sv = []
        with AdminDirectory() as dir_service:
            for u in dir_service.load_data():   
                if 'isEnforcedIn2Sv' in u and not u['isEnforcedIn2Sv']:
                    not_enforced_2sv.append(u['primaryEmail'])
                if 'isEnrolledIn2Sv' in u and not u['isEnrolledIn2Sv']:
                    not_enrolled_2sv.append(u['primaryEmail'])



        if len(not_enforced_2sv) > 0 and len(not_enrolled_2sv) == 0:
            #partial pass as some users are not enforced
            #but all users are enrolled

            msg = f'''
            2SV is not enforced for these users:
            {', '.join(not_enforced_2sv)}
            However, all users are enrolled in 2SV.
            '''
            return CheckResult(
                    id = self.id,
                    result = CheckStatus.PARTIAL_PASS,
                    message = \
                        'These users are not enforced in 2SV: {}'.format(
                        ', '.join(not_enforced_2sv)))


        if len(not_enrolled_2sv) > 0:
            return CheckResult(
                    id = self.id,
                    result = CheckStatus.FAIL,
                    message = \
                        'These user are not enrolled in 2SV: {}'.format(
                        ', '.join(not_enrolled_2sv)))
        else:
            return CheckResult(
                    id = self.id,
                    result = CheckStatus.PASS,
                    message = 'All users are enrolled in 2SV')


        


