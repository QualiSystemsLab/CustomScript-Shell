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
    def run_script(self, tmp_folder, script_file, env_vars, output_writer):
        """
        :type tmp_folder: str
        :type script_file: ScriptFile
        :type env_vars: dict
        :type output_writer: ReservationOutputWriter
        """
        pass

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