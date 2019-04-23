from cb_base import CbBase

class CbHeater(CbBase):
    """A computational bacterium producing heat a.k.a heater
    """
    def __init__(self, env, id, context, event_stream, event_kinds, period, output, heat_on=False):

        super().__init__(env, id, context, event_stream, event_kinds, period)

        #Heater properties
        self.heat_output = output
        self.heat_on = heat_on
        self.output_unit = "watts"
        self.listener_callback = None
        
    def set_listener_callback(self,callable):
        self.listener_callback = callable

    def sustenance_activity(self):
        if (self.heat_on):
            print ("{} at {} producing heat: {} {}".format(self.id,self.env.now,self.heat_output,self.output_unit))
        else:
            print ("{} at {} not producing heat".format(self.id,self.env.now))

    def on_interrupt_activity(self):
        print('{} at {} interrupted with {}'.format(self.id,self.env.now,self.event))
        changed = False
        if self.event[0] == 'heat_on' and not self.heat_on:
            self.heat_on = True
            changed = True
        elif self.event[0] == 'heat_off' and self.heat_on:
            self.heat_on = False
            changed = True
        if self.listener_callback and changed:
            self.listener_callback(self)
    
    
