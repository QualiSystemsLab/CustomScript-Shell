import base64

import time
from multiprocessing.pool import ThreadPool
from uuid import uuid4

import re
import winrm
from logging import Logger

from cloudshell.cm.customscript.domain.reservation_output_writer import ReservationOutputWriter
from cloudshell.cm.customscript.domain.script_configuration import HostConfiguration
from cloudshell.cm.customscript.domain.script_executor import IScriptExecutor, ErrorMsg, ExcutorConnectionError
from requests import ConnectionError


class WindowsScriptExecutor(IScriptExecutor):
    def __init__(self, logger, target_host, cancel_sampler):
        """
        :type logger: Logger
        :type target_host: HostConfiguration
        :type cancel_sampler: CancellationContext
        """
        self.logger = logger
        self.cancel_sampler = cancel_sampler
        self.pool = ThreadPool(processes=1)
        if target_host.connection_secured:
            self.session = winrm.Session(target_host.ip, auth=(target_host.username, target_host.password), transport='ssl')
        else:
            self.session = winrm.Session(target_host.ip, auth=(target_host.username, target_host.password))

    def connect(self):
        try:
            uid = str(uuid4())
            result = self.session.run_cmd('@echo '+uid)
            assert uid in result.std_out
        except ConnectionError as e:
            match = re.search(r'\[Errno (?P<errno>\d+)\]', str(e.message))
            error_code = int(match.group('errno')) if match else 0
            raise ExcutorConnectionError(error_code, e)
        except Exception as e:
            raise ExcutorConnectionError(0, e)

    def execute(self, script_file, env_vars, output_writer):
        """
        :type tmp_folder: str
        :type script_file: ScriptFile
        :type env_vars: dict
        :type output_writer: ReservationOutputWriter
        """
        self.logger.debug('PowerShellScript:' + script_file.text)
        code = ''
        for key, value in (env_vars or {}).iteritems():
            code += 'set %s="%s" &&' % (key, str(value))
        encoded_script = base64.b64encode(script_file.text.encode('utf_16_le')).decode('ascii')
        code += '\npowershell -encodedcommand %s' % encoded_script

        result = self._run_cancelable(code)
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

    def _run_cancelable(self, code):
        shell_id = self.session.protocol.open_shell()
        command_id = self.session.protocol.run_command(shell_id, code)

        async_result = self.pool.apply_async(self.session.protocol.get_command_output, kwds={'shell_id': shell_id, 'command_id': command_id})
        try:
            while not async_result.ready():
                if self.cancel_sampler.is_cancelled():
                    self.cancel_sampler.throw()
                time.sleep(1)
            result = winrm.Response(async_result.get())
        finally:
            self.session.protocol.cleanup_command(shell_id, command_id)
            self.session.protocol.close_shell(shell_id)

        self.logger.debug('ReturnedCode:' + str(result.status_code))
        self.logger.debug('Stdout:' + result.std_out)
        self.logger.debug('Stderr:' + result.std_err)
        return result