import json
import os

from cloudshell.core.context.error_handling_context import ErrorHandlingContext
from cloudshell.shell.core.context import ResourceCommandContext
from cloudshell.shell.core.session.cloudshell_session import CloudShellSessionContext
from cloudshell.shell.core.session.logging_session import LoggingSessionContext

from cloudshell.cm.customscript.domain.reservation_output_writer import ReservationOutputWriter
from cloudshell.cm.customscript.domain.script_configuration import ScriptConfigurationParser, ScriptRepository, \
    HostConfiguration
from cloudshell.cm.customscript.domain.script_downloader import ScriptDownloader, HttpAuth
from cloudshell.cm.customscript.domain.script_executor import IScriptExecutor
from cloudshell.cm.customscript.domain.script_executor_selector import ScriptExecutorSelector
from cloudshell.cm.customscript.domain.script_file import ScriptFile


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

                logger.info('Downloading file from \'%s\' ...' % script_conf.script_repo.url)
                script_file = self._download_script(script_conf.script_repo, logger)
                logger.info('Done (%s, %s chars).' % (script_file.name, len(script_file.text)))

                service = ScriptExecutorSelector.get(script_conf.host_conf, logger)

                logger.info('Creating temp folder on target machine ...')
                tmp_folder = service.create_temp_folder()
                logger.info('Done (%s).' % tmp_folder)

                try:
                    logger.info('Copying "%s" (% chars) to "%s" target machine ...'%(script_file.name,len(script_file.text), tmp_folder))
                    service.copy_script(tmp_folder, script_file)
                    logger.info('Done.')

                    logger.info('Running "%s" on target machine ...' % script_file.name)
                    with CloudShellSessionContext(command_context) as session:
                        output_writer = ReservationOutputWriter(session, command_context)
                        service.run_script(tmp_folder, script_file, script_conf.host_conf.parameters, output_writer)
                    logger.info('Done.')

                finally:
                    logger.info('Deleting "%s" folder from target machine ...' % tmp_folder)
                    service.delete_temp_folder(tmp_folder)
                    logger.info('Done.')

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



# conf = '''{
# 	"repositoryDetails": {
# 		"url": "http://192.168.30.108:8081/artifactory/LinuxScripts/ls.sh"
# 	},
# 	"hostDetails": {
# 		"ip": "192.168.85.20",
# 		"username": "root",
# 		"password": "qs1234",
# 		"connectionMethod": "ssh"
# 	}
# }'''
# context = ResourceCommandContext()
# context.resource = ResourceContextDetails()
# context.resource.name = 'TEST Resource'
# context.reservation = ReservationContextDetails()
# context.reservation.reservation_id = '8cc5bc1a-ae62-43c6-8772-3cd2bde5dbd8'
#
# shell = CustomScriptShell()
#
# shell.execute_script(context, conf)