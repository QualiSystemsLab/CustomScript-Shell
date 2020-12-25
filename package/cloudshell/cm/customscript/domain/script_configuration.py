import json
import numbers

# WILL OVERRIDE THE DEFAULTS
REPO_URL_PARAM = "REPO_RAW_URL"
REPO_USER_PARAM = "GH_REPO_USER"
REPO_PASSWORD_PARAM = "GH_REPO_PASSWORD"

# GITLAB PARAMS
GL_SERVER_PARAM = "GL_SERVER"
GL_SCRIPT_PATH_PARAM = "GL_SCRIPT_PATH"
GL_TOKEN_PARAM = "GL_TOKEN"
GL_PROJECT_ID_PARAM = "GL_PROJECT_ID"
GL_BRANCH_PARAM = "GL_BRANCH"
GL_SSL_PARAM = "GL_SSL"

CONNECTION_METHOD_PARAM = "CONNECTION_METHOD"


class ScriptConfiguration(object):
    def __init__(self, script_repo=None, host_conf=None, timeout_minutes=None, print_output=True, gitlab_details=None):
        """
        :type script_repo: ScriptRepository
        :type host_conf: HostConfiguration
        :type timeout_minutes: float
        :type print_output: bool
        :type gitlab_details: GitLabRepoDetails
        """
        self.timeout_minutes = timeout_minutes or 0.0
        self.script_repo = script_repo or ScriptRepository()
        self.host_conf = host_conf or HostConfiguration()
        self.print_output = print_output
        self.gitlab_details = gitlab_details or GitLabRepoDetails()


class ScriptRepository(object):
    def __init__(self):
        self.url = None
        self.username = None
        self.password = None


class HostConfiguration(object):
    def __init__(self):
        self.ip = None
        self.connection_method = None
        self.connection_secured = None
        self.username = None
        self.password = None
        self.access_key = None
        self.parameters = {}


class GitLabRepoDetails(object):
    def __init__(self):
        self.server = None
        self.script_path = None
        self.access_token = None
        self.project_id = None
        self.script_branch = "master"
        self.is_ssl = False


def append_gitlab_details(script_conf, params_dict):
    """
    go over custom params and over-ride values
    :param ScriptConfiguration script_conf:
    :param dict params_dict:
    :return same config:
    :rtype ScriptConfiguration
    """
    gitlab_details = script_conf.gitlab_details

    if params_dict.get(GL_SERVER_PARAM):
        gitlab_details.server = params_dict[GL_SERVER_PARAM]

    if params_dict.get(GL_SCRIPT_PATH_PARAM):
        gitlab_details.script_path = params_dict[GL_SCRIPT_PATH_PARAM]

    if params_dict.get(GL_PROJECT_ID_PARAM):
        gitlab_details.project_id = params_dict[GL_PROJECT_ID_PARAM]

    if params_dict.get(GL_TOKEN_PARAM):
        gitlab_details.access_token = params_dict[GL_TOKEN_PARAM]
    else:
        gitlab_details.access_token = script_conf.script_repo.password

    if params_dict.get(GL_SSL_PARAM).lower() == "true":
        gitlab_details.is_ssl = True

    if params_dict.get(GL_BRANCH_PARAM):
        gitlab_details.script_branch = params_dict[GL_BRANCH_PARAM].lower()

    # VALIDATE DETAILS
    if gitlab_details.server:
        required_details = [
            (GL_SERVER_PARAM, gitlab_details.server),
            (GL_SCRIPT_PATH_PARAM, gitlab_details.script_path),
            (GL_PROJECT_ID_PARAM, gitlab_details.project_id),
            (GL_TOKEN_PARAM, gitlab_details.access_token)
        ]
        missing_details = [x[0] for x in required_details if not x[1]]
        if missing_details:
            raise Exception("Missing Gitlab Param Details: {}".format(missing_details))

    return script_conf


