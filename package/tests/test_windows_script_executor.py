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

    def test_execute_success(self):
        output_writer = Mock()
        self.session.run_ps = Mock(return_value=Result(0, 'some output', 'some error'))
        self.executor.execute(ScriptFile('script1', 'some script code'), {'var1':'123'}, output_writer)
        output_writer.write.assert_any_call('some output')
        output_writer.write.assert_any_call('some error')

    def test_execute_fail(self):
        output_writer = Mock()
        self.session.run_ps = Mock(return_value=Result(1, 'some output', 'some error'))
        with self.assertRaises(Exception, ) as e:
            self.executor.execute(ScriptFile('script1', 'some script code'), {}, output_writer)
        self.assertEqual(ErrorMsg.RUN_SCRIPT % 'some error', e.exception.message)
        output_writer.write.assert_any_call('some output')
        output_writer.write.assert_any_call('some error')


class Result(object):
    def __init__(self, status_code, std_out, std_err):
        self.std_err = std_err
        self.std_out = std_out
        self.status_code = status_code
