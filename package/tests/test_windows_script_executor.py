from unittest import TestCase
from mock import patch, Mock

from cloudshell.cm.customscript.domain.script_configuration import HostConfiguration
from cloudshell.cm.customscript.domain.script_executor import ErrorMsg
from cloudshell.cm.customscript.domain.script_file import ScriptFile
from cloudshell.cm.customscript.domain.windows_script_executor import WindowsScriptExecutor


class TestWindowsScriptExecutor(TestCase):

    def setUp(self):
        self.logger = Mock()
        self.session = Mock()
        self.host = HostConfiguration()
        self.host.ip = "1.2.3.4"

        self.session_patcher = patch('cloudshell.cm.customscript.domain.windows_script_executor.winrm.Session')
        self.session_patcher.start().return_value = self.session

        self.executor = WindowsScriptExecutor(self.logger, self.host)

    def tearDown(self):
        self.session_patcher.stop()

    def test_create_temp_folder_success(self):
        self.session.run_ps = Mock(return_value=Result(0,'tmp123',''))
        result = self.executor.create_temp_folder()
        self.assertEqual('tmp123', result)

    def test_create_temp_folder_fail(self):
        self.session.run_ps = Mock(return_value=Result(1,'','some error'))
        with self.assertRaises(Exception) as e:
            self.executor.create_temp_folder()
        self.assertEqual(ErrorMsg.CREATE_TEMP_FOLDER % 'some error', e.exception.message)

    def test_copy_script_success(self):
        self.session.run_ps = Mock(return_value=Result(0,'',''))
        self.executor.copy_script('tmp123', ScriptFile('script1','some script code'))

    def test_copy_script_fail(self):
        self.session.run_ps = Mock(return_value=Result(1,'','some error'))
        with self.assertRaises(Exception) as e:
            self.executor.copy_script('tmp123', ScriptFile('script1','some script code'))
        self.assertEqual(ErrorMsg.COPY_SCRIPT % 'some error', e.exception.message)

    def test_run_script_success(self):
        output_writer = Mock()
        self.session.run_ps = Mock(return_value=Result(0, 'some output', 'some error'))
        self.executor.run_script('tmp123', ScriptFile('script1', 'some script code'), output_writer)
        output_writer.write.assert_any_call('some output')
        output_writer.write.assert_any_call('some error')

    def test_run_script_fail(self):
        output_writer = Mock()
        self.session.run_ps = Mock(return_value=Result(1, 'some output', 'some error'))
        with self.assertRaises(Exception, ) as e:
            self.executor.run_script('tmp123', ScriptFile('script1', 'some script code'), output_writer)
        self.assertEqual(ErrorMsg.RUN_SCRIPT % 'some error', e.exception.message)
        output_writer.write.assert_any_call('some output')
        output_writer.write.assert_any_call('some error')

    def test_delete_temp_folder_success(self):
        self.session.run_ps = Mock(return_value=Result(0,'',''))
        self.executor.delete_temp_folder('tmp123')

    def test_delete_temp_folder_fail(self):
        self.session.run_ps = Mock(return_value=Result(1,'','some error'))
        with self.assertRaises(Exception) as e:
            self.executor.delete_temp_folder('tmp123')
        self.assertEqual(ErrorMsg.DELETE_TEMP_FOLDER % 'some error', e.exception.message)


class Result(object):
    def __init__(self, status_code, std_out, std_err):
        self.std_err = std_err
        self.std_out = std_out
        self.status_code = status_code
