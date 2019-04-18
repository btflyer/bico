import simpy

class CbBase(object):
    """A computational bacterium performs its basic function in a
    continuous but periodic fashion (sleep, act).

    A bacterium responds to changes in its environmental context
    by checking the attributes of the given context.

    A bacterium reacts to events. An event interrupts
    and pre-empt its other on-going activity (in this case sleeping).

    """
    def __init__(self, env, id, context, event_stream, event_kinds, period):
        self.env = env
        self.id = id
        self.ev_kinds = event_kinds
        self.context = context
        self.events = event_stream
        self.event = None
        self.period = period

        self.init_cb_process();

    def init_cb_process(self):
        self.acting_process = self.env.process(self.acting())
        self.listening_process = self.env.process(self.listening())


    def acting(self):
        """
            Perform basic sustenance activity.
            Sleep for the period and wake up to do the work.
            If interrupted, process the event that caused the interrupt.
        """
        sleep_time_left = self.period
        while True:
            try:
                #sleep for period
                sleep_starts_at = self.env.now
                yield self.env.timeout(sleep_time_left)
                #act
                self.sustenance_activity()
                sleep_time_left = self.period
            except simpy.Interrupt:
                # handle event
                self.on_interrupt_activity()
                #clear the processed event
                self.event = None
                sleep_time_left = self.period - (self.env.now-sleep_starts_at)
                print('sleep_time_left %d' % sleep_time_left)


    def listening(self):
        """Pick up interesting events and interrupt basic activity"""
        filter = lambda event: ((event[1] is None or event[1] == self.id)
                                and (event[0] in self.ev_kinds))
        while True:
            self.event = yield self.events.get(filter)
            #interrupt the duty cycle to process the event
            self.acting_process.interrupt()
            
