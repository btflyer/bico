from cb_base import CbBase

class CbThermometer(CbBase):
    """A computational bacterium measuring heat
    """
    def __init__(self, env, name, kind, period, context, events):

        super().__init__(env,context,events, kind)

        self.name = name

        #Heater properties
        self.last_temp_read = -1



    def sustenance_activity(self, context, period):
        print ("Measuring heat: {} {}".format(self.last_temp_read))

    def on_interrupt_activity():
        print('Thermometer interrupted')
