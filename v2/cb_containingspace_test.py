from cb_heater import CbHeater
from cb_thermometer import CbThermometer
from cb_containingspace import ContainingSpace

import simpy

SIM_TIME = 2000  # seconds (10 minutes)


def heat_source_activity(env,space,actions):
    for action in actions:
        yield env.timeout(action[0])
        print('>> Heat source action %s' % action[1])
        if action[1] is 'add':
            action[2].heat_on = True
            space.add_heat_source(action[2])
        elif action[1] is 'remove':
            space.remove_heat_source(action[2])
            action[2].heat_on = False
        elif action[1] is 'change':
            if action[2].heat_on:
                action[2].heat_on = False  #should send an event to heater!
            else:
                action[2].heat_on = True
            # action[2].output = action[3] #can only turn it on and off
            space.heat_source_output_changed(action[2]) #heater should issue an event for this
                                                        #or maybe it just emits heat...
        else:
            raise RuntimeError('heat_source_activity(): Unknown action type: %s'
                               % action[1])           

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
    env.process(heat_source_activity(env,room,heat_source_actions))
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
