
from cloudshell.shell.core.driver_context import CancellationContext


class CancellationSampler(object):
    def __init__(self, cancellation_context):
        '''
        :type cancellation_context: CancellationContext
        '''
        self.cancellation_context = cancellation_context

    def is_cancelled(self):
        return self.cancellation_context.is_cancelled == True

    def throw(self):
        raise CancellationException("Command was cancelled")

    def throw_if_canceled(self):
        if self.is_cancelled():
            self.throw()


class CancellationException(Exception):
    pass