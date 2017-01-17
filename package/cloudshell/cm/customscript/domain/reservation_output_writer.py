

class ReservationOutputWriter(object):
    def __init__(self, session, command_context):
        """
        :type session: CloudShellAPISession
        :type command_context: ResourceCommandContext
        """
        self.session = session
        self.resevation_id = command_context.reservation.reservation_id

    def write(self, msg):
        if msg:
            self.session.WriteMessageToReservationOutput(self.resevation_id, msg)