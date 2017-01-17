from unittest import TestCase

from mock import patch, Mock

from cloudshell.cm.customscript.customscript_shell import CustomScriptShell
from cloudshell.cm.customscript.domain.reservation_output_writer import ReservationOutputWriter
from cloudshell.cm.customscript.domain.script_configuration import ScriptConfiguration
from cloudshell.cm.customscript.domain.script_file import ScriptFile
from tests.helpers import Any


class TestCustomScriptShell(TestCase):

    def setUp(self):
        self.context = Mock()
        self.executor = Mock()
        self.script_conf = ScriptConfiguration()
        self.logger_patcher = patch('cloudshell.cm.customscript.customscript_shell.LoggingSessionContext')
        self.logger_patcher.start()
        self.error_patcher = patch('cloudshell.cm.customscript.customscript_shell.ErrorHandlingContext')
        self.error_patcher.start()
        self.api_patcher = patch('cloudshell.cm.customscript.customscript_shell.CloudShellSessionContext')
        self.api_patcher.start()
        self.parser_patcher = patch('cloudshell.cm.customscript.customscript_shell.ScriptConfigurationParser.json_to_object')
        self.parser_patcher.start().return_value = self.script_conf
        self.downloader_patcher = patch('cloudshell.cm.customscript.customscript_shell.ScriptDownloader.download')
        self.downloader = self.downloader_patcher.start()
        self.selector_patcher = patch('cloudshell.cm.customscript.customscript_shell.ScriptExecutorSelector.get')
        self.selector_get = self.selector_patcher.start()
        self.selector_get.return_value = self.executor

    def tearDown(self):
        self.logger_patcher.stop()
        self.error_patcher.stop()
        self.api_patcher.stop()
        self.parser_patcher.stop()
        self.downloader_patcher.stop()
        self.selector_patcher.stop()

    def test_download_script_without_auth(self):
        self.script_conf.script_repo.url = 'some url'

        CustomScriptShell().execute_script(self.context, '')

        self.downloader.assert_called_with('some url', None)

    def test_download_script_with_auth(self):
        self.script_conf.script_repo.url = 'some url'
        self.script_conf.script_repo.username = 'admin'
        self.script_conf.script_repo.password = '1234'

        CustomScriptShell().execute_script(self.context, '')

        self.downloader.assert_called_with('some url', Any(lambda x: x.username == 'admin' and x.password=='1234'))

    def test_selector_is_called_with_host_details(self):
        CustomScriptShell().execute_script(self.context, '')

        self.selector_get.assert_called_with(self.script_conf.host_conf, Any())

    def test_execute_is_called(self):
        CustomScriptShell().execute_script(self.context, '')

        self.selector_get.assert_called_with(self.script_conf.host_conf, Any())

        self.executor.execute.assert_called_once()

            # def test_flow(self):
    #     script_file = ScriptFile('name','text')
    #     env_vars = Mock()
    #     self.script_conf.host_conf.parameters = env_vars
    #     self.downloader.return_value = script_file
    #     self.executor.create_temp_folder.return_value = 'tmp123'
    #
    #     CustomScriptShell().execute_script(self.context, '')
    #
    #     self.executor.create_temp_folder.assert_called()
    #     self.executor.copy_script.assert_called_with('tmp123', script_file)
    #     self.executor.run_script.assert_called_with('tmp123', script_file, env_vars, Any(lambda x: isinstance(x, ReservationOutputWriter)))
    #     self.executor.delete_temp_folder.assert_called_with('tmp123')

    # def test_delete_temp_folder_when_copying_fails(self):
    #     self.executor.create_temp_folder.return_value = 'tmp123'
    #     self.executor.copy_script.side_effect = Exception()
    #
    #     with self.assertRaises(Exception):
    #         CustomScriptShell().execute_script(self.context, '')
    #
    #     self.executor.delete_temp_folder.assert_called_with('tmp123')
    #
    # def test_delete_temp_folder_when_running_fails(self):
    #     self.executor.create_temp_folder.return_value = 'tmp123'
    #     self.executor.run_script.side_effect = Exception()
    #
    #     with self.assertRaises(Exception):
    #         CustomScriptShell().execute_script(self.context, '')
    #
    #     self.executor.delete_temp_folder.assert_called_with('tmp123')