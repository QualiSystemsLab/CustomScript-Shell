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

    def create_temp_folder(self):
        """
        :rtype str
        """
        code = """
$fullPath = Join-Path $env:Temp ([System.Guid]::NewGuid().ToString())
New-Item $fullPath -type directory | Out-Null
Write-Output $fullPath
        """
        result = self._run_ps(code)
        if result.status_code != 0:
            raise Exception(ErrorMsg.CREATE_TEMP_FOLDER % result.std_err)
        return result.std_out.rstrip('\r\n')

    def copy_script(self, tmp_folder, script_file):
        """
        :type tmp_folder: str
        :type script_file: ScriptFile
        """
        encoded_script_txt = base64.b64encode(script_file.text.encode("utf-8"))
        code = """
$path   = Join-Path "%s" "%s"
$data   = [System.Convert]::FromBase64String("%s")
Add-Content -value $data -encoding byte -path $path
"""
        result = self._run_ps(code, tmp_folder, script_file.name, encoded_script_txt)
        if result.status_code != 0:
            raise Exception(ErrorMsg.COPY_SCRIPT % result.std_err)

    def run_script(self, tmp_folder, script_file, env_vars, output_writer):
        """
        :type tmp_folder: str
        :type script_file: ScriptFile
        :type env_vars: dict
        :type output_writer: ReservationOutputWriter
        """
        code = ''
        for key, value in (env_vars or {}).iteritems():
            code += '\n$env:%s = "%s"' % (key, str(value))
        code += """
$path = Join-Path "%s" "%s"
cmd.exe /c $path
"""
        result = self._run_ps(code, tmp_folder, script_file.name)
        output_writer.write(result.std_out)
        output_writer.write(result.std_err)
        if result.status_code != 0:
            raise Exception(ErrorMsg.RUN_SCRIPT % result.std_err)

    def delete_temp_folder(self, tmp_folder):
        """
        :type tmp_folder: str
        """
        code = """
$path = "%s"
Remove-Item $path -recurse
"""
        result = self._run_ps(code % tmp_folder)
        if result.status_code != 0:
            raise Exception(ErrorMsg.DELETE_TEMP_FOLDER % result.std_err)

    def _run_ps(self, txt, *args):
        code = txt % args
        self.logger.debug('PowerShellScript:' + code)
        result = self.session.run_ps(code)
        self.logger.debug('ReturnedCode:' + str(result.status_code))
        self.logger.debug('Stdout:' + result.std_out)
        self.logger.debug('Stderr:' + result.std_err)
        return result
