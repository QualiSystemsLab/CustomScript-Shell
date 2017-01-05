import json
import os

from cloudshell.core.context.error_handling_context import ErrorHandlingContext
from cloudshell.shell.core.context import ResourceCommandContext
from cloudshell.shell.core.session.cloudshell_session import CloudShellSessionContext
from cloudshell.shell.core.session.logging_session import LoggingSessionContext


class CustomScriptShell(object):

    def __init__(self):
        pass

    def execute_script(self, command_context, script_conf_json):
        """
        :type command_context: ResourceCommandContext
        :type ansi_conf_json: str
        :rtype str
        """
        with LoggingSessionContext(command_context) as logger:
            with ErrorHandlingContext(logger):
                logger.debug('\'execute_script\' is called with the configuration json: \n' + script_conf_json)
                pass

  

class CustomScriptException(Exception):
    pass