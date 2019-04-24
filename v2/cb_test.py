from cb_heater import CbHeater
from cb_thermometer import CbThermometer

import simpy

def event_generator(env,queue,period):
    """Put events into the queue periodically"""
    # TODO: Kind of event and creation time should be randomized properly
    event_no = 0
    while True:
        yield env.timeout(period)
        event_no = event_no + 1
        if ((event_no % 3) == 0):
            event = ('ping',None,env.now) #only _one_ receiver will get this
        elif ((event_no % 3) == 1):
            event = ('heat_on','heater1',env.now)
        else:
            event = ('heat_off','heater1',env.now)
        yield queue.put(event)
        #if (event[0] == 'ping'): #issue multiple events to simulate broadcast
        #    yield queue.put(event)
        print('At %.1f: created event %s number %s' %(env.now,event,event_no))

def heater_state_change_listener(heater):
    print('Heater %s is %s' % (heater.id,'on' if heater.heat_on else 'off'))

def temp_listener(events):
        """Pick up temperature measurement events"""
        filter = lambda event: (event[0]  == 'temp_measurement')
        while True:
            event = yield events.get(filter)
            print('Temp measurement received: %.1f, %s, %s' % (event[1],event[2],event[3]))

class SimpleContext(object):
    """Simple struct for representing a minimal context for a thermometer"""
    def __init__(self, temp):
        self.temperature = temp

## run tests
env = simpy.Environment()
event_queue = simpy.FilterStore(env)
env.process(event_generator(env,event_queue,31))
env.process(temp_listener(event_queue))
heater1 = CbHeater(env,'heater1',None,event_queue,['ping','heat_on','heat_off'],10,25)
heater1.set_listener_callback(heater_state_change_listener)
tmeter1 = CbThermometer(env,'temp1',SimpleContext(290.0),event_queue,['ping'],30)
env.run(until=350)
