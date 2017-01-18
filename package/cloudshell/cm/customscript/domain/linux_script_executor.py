import sys
from StringIO import StringIO
from paramiko import SSHClient, AutoAddPolicy, RSAKey
from scpclient import Write, SCPError

from cloudshell.cm.customscript.domain.reservation_output_writer import ReservationOutputWriter
from cloudshell.cm.customscript.domain.script_configuration import HostConfiguration
from cloudshell.cm.customscript.domain.script_executor import IScriptExecutor, ErrorMsg
from cloudshell.cm.customscript.domain.script_file import ScriptFile


class LinuxScriptExecutor(IScriptExecutor):
    class ExecutionResult(object):
        def __init__(self, exit_code, std_out, std_err):
            self.std_err = std_err
            self.std_out = std_out
            self.success = exit_code == 0

    def __init__(self, logger, target_host):
        """
        :type logger: Logger
        :type target_host: HostConfiguration
        """
        self.logger = logger
        self.session = SSHClient()
        self.session.set_missing_host_key_policy(AutoAddPolicy())
        if target_host.access_key:
            key_stream = StringIO(target_host.access_key)
            key_obj = RSAKey.from_private_key(key_stream)
            self.session.connect(target_host.ip, pkey=key_obj)
        else:
            self.session.connect(target_host.ip, username=target_host.username, password=target_host.password)

    def execute(self, script_file, env_vars, output_writer):
        """
        :type script_file: ScriptFile
        :type output_writer: ReservationOutputWriter
        """
        self.logger.info('Creating temp folder on target machine ...')
        tmp_folder = self.create_temp_folder()
        self.logger.info('Done (%s).' % tmp_folder)

        try:
            self.logger.info('Copying "%s" (% chars) to "%s" target machine ...' % (
            script_file.name, len(script_file.text), tmp_folder))
            self.copy_script(tmp_folder, script_file)
            self.logger.info('Done.')

            self.logger.info('Running "%s" on target machine ...' % script_file.name)
            self.run_script(tmp_folder, script_file, env_vars, output_writer)
            self.logger.info('Done.')

        finally:
            self.logger.info('Deleting "%s" folder from target machine ...' % tmp_folder)
            self.delete_temp_folder(tmp_folder)
            self.logger.info('Done.')

    def create_temp_folder(self):
        """
        :rtype str
        """
        result = self._run('mktemp -d')
        if not result.success:
            raise Exception(ErrorMsg.CREATE_TEMP_FOLDER % result.std_err)
        return result.std_out.rstrip('\n')

    def copy_script(self, tmp_folder, script_file):
        """
        :type tmp_folder: str
        :type script_file: ScriptFile
        """
        file_stream = StringIO(script_file.text)
        file_size = len(file_stream.getvalue())
        scp = None
        try:
            scp = Write(self.session.get_transport(), tmp_folder)
            scp.send(file_stream, script_file.name, '0601', file_size)
        except SCPError as e:
            raise Exception,ErrorMsg.COPY_SCRIPT % str(e),sys.exc_info()[2]
        finally:
            if scp:
                scp.close()

    def run_script(self, tmp_folder, script_file, env_vars, output_writer):
        """
        :type tmp_folder: str
        :type script_file: ScriptFile
        :type env_vars: dict
        :type output_writer: ReservationOutputWriter
        """
        code = ''
        for key, value in (env_vars or {}).iteritems():
            code += 'export %s=%s;' % (key,str(value))
        code += 'sh '+tmp_folder+'/'+script_file.name
        result = self._run(code)
        output_writer.write(result.std_out)
        output_writer.write(result.std_err)
        if not result.success:
            raise Exception(ErrorMsg.RUN_SCRIPT % result.std_err)

    def delete_temp_folder(self, tmp_folder):
        """
        :type tmp_folder: str
        """
        result = self._run('rm -rf '+tmp_folder)
        if not result.success:
            raise Exception(ErrorMsg.DELETE_TEMP_FOLDER % result.std_err)

    def _run(self, txt, *args):
        code = txt % args
        self.logger.debug('BashScript:' + code)
        stdin, stdout, stderr = self.session.exec_command(code)
        exit_code = stdout.channel.recv_exit_status()
        stdout_txt = ''.join(stdout.readlines())
        stderr_txt = ''.join(stderr.readlines())
        self.logger.debug('ReturnedCode:' + str(exit_code))
        self.logger.debug('Stdout:' + stdout_txt)
        self.logger.debug('Stderr:' + stderr_txt)
        return LinuxScriptExecutor.ExecutionResult(exit_code, stdout_txt, stderr_txt)