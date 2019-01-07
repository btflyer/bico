from cb_base import CbBase

class CbHeater(CbBase):
    """A computational bacterium producing heat a.k.a heater
    """
    def __init__(self, env, name, kind, period, context, events):

        super().__init__(self,env,context,events, kind)

        self.name = name

        #Heater properties
        self.heat_output = 25
        self.output_unit = "watts"


    def sustenance_activity(self, context, period):
        print ("Producing heat: {} {}".format(self.heat_output,self.output_unit))

    def on_interrupt_activity():
        print('Heater interrupted')
