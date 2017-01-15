import json
import os

from cloudshell.core.context.error_handling_context import ErrorHandlingContext
from cloudshell.shell.core.context import ResourceCommandContext
from cloudshell.shell.core.session.cloudshell_session import CloudShellSessionContext
from cloudshell.shell.core.session.logging_session import LoggingSessionContext

from cloudshell.cm.customscript.domain.linux_script_executor import LinuxScriptExecutor
from cloudshell.cm.customscript.domain.script_configuration import ScriptConfigurationParser, ScriptRepository, \
    HostConfiguration
from cloudshell.cm.customscript.domain.script_downloader import ScriptDownloader, HttpAuth
from cloudshell.cm.customscript.domain.script_executor import ReservationOutputWriter, IScriptExecutor
from cloudshell.cm.customscript.domain.script_file import ScriptFile
from cloudshell.cm.customscript.domain.windows_script_executor import WindowsScriptExecutor


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

                script_file = self._download_script(script_conf.script_repo, logger)

                service = self._create_script_executor(script_conf.host_conf, logger)

                logger.info('Creating temp folder on target machine.')
                tmp_folder = service.create_temp_folder()
                logger.info('Done.')

                try:
                    logger.info('Copying script to target machine.')
                    service.copy_script(tmp_folder, script_file)
                    logger.info('Done.')

                    logger.info('Running script on target machine.')
                    with CloudShellSessionContext(command_context) as session:
                        output_writer = ReservationOutputWriter(session, command_context)
                        service.run_script(tmp_folder, script_file.name, output_writer)
                    logger.info('Done.')

                finally:
                    logger.info('Deleting temp folder from target machine.')
                    service.delete_temp_folder(tmp_folder)
                    logger.info('Done.')

    @staticmethod
    def _download_script(self, script_repo, logger):
        """
        :type script_repo: ScriptRepository
        :type logger: Logger
        :rtype ScriptFile
        """
        url = script_repo.url
        auth = None
        if script_repo.username:
            auth = HttpAuth(script_repo.username, script_repo.password)
        return ScriptDownloader(logger).download(url, auth)

    @staticmethod
    def _create_script_executor(self, host_conf, logger):
        """
        :type host_conf: HostConfiguration
        :type logger: Logger
        :rtype IScriptExecutor
        """
        if host_conf.connection_method == 'ssh':
            return LinuxScriptExecutor(logger, host_conf)
        else:
            return WindowsScriptExecutor(logger, host_conf)