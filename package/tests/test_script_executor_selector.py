from unittest import TestCase
from mock import Mock, patch

from cloudshell.cm.customscript.domain.script_configuration import HostConfiguration
from cloudshell.cm.customscript.domain.script_executor_selector import ScriptExecutorSelector


class TestScriptExecutorSelector(TestCase):

    def test_create_windows_script_executor(self):
        host_conf = HostConfiguration()
        host_conf.connection_method = 'winrm'
        with patch('cloudshell.cm.customscript.domain.script_executor_selector.WindowsScriptExecutor') as win_ctor:
            win_executor = Mock()
            win_ctor.return_value = win_executor
            result = ScriptExecutorSelector().get(host_conf, Mock(), Mock())
            self.assertEqual(result, win_executor)

    def test_create_linux_script_executor(self):
        host_conf = HostConfiguration()
        host_conf.connection_method = 'ssh'
        with patch('cloudshell.cm.customscript.domain.script_executor_selector.LinuxScriptExecutor') as linux_ctor:
            linux_executor = Mock()
            linux_ctor.return_value = linux_executor
            result = ScriptExecutorSelector().get(host_conf, Mock(), Mock())
            self.assertEqual(result, linux_executor)