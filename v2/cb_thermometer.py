from cb_base import CbBase

class CbThermometer(CbBase):
    """A computational bacterium measuring heat
    """
    def __init__(self, env, id, context, event_stream, event_kinds, period):

        super().__init__(env, id, context, event_stream, event_kinds, period)

        #self.id = id

        #Heater properties
        self.last_temp_read = -1



    def sustenance_activity(self):
        if self.context:
           self.last_temp_read = self.context.temperature 
        print ("{} at {} measuring heat: {:.1f}".format(self.id,self.env.now,self.last_temp_read))

    def on_interrupt_activity(self):
        print('{} at {} thermometer interrupted with {}'.format(self.id,self.env.now,self.event))
