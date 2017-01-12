import json


class ScriptConfiguration(object):
    def __init__(self, script_repo = None, host_conf = None):
        """
        :type script_repo: ScriptRepository
        :type host_conf: HostConfiguration
        """
        self.script_repo = script_repo or ScriptRepository()
        self.host_conf = host_conf or HostConfiguration()


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


class ScriptConfigurationParser(object):
    @staticmethod
    def json_to_object(json_str):
        """
        Decodes a json string to an ScriptConfigurationParser instance.
        :type json_str: str
        :rtype ScriptConfiguration
        """
        json_obj = json.loads(json_str)
        ScriptConfigurationParser._validate(json_obj)

        script_conf = ScriptConfiguration()
        if json_obj.get('repositoryDetails'):
            script_conf.script_repo.url = json_obj['repositoryDetails'].get('url')
            script_conf.script_repo.username = json_obj['repositoryDetails'].get('username')
            script_conf.script_repo.password = json_obj['repositoryDetails'].get('password')
        if json_obj.get('hostDetails'):
            script_conf.host_conf = HostConfiguration()
            script_conf.host_conf.ip = json_obj['hostDetails'].get('ip')
            script_conf.host_conf.connection_method = json_obj['hostDetails'].get('connectionMethod')
            script_conf.host_conf.connection_secured = bool_parse(json_obj['hostDetails'].get('connectionSecured'))
            script_conf.host_conf.username = json_obj['hostDetails'].get('username')
            script_conf.host_conf.password = json_obj['hostDetails'].get('password')
            script_conf.host_conf.access_key = json_obj['hostDetails'].get('accessKey')
            if json_obj['hostDetails'].get('parameters'):
                script_conf.host_conf.parameters = dict((i['name'], i['value']) for i in json_obj['hostDetails']['parameters'])

        return script_conf

    @staticmethod
    def _validate(json_obj):
        """
        :type json_obj: json
        :rtype bool
        """
        basic_msg = 'Failed to parse script configuration input json: '

        if json_obj.get('repositoryDetails') is None:
            raise SyntaxError(basic_msg + 'Missing "repositoryDetails" node.')

        if not json_obj.get('repositoryDetails').get('url'):
            raise SyntaxError(basic_msg + 'Missing/Empty "repositoryDetails.url" node.')

        if not json_obj.get('hostDetails'):
            raise SyntaxError(basic_msg + 'Missing/Empty "hostDetails" node.')

        if not json_obj.get('hostDetails').get('ip'):
            raise SyntaxError(basic_msg + 'Missing/Empty "hostDetails.ip" node.')

        if not json_obj.get('hostDetails').get('connectionMethod'):
            raise SyntaxError(basic_msg + 'Missing/Empty "hostDetails.connectionMethod" node.')


def bool_parse(b):
    if b is None:
        return None
    else:
        return str(b).lower() == 'true'