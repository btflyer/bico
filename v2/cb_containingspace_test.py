from cb_heater import CbHeater
from cb_thermometer import CbThermometer
from cb_containingspace import ContainingSpace

import simpy

SIM_TIME = 2300  # seconds (10 minutes)
    
def heat_source_activity(env,space,event_queue,actions):
    for action in actions:
        yield env.timeout(action[0])
        print('>> Heat source action %s' % action[1])
        if action[1] is 'add':
            #action[2].heat_on = True
            space.add_heat_source(action[2])
            yield event_queue.put(('heat_on',action[2].id,env.now))
        elif action[1] is 'remove':
            space.remove_heat_source(action[2])
            #action[2].heat_on = False #not strictly necessary, could send an event
            yield event_queue.put(('heat_off',action[2].id,env.now))
        elif action[1] is 'change':
            heat_event = 'heat_off' if action[2].heat_on else 'heat_on'
            event = (heat_event,action[2].id,env.now)
            print('>> Heat change event created %s, %s, %s' % event)
            yield event_queue.put(event)
        else:
            raise RuntimeError('heat_source_activity(): Unknown action type: %s'
                               % action[1])

def temp_listener(events):
        """Pick up interesting events and interrupt basic activity"""
        filter = lambda event: (event[0]  == 'temp_measurement')
        while True:
            event = yield events.get(filter)
            print('## Temp measurement: %.1f, %s, %s' % (event[1],event[2],event[3]))


def test_case_1(env):
    """Complex test case: 3 heat sources introduced during the scenario and
    one of them removed later. Initial room temp is 290K with 288K as the
    low equilibrium.
    """
    room = ContainingSpace(env,288,290,(5*5*3))
    event_queue = simpy.FilterStore(env)
    hs_1 = CbHeater(env,'h1',room,event_queue,['ping','heat_on','heat_off'],10,100)
    hs_2 = CbHeater(env,'h2',room,event_queue,['ping','heat_on','heat_off'],10,300)
    hs_3 = CbHeater(env,'h3',room,event_queue,['ping','heat_on','heat_off'],10,200)
    tmeter1 = CbThermometer(env,'t1',room,event_queue,['ping'],10)
    heat_source_actions = [
        (100,'add',hs_1),
        (300,'add',hs_2),
        (600,'change',hs_2),
        (810,'add',hs_3),
        (90,'remove',hs_1)
    ]                
    env.process(heat_source_activity(env,room,event_queue,heat_source_actions))
    env.process(temp_listener(event_queue))
    # Execute!
    print('==== Start of test_case_1 ====')
    env.run(until=SIM_TIME)
    # End of run
    print('#### End of test_case_1 after %d seconds ####' % SIM_TIME)



## run tests
env = simpy.Environment()
#event_queue = simpy.FilterStore(env) # should it be global? probably yes, if many spaces, now only one
#env.process(event_generator(env,event_queue,31))
#heater1 = CbHeater(env,'heater1',None,event_queue,['ping','heat_on','heat_off'],10,25)
#tmeter1 = CbThermometer(env,'temp1',None,event_queue,['ping'],10)
#env.run(until=350)
test_case_1(env)
