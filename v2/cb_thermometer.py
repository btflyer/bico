from cb_base import CbBase

class CbThermometer(CbBase):
    """A computational bacterium measuring heat
    """
    def __init__(self, env, name, context, event_stream, event_kinds, period):

        super().__init__(env, name, context, event_stream, event_kinds, period)

        #self.name = name

        #Heater properties
        self.last_temp_read = -1



    def sustenance_activity(self):
        print ("{} at {} measuring heat: {}".format(self.name,self.env.now,self.last_temp_read))

    def on_interrupt_activity(self):
        print('{} at {} thermometer interrupted with {}'.format(self.name,self.env.now,self.event))
