import base64
import winrm
from logging import Logger

from cloudshell.cm.customscript.domain.reservation_output_writer import ReservationOutputWriter
from cloudshell.cm.customscript.domain.script_configuration import HostConfiguration
from cloudshell.cm.customscript.domain.script_executor import IScriptExecutor, ErrorMsg


class WindowsScriptExecutor(IScriptExecutor):
    def __init__(self, logger, target_host):
        """
        :type logger: Logger
        :type target_host: HostConfiguration
        """
        self.logger = logger
        self.session = winrm.Session(target_host.ip, auth=(target_host.username, target_host.password))

    def execute(self, script_file, env_vars, output_writer):
        """
        :type tmp_folder: str
        :type script_file: ScriptFile
        :type env_vars: dict
        :type output_writer: ReservationOutputWriter
        """
        code = script_file.text
        self.logger.debug('PowerShellScript:' + code)
        if env_vars:
            encoded_script = base64.b64encode(script_file.text.encode('utf_16_le')).decode('ascii')
            code = '\n'.join(['$env:%s="%s"'%(k, str(v)) for k,v in env_vars.iteritems()])
            self.logger.debug('AddingEnvVars:' + code)
            code += '\npowershell -encodedcommand %s' % encoded_script

        result = self._run_ps(code)
        output_writer.write(result.std_out)
        output_writer.write(result.std_err)
        if result.status_code != 0:
            raise Exception(ErrorMsg.RUN_SCRIPT % result.std_err)


    def _run_ps(self, code):
        result = self.session.run_ps(code)
        self.logger.debug('ReturnedCode:' + str(result.status_code))
        self.logger.debug('Stdout:' + result.std_out)
        self.logger.debug('Stderr:' + result.std_err)
        return result
