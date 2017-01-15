from unittest import TestCase
from mock import patch, Mock

from cloudshell.cm.customscript.domain.script_configuration import HostConfiguration
from cloudshell.cm.customscript.domain.script_executor import ErrorMsg
from cloudshell.cm.customscript.domain.script_file import ScriptFile
from cloudshell.cm.customscript.domain.linux_script_executor import LinuxScriptExecutor
from tests.helpers import Any


class TestLinuxScriptExecutor(TestCase):

    def setUp(self):
        self.logger = Mock()
        self.session = Mock()
        self.host = HostConfiguration()
        self.host.ip = "1.2.3.4"

        self.session_patcher = patch('cloudshell.cm.customscript.domain.linux_script_executor.SSHClient')
        self.session_patcher.start().return_value = self.session

        self.executor = LinuxScriptExecutor(self.logger, self.host)

    def tearDown(self):
        self.session_patcher.stop()

    def _mock_session_answer(self, exit_code, stdout, stderr):
        stdout_mock = Mock()
        stderr_mock = Mock()
        stdout_mock.channel.recv_exit_status = Mock(return_value=exit_code)
        stdout_mock.readlines = Mock(return_value=stdout)
        stderr_mock.readlines = Mock(return_value=stderr)
        self.session.exec_command = Mock(return_value=(None, stdout_mock, stderr_mock))

    def test_user_password(self):
        self.host.username = 'root'
        self.host.password = '1234'
        executor = LinuxScriptExecutor(self.logger, self.host)
        self.session.connect.assert_called_with('1.2.3.4',  username='root', password='1234')

    def test_pem_file(self):
        self.host.access_key = 'just an access key'
        key_obj = Mock()
        with patch('cloudshell.cm.customscript.domain.linux_script_executor.RSAKey.from_private_key') as from_private_key:
            from_private_key.return_value = key_obj
            executor = LinuxScriptExecutor(self.logger, self.host)
        self.session.connect.assert_called_with('1.2.3.4', pkey=key_obj)

    def test_create_temp_folder_success(self):
        self._mock_session_answer(0,'tmp123','')
        result = self.executor.create_temp_folder()
        self.assertEqual('tmp123', result)

    def test_create_temp_folder_fail(self):
        self._mock_session_answer(1,'','some error')
        with self.assertRaises(Exception) as e:
            self.executor.create_temp_folder()
        self.assertEqual(ErrorMsg.CREATE_TEMP_FOLDER % 'some error', e.exception.message)

    def test_copy_script_success(self):
        sftp = Mock()
        self.session.open_sftp = Mock(return_value=sftp)
        self.executor.copy_script('tmp123', ScriptFile('script1','some script code'))
        sftp.putfo.assert_called_once_with(Any(lambda x: x.getvalue() == 'some script code'), 'tmp123/script1')
        sftp.close.assert_called_once()

    def test_copy_script_fail(self):
        sftp = Mock()
        sftp.putfo.side_effect = IOError('some error')
        self.session.open_sftp = Mock(return_value=sftp)
        with self.assertRaises(Exception) as e:
            self.executor.copy_script('tmp123', ScriptFile('script1','some script code'))
        self.assertIn(ErrorMsg.COPY_SCRIPT % '', e.exception.message)
        self.assertIn('some error', e.exception.message)
        sftp.close.assert_called_once()

    def test_run_script_success(self):
        output_writer = Mock()
        self._mock_session_answer(0, 'some output', '')
        self.executor.run_script('tmp123', ScriptFile('script1', 'some script code'), output_writer)
        output_writer.write.assert_any_call('some output')

    def test_run_script_fail(self):
        output_writer = Mock()
        self._mock_session_answer(1, 'some output', 'some error')
        with self.assertRaises(Exception, ) as e:
            self.executor.run_script('tmp123', ScriptFile('script1', 'some script code'), output_writer)
        self.assertEqual(ErrorMsg.RUN_SCRIPT % 'some error', e.exception.message)
        output_writer.write.assert_any_call('some output')
        output_writer.write.assert_any_call('some error')

    def test_delete_temp_folder_success(self):
        self._mock_session_answer(0,'','')
        self.executor.delete_temp_folder('tmp123')

    def test_delete_temp_folder_fail(self):
        self._mock_session_answer(1,'','some error')
        with self.assertRaises(Exception) as e:
            self.executor.delete_temp_folder('tmp123')
        self.assertEqual(ErrorMsg.DELETE_TEMP_FOLDER % 'some error', e.exception.message)