def over_ride_defaults(script_conf, params_dict):
    """
    go over custom params and over-ride values
    :param ScriptConfiguration script_conf:
    :param dict params_dict:
    :return same config:
    :rtype ScriptConfiguration
    """
    if params_dict.get(REPO_URL_PARAM):
        script_conf.script_repo.url = params_dict[REPO_URL_PARAM]

    if params_dict.get(REPO_USER_PARAM):
        script_conf.script_repo.username = params_dict[REPO_USER_PARAM]

    if params_dict.get(REPO_PASSWORD_PARAM):
        script_conf.script_repo.password = params_dict[REPO_PASSWORD_PARAM]

    if params_dict.get(CONNECTION_METHOD_PARAM):
        script_conf.host_conf.connection_method = params_dict[CONNECTION_METHOD_PARAM].lower()

    return script_conf


class ScriptConfigurationParser(object):

    def __init__(self, api):
        """
        :type api: CloudShellAPISession
        """
        self.api = api

    def json_to_object(self, json_str):
        """
        Decodes a json string to an ScriptConfigurationParser instance.
        :type json_str: str
        :rtype ScriptConfiguration
        """
        json_obj = json.loads(json_str)
        ScriptConfigurationParser._validate(json_obj)

        script_conf = ScriptConfiguration()
        script_conf.timeout_minutes = json_obj.get('timeoutMinutes', 0.0)
        script_conf.print_output = bool_parse(json_obj.get('printOutput', True))

        repo = json_obj['repositoryDetails']
        script_conf.script_repo.url = repo.get('url')
        script_conf.script_repo.username = repo.get('username')
        script_conf.script_repo.password = repo.get('password')

        host = json_obj['hostsDetails'][0]
        script_conf.host_conf = HostConfiguration()
        script_conf.host_conf.ip = host.get('ip')
        script_conf.host_conf.connection_method = host['connectionMethod'].lower()
        script_conf.host_conf.connection_secured = bool_parse(host.get('connectionSecured'))
        script_conf.host_conf.username = host.get('username')
        script_conf.host_conf.password = self._get_password(host)
        script_conf.host_conf.access_key = self._get_access_key(host)
        if host.get('parameters'):
            all_params_dict = dict((i['name'], i['value']) for i in host['parameters'])
            script_conf.host_conf.parameters = all_params_dict
            script_conf = over_ride_defaults(script_conf, all_params_dict)

        return script_conf

    def _get_password(self, json_host):
        pw = json_host.get('password')
        if pw:
            return self.api.DecryptPassword(pw).Value
        else:
            return pw

    def _get_access_key(self, json_host):
        key = json_host.get('accessKey')
        if key:
            return self.api.DecryptPassword(key).Value
        else:
            return key

    @staticmethod
    def _validate(json_obj):
        """
        :type json_obj: dict
        :rtype bool
        """
        basic_msg = 'Failed to parse script configuration input json: '

        if json_obj.get('timeoutMinutes'):

            if not isinstance(json_obj.get('timeoutMinutes'), numbers.Number):
                raise SyntaxError(basic_msg + 'Node "timeoutMinutes" must be numeric type.')

            if json_obj.get('timeoutMinutes') < 0:
                raise SyntaxError(basic_msg + 'Node "timeoutMinutes" must be greater/equal to zero.')

        if json_obj.get('repositoryDetails') is None:
            raise SyntaxError(basic_msg + 'Missing "repositoryDetails" node.')

        if not json_obj.get('repositoryDetails').get('url'):
            raise SyntaxError(basic_msg + 'Missing/Empty "repositoryDetails.url" node.')

        if not json_obj.get('hostsDetails'):
            raise SyntaxError(basic_msg + 'Missing/Empty "hostsDetails" node.')

        if len(json_obj.get('hostsDetails')) > 1:
            raise SyntaxError(basic_msg + 'Node "hostsDetails" must contain only one item.')

        if not json_obj.get('hostsDetails')[0].get('ip'):
            raise SyntaxError(basic_msg + 'Missing/Empty "hostsDetails[0].ip" node.')

        if not json_obj.get('hostsDetails')[0].get('connectionMethod'):
            raise SyntaxError(basic_msg + 'Missing/Empty "hostsDetails[0].connectionMethod" node.')

        if json_obj.get('hostsDetails')[0].get('ip') == "NA":
            raise ValueError(basic_msg + 'HostDetails IP is NA, will not be able to connect.')


def bool_parse(b):
    if b is None:
        return None
    else:
        return str(b).lower() == 'true'
