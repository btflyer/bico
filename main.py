import random

import simpy
from compubact import BacterialContext, ComputationalBacterium, event_generator
from messaging import MessageDispatcher

RANDOM_SEED = 42
RT_MEAN = 20.0         # Avg. room temperature
RT_SIGMA = 2.0         # Sigma of room temperature
SIM_TIME = 600  # Simulation time in seconds



############################################################    
# Setup and start the simulation
print('Computation Bacteria colony')
random.seed(RANDOM_SEED)  # This helps reproducing the results

# Create an environment and start the setup process
env = simpy.Environment()
context = BacterialContext(env,20)
event_queue = simpy.FilterStore(env)
env.process(event_generator(env,event_queue,71))

message_dispatcher = MessageDispatcher()

cb_1 = ComputationalBacterium(env,'cb_1','sensor',10,context,event_queue, message_dispatcher)
cb_2 = ComputationalBacterium(env,'cb_2','actuator',10,context,event_queue, message_dispatcher)

# Execute!
env.run(until=SIM_TIME)

# End of run
print('End of run after %d seconds' % SIM_TIME)
