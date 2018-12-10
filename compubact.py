"""
Computational Bacterium prototype, based on Machine shop example
from simpy docs

Covers:

- Rudimentary Computational Bacterium life-cycle and interaction with
  its environment

Scenario:
  A Computational Bacterium is created with an environmental context and
  an event queue. The bacterium sleeps for a fixed period and then senses
  (reads) the ambient_temperature from the environment and prints it out.
  A simple stochastic process inserts events to the event queue that the
  bacterium listens to. The appearance of an event of the right type
  interrupts the normal processinc cycle, and the bacterium processes the
  event (prints it out) and then continues the interrupted cycle.

"""
import random

import simpy


RANDOM_SEED = 42
RT_MEAN = 20.0         # Avg. room temperature
RT_SIGMA = 2.0         # Sigma of room temperature
SIM_TIME = 600  # Simulation time in seconds


def temperature_dist():
    """Random normal variated temperature around RT_MEAN with RT_SIGMA"""
    return random.normalvariate(RT_MEAN, RT_SIGMA)

class BacterialContext(object):
    """A context or environment for Computational Bacteria to exist in

    attributes:
    - ambient_temperature

    """
    def __init__(self,env,period):
        self.ambient_temperature = RT_MEAN
        self.env = env
        env.process(self.update(period))       

    def update(self, period):
        """Acquire new values for the context variables"""
        while True:
            yield self.env.timeout(period)
            self.ambient_temperature -= 1 #temperature_dist()    
            
    
class ComputationalBacterium(object):
    """A computational bacterium performs its basic function in a
    continuous but periodic fashion (sleep, act).

    A bacterium responds to changes in its environmental context
    by checking the attributes of the given context.

    A bacterium reacts to events. An event interrupts
    and pre-empt its other on-going activity (in this case sleeping).
    
    """
    def __init__(self, env, name, kind, period, context, events, msg_dispatch):
        self.env = env
        self.name = name
        self.kind = kind
        self.context = context
        self.event = None
        self.message_dispatcher = msg_dispatch
        self.events = events
        # Add: message queue for output
        # Start "acting" and "listening" processes for this bacterium
        self.acting_process = env.process(self.acting(context,period))
        # attribute not needed?
        self.listening_process = env.process(self.listening(events))
        self.message_dispatcher.register(self)

        if (self.kind is 'actuator'):
          self.msg_types = ('low temperature', 'high temperature')
        else:
          self.msg_types = ()

    def acting(self, context, period):
        """Perform basic sustenance activity.

        Sleep for the period and wake up to sense ambient temperature.

        If interrupted, process the event that caused the interrupt.

        """
        sleep_time_left = period
        while True:
            try:
                #sleep for period
                sleep_starts_at = self.env.now
                yield self.env.timeout(sleep_time_left)
                #act
                if (self.kind is 'sensor'):
                  print('At %.1f: %s sensing temperature = %.1f' %
                      (self.env.now,self.name,context.ambient_temperature))
                  if (context.ambient_temperature < 18.0):
                    #event = ('actuator','low temperature')
                    event = ('actuator','low temperature')
                    yield self.events.put(event)
                    print('At %.1f: created event %s' %(self.env.now,event))
                elif (self.kind is 'actuator'): 
                  print('At %.1f: %s does something' %(self.env.now,self.name))
                else:
                  print('Null event')
                    
                sleep_time_left = period
            except simpy.Interrupt:
                # check event and perform action
                print('At %.1f: %s interrupted' %
                      (self.env.now,self.name))
                if self.event is not None and self.event[1] in self.msg_types:
                    print('%s processed %s' % (self.name,self.event))

                    print('actuator event caught {}'.format(self.event[1]))
                    #if(self.event[1] is 'low temperature'):
                    #  print('Low temperature event caught')

                    self.event = None
                    sleep_time_left = period - (self.env.now-sleep_starts_at)
                    print('sleep_time_left %d' % sleep_time_left)
                    


    def listening(self,events):
        """Pick up interesting events and interrupt basic activity"""
        filter = lambda event: (event[0] == self.kind)# and event[1] == 'low temperature')# event filter function
        while True:
            self.event = yield events.get(filter)
            self.acting_process.interrupt()

def event_generator(env,queue,period):
    """Put events into the queue periodically"""
    # TODO: Kind of event and creation time should be randomized properly
    event_no = 0
    while True:
        yield env.timeout(period)
        event_no = event_no + 1
        if ((event_no % 2) == 1):
            event = ('sensor','tick')
        else:
            event = ('actuator','tick')
        yield queue.put(event)
        print('At %.1f: created event %s' %(env.now,event))
        
############################################################    
# Setup and start the simulation
#print('Computation Bacteria colony')
#random.seed(RANDOM_SEED)  # This helps reproducing the results

# Create an environment and start the setup process
#env = simpy.Environment()
#context = BacterialContext(env,5)
#event_queue = simpy.FilterStore(env)
#env.process(event_generator(env,event_queue,71))
#cb_1 = ComputationalBacterium(env,'cb_1','A',10,context,event_queue)

# Execute!
#env.run(until=SIM_TIME)

# End of run
#print('End of run after %d seconds' % SIM_TIME)
