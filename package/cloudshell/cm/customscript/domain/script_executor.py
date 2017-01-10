import os
from abc import abstractmethod, ABCMeta

from cloudshell.cm.customscript.domain.script_file import ScriptFile


class IScriptExecutor(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def create_temp_folder(self):
        """
        :rtype str
        """
        return None

    @abstractmethod
    def copy_script(self, tmp_folder, script_file):
        """
        :type tmp_folder: str
        :type script_file: ScriptFile
        """
        pass

    @abstractmethod
    def run_script(self, tmp_folder, script_file, output_writer):
        """
        :type tmp_folder: str
        :type script_file: ScriptFile
        :type output_writer: ReservationOutputWriter
        :rtype ExecutionResult
        """
        return None

    @abstractmethod
    def delete_temp_folder(self, tmp_folder):
        """
        :type tmp_folder: str
        """
        pass


class ErrorMsg(object):
    CREATE_TEMP_FOLDER = 'Failed to create temp folder on target machine. Error: ' + os.linesep + '%s'
    DELETE_TEMP_FOLDER = 'Failed to delete the temp folder from target machine. Error: ' + os.linesep + '%s'
    COPY_SCRIPT = 'Failed to copy the script to target machine. Error: ' + os.linesep + '%s'
    RUN_SCRIPT = 'Failed to run the script on target machine. Error: ' + os.linesep + '%s'


class ExecutionResult(object):
    def __init__(self, success, output, error):
        self.error = error
        self.output = output
        self.success = success


# def throw_error(err):
#     def func_provider(func):
#         def func_wrapper(*args, **kwargs):
#             result = func(*args, **kwargs)
#             if result.status_code != 0:
#                 raise Exception(err + os.linesep + result.success)
#         return func_wrapper
#     return func_provider


class ReservationOutputWriter(object):
    def __init__(self, session, command_context):
        """
        :type session: CloudShellAPISession
        :type command_context: ResourceCommandContext
        """
        self.session = session
        self.resevation_id = command_context.reservation.reservation_id

    def write(self, msg):
        self.session.WriteMessageToReservationOutput(self.resevation_id, msg)