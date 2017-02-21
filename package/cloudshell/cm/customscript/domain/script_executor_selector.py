from cloudshell.cm.customscript.domain.linux_script_executor import LinuxScriptExecutor
from cloudshell.cm.customscript.domain.windows_script_executor import WindowsScriptExecutor


class ScriptExecutorSelector(object):
    @staticmethod
    def get(host_conf, logger, cancel_sampler):
        """
        :type host_conf: HostConfiguration
        :type logger: Logger
        :type cancel_sampler: CancellationSampler
        :rtype IScriptExecutor
        """
        if host_conf.connection_method == 'ssh':
            return LinuxScriptExecutor(logger, host_conf, cancel_sampler)
        else:
            return WindowsScriptExecutor(logger, host_conf, cancel_sampler)
