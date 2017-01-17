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

        repo = json_obj['repositoryDetails']
        script_conf.script_repo.url = repo.get('url')
        script_conf.script_repo.username = repo.get('username')
        script_conf.script_repo.password = repo.get('password')

        host = json_obj['hostsDetails'][0]
        script_conf.host_conf = HostConfiguration()
        script_conf.host_conf.ip = host.get('ip')
        script_conf.host_conf.connection_method = host['connectionMethod'].lower() if host.get('connectionMethod') else None
        script_conf.host_conf.connection_secured = bool_parse(host.get('connectionSecured'))
        script_conf.host_conf.username = host.get('username')
        script_conf.host_conf.password = host.get('password')
        script_conf.host_conf.access_key = host.get('accessKey')
        if host.get('parameters'):
            script_conf.host_conf.parameters = dict((i['name'], i['value']) for i in host['parameters'])

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

        if not json_obj.get('hostsDetails'):
            raise SyntaxError(basic_msg + 'Missing/Empty "hostsDetails" node.')

        if len(json_obj.get('hostsDetails')) > 1:
            raise SyntaxError(basic_msg + 'Node "hostsDetails" must contain only one item.')

        if not json_obj.get('hostsDetails')[0].get('ip'):
            raise SyntaxError(basic_msg + 'Missing/Empty "hostsDetails[0].ip" node.')

        if not json_obj.get('hostsDetails')[0].get('connectionMethod'):
            raise SyntaxError(basic_msg + 'Missing/Empty "hostsDetails[0].connectionMethod" node.')


def bool_parse(b):
    if b is None:
        return None
    else:
        return str(b).lower() == 'true'