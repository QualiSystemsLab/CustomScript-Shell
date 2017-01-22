from unittest import TestCase
from mock import patch, Mock

from cloudshell.cm.customscript.domain.script_configuration import HostConfiguration
from cloudshell.cm.customscript.domain.script_executor import ErrorMsg
from cloudshell.cm.customscript.domain.script_file import ScriptFile
from cloudshell.cm.customscript.domain.windows_script_executor import WindowsScriptExecutor
from tests.helpers import Any


class TestWindowsScriptExecutor(TestCase):

    def setUp(self):
        self.logger = Mock()
        self.session = Mock()
        self.session_ctor = Mock()
        self.host = HostConfiguration()
        self.host.username = 'admin'
        self.host.password = '1234'
        self.host.ip = "1.2.3.4"

        self.session_patcher = patch('cloudshell.cm.customscript.domain.windows_script_executor.winrm.Session')
        self.session_ctor = self.session_patcher.start()
        self.session_ctor.return_value = self.session

    def tearDown(self):
        self.session_patcher.stop()

    def test_http(self):
        WindowsScriptExecutor(self.logger, self.host)
        self.session_ctor.assert_called_with('1.2.3.4', auth=('admin','1234'))

    def test_https(self):
        self.host.connection_secured = True
        WindowsScriptExecutor(self.logger, self.host)
        self.session_ctor.assert_called_with('1.2.3.4', auth=('admin','1234'), transport='ssl')

    def test_execute_success(self):
        executor = WindowsScriptExecutor(self.logger, self.host)
        output_writer = Mock()
        self.session.run_ps = Mock(return_value=Result(0, 'some output', 'some error'))
        executor.execute(ScriptFile('script1', 'some script code'), {'var1':'123'}, output_writer)
        output_writer.write.assert_any_call('some output')
        output_writer.write.assert_any_call('some error')

    def test_execute_fail(self):
        executor = WindowsScriptExecutor(self.logger, self.host)
        output_writer = Mock()
        self.session.run_ps = Mock(return_value=Result(1, 'some output', 'some error'))
        with self.assertRaises(Exception, ) as e:
            executor.execute(ScriptFile('script1', 'some script code'), {}, output_writer)
        self.assertEqual(ErrorMsg.RUN_SCRIPT % 'some error', e.exception.message)
        output_writer.write.assert_any_call('some output')
        output_writer.write.assert_any_call('some error')


class Result(object):
    def __init__(self, status_code, std_out, std_err):
        self.std_err = std_err
        self.std_out = std_out
        self.status_code = status_code
