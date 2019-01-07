class CbBase(object):
    """A computational bacterium performs its basic function in a
    continuous but periodic fashion (sleep, act).

    A bacterium responds to changes in its environmental context
    by checking the attributes of the given context.

    A bacterium reacts to events. An event interrupts
    and pre-empt its other on-going activity (in this case sleeping).

    """
    def __init__(self, env, context, events, kind):
        self.env = env
        self.kind = kind
        self.context = context
        self.events = events

        self.init_cb_process();

    def init_cb_process(self):
        self.acting_process = self.env.process(self.acting(context,period))
        self.listening_process = self.env.process(self.listening(events))


    def acting(self, context, period):
        """
            Perform basic sustenance activity.
            Sleep for the period and wake up to produce heat
            If interrupted, process the event that caused the interrupt.
        """
        sleep_time_left = period
        while True:
            try:
                #sleep for period
                sleep_starts_at = self.env.now
                yield self.env.timeout(sleep_time_left)
                #act
                self.sustenance_activity()
                sleep_time_left = period
            except simpy.Interrupt:
                # check event and perform action
                self.on_interrupt_activity()


    def listening(self,events):
        """Pick up interesting events and interrupt basic activity"""
        filter = lambda event: (event[0] == self.kind)
        while True:
            self.event = yield events.get(filter)
            self.acting_process.interrupt()
