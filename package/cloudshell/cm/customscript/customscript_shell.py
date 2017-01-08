import json
import os

from cloudshell.core.context.error_handling_context import ErrorHandlingContext
from cloudshell.shell.core.context import ResourceCommandContext
from cloudshell.shell.core.session.cloudshell_session import CloudShellSessionContext
from cloudshell.shell.core.session.logging_session import LoggingSessionContext

from cloudshell.cm.customscript.domain.script_configuration import ScriptConfigurationParser, ScriptConfiguration
from cloudshell.cm.customscript.domain.script_downloader import ScriptDownloader, HttpAuth
from cloudshell.cm.customscript.domain.script_executor import ReservationOutputWriter


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
                script_conf = ScriptConfigurationParser.json_to_object(script_conf_json)

                repo = script_conf.script_repo
                auth = HttpAuth(repo.username, repo.password) if repo.username else None
                script_file = ScriptDownloader(logger).download(repo.url, auth)

                service = None

                self.logger.info('Creating temp folder on target machine.')
                tmp_folder = service.create_temp_folder()
                self.logger.info('Done.')

                try:
                    self.logger.info('Copying script to target machine.')
                    service.copy_script(tmp_folder, script_file)
                    self.logger.info('Done.')

                    self.logger.info('Running script on target machine.')
                    with CloudShellSessionContext(command_context) as session:
                        output_writer = ReservationOutputWriter(session, command_context)
                        service.run_script(tmp_folder, script_file.name, output_writer)
                    self.logger.info('Done.')

                finally:
                    self.logger.info('Deleting temp folder from target machine.')
                    service.delete_temp_folder(tmp_folder)
                    self.logger.info('Done.')


class CustomScriptException(Exception):
    pass