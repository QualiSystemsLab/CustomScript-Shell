from cloudshell.shell.core.resource_driver_interface import ResourceDriverInterface
from cloudshell.cm.customscript.customscript_shell import CustomScriptShell


class CustomScriptShellDriver(ResourceDriverInterface):
    def cleanup(self):
        pass

    def __init__(self):
        self.customscript_shell = CustomScriptShell()

    def initialize(self, context):
        pass

    def execute_script(self, context, script_configuration_json, cancellation_context):
        return self.customscript_shell.execute_script(context, script_configuration_json, cancellation_context)


