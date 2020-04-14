import json
import numbers

from cloudshell.cm.customscript.domain.script_configuration import HostConfiguration, bool_parse


class CommandConfiguration(object):
    def __init__(self, command_info=None, host_conf=None, timeout_minutes=None):
        """
        :type command_info: CommandInfo
        :type host_conf: HostConfiguration
        :type timeout_minutes: float
        :type print_output: bool
        """
        self.timeout_minutes = timeout_minutes or 0.0
        self.command_info = command_info or CommandInfo()
        self.host_conf = host_conf or HostConfiguration()
        self.print_output = False


class CommandInfo(object):
    def __init__(self):
        self.cmd = None


class CommandConfigurationParser(object):

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
        CommandConfigurationParser._validate(json_obj)

        script_conf = CommandConfiguration()
        script_conf.timeout_minutes = json_obj.get('timeoutMinutes', 0.0)

        cmd_info = json_obj['commandInfo']
        script_conf.command_info.cmd = cmd_info['cmd']

        host = json_obj['hostsDetails'][0]
        script_conf.host_conf = HostConfiguration()
        script_conf.host_conf.ip = host.get('ip')
        script_conf.host_conf.connection_method = host['connectionMethod'].lower()
        script_conf.host_conf.connection_secured = bool_parse(host.get('connectionSecured'))
        script_conf.host_conf.username = host.get('username')
        script_conf.host_conf.password = host.get('password')
        script_conf.host_conf.access_key = host.get('accessKey')

        return script_conf

    @staticmethod
    def _validate(json_obj):
        """
        :type json_obj: json
        :rtype bool
        """
        basic_msg = 'Failed to parse script configuration input json: '

        if json_obj.get('timeoutMinutes'):

            if not isinstance(json_obj.get('timeoutMinutes'), numbers.Number):
                raise SyntaxError(basic_msg + 'Node "timeoutMinutes" must be numeric type.')

            if json_obj.get('timeoutMinutes') < 0:
                raise SyntaxError(basic_msg + 'Node "timeoutMinutes" must be greater/equal to zero.')

        if json_obj.get('commandInfo') is None:
            raise SyntaxError(basic_msg + 'Missing "commandInfo" node.')

        if not json_obj.get('commandInfo').get('cmd'):
            raise SyntaxError(basic_msg + 'Missing/Empty "commandInfo.cmd" node.')

        if not json_obj.get('hostsDetails'):
            raise SyntaxError(basic_msg + 'Missing/Empty "hostsDetails" node.')

        if len(json_obj.get('hostsDetails')) > 1:
            raise SyntaxError(basic_msg + 'Node "hostsDetails" must contain only one item.')

        if not json_obj.get('hostsDetails')[0].get('ip'):
            raise SyntaxError(basic_msg + 'Missing/Empty "hostsDetails[0].ip" node.')

        if not json_obj.get('hostsDetails')[0].get('connectionMethod'):
            raise SyntaxError(basic_msg + 'Missing/Empty "hostsDetails[0].connectionMethod" node.')