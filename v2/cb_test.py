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


## run tests
env = simpy.Environment()
event_queue = simpy.FilterStore(env)
env.process(event_generator(env,event_queue,31))
heater1 = CbHeater(env,'heater1',None,event_queue,['ping','heat_on','heat_off'],10,25)
tmeter1 = CbThermometer(env,'temp1',None,event_queue,['ping'],10)
env.run(until=350)
