"""
Prototype implementation for a closed physical space with heat sources

Heat sources warm up the space gradually until it reaches a new equlibirium with
its surroundings. The equilibrium is based on the heat output of active
heat sources at any given time, so, it changes as heat sources come and go.

When heat sources are turned off, the space starts cooling
down towards a lower equilibrium that is a value fixed when creating the space.

Note that the space keeps cooling down even if there are active heat sources
if their combined heat output is not enough to reach the current temperature
of the space (target equilibrium temp is lower than actual current temp).

"""

import simpy

UPDATE_FREQ = 2 # times per minute
SIM_TIME = 2000  # seconds (10 minutes)

class ContainingSpace(object):

        def __init__(self,env,low_eq,start_temp,volume):
            self.env = env
            self.low_equilibrium = low_eq  # Kelvin
            self.temperature = start_temp  # Kelvin
            self.volume = volume           # cubic meter
            self.heat_sources = []
            self.duty_process = env.process(
                self.update((1 / UPDATE_FREQ) * 60)
            ) 

        def update(self,cycle_length): #private
            """The duty cycle: wait for set time, then compute new temperature
            based on heat output level from heat sources during the time passed

            Adding or removing heat sources interrupts the cycle, in which
            case new temperature is set based on time passed and on the
            heat output until the interrupt. A new cycle is started with the
            time remaining from the previous cycle to keep the update period
            constant.
            """
            print('At %s: start of first cycle, temperature: %1.f' %
                  (self.env.now,self.temperature))
            time_to_next_update = cycle_length
            while True:
                try:
                    cycle_start_time = self.env.now
                    print('@Cycle starts at: %s' % cycle_start_time)
                    #record heat ouput and target equilibriums for computing
                    #temperature at the end of this cycle
                    heat_output_at_start = self.current_heat_from_sources()
                    equilibriums_at_start = self.compute_equilibriums()
                    print('Output is %d at: %s' %(heat_output_at_start,cycle_start_time))
                    yield self.env.timeout(time_to_next_update)
                    time_passed = self.env.now - cycle_start_time
                    self.compute_and_set_temperature(
                        equilibriums_at_start,
                        self.cooling_gradient(time_passed),
                        self.warming_gradient(time_passed,heat_output_at_start))
                    print('At %s: temperature is %.1f K' %
                          (self.env.now,self.temperature))
                    time_to_next_update = cycle_length
                except simpy.Interrupt:
                    print('Cycle interrupted at %s' % self.env.now)
                    #calculate and set temperature based on time passed
                    #until now, heat output at the start of this cycle, and
                    #the target equilibriums at the start of this cycle
                    time_passed = self.env.now - cycle_start_time
                    self.compute_and_set_temperature(
                        equilibriums_at_start,
                        self.cooling_gradient(time_passed),
                        self.warming_gradient(time_passed,heat_output_at_start))
                    print('At %s: temperature is %.1f K' %
                          (self.env.now,self.temperature))
                    #the length of the next cycle needs to be adjusted by
                    #subtracting the time passed to keep update frequency constant
                    time_to_next_update = cycle_length - time_passed

        def compute_and_set_temperature(self,eq_target,cooling_gradient,warming_gradient): #private
            print('Equilibrium target: %.1f' % eq_target[1])
            gradient = 0.0 # delta temperature
            #if the current temperature is higher than the target temp, need
            #to apply the cooling gradient (constant)
            if self.temperature > eq_target[1]:
                #make sure we don't go below the target equilibrium
                gradient = min(self.temperature-eq_target[1],
                               cooling_gradient)#self.cooling_gradient(time_span))
                self.temperature -= gradient
            #else if the target temp is higher than the current temp,
            #need to apply warming gradient (depends on heat output)
            elif self.temperature < eq_target[1]:
                #make sure we don't go above the target equilibrium 
                gradient = min(eq_target[1]-self.temperature,
                               warming_gradient)#self.warming_gradient(time_span))
                self.temperature += gradient
            #otherwise current temperature is already at the target temp
            #and there is no need to change it
            if self.temperature < eq_target[0]: #...just to be sure we don't go
                self.temperature = eq_target[0] #below lowest possible temp. 

        def current_heat_from_sources(self): #private
            #total_output = sum(s.heat_output for s in self.heat_sources)
            total_output = sum(s.heat_output for s in self.heat_sources if s.heat_on)
            if total_output is None or total_output < 0:
                total_output = 0
            return total_output
        
        def compute_equilibriums(self): #private
            """Computation of the target temperature is based on the heat output 
            of the active sources and on the volume of the space. The lower
            bound is constant (fixed when the space is created). Returns a tuple
            with the lower bound and the target temperature,
            """
            total_output = self.current_heat_from_sources()
            return (self.low_equilibrium,
                    ((total_output * self.volume / 10000) + self.low_equilibrium))

        def cooling_gradient(self,time_span): #private
            #Cooling rate is constant: 0.1K per minute
            return (time_span / 60 * 0.1) 

        def warming_gradient(self,time_span,total_output): #private
            #result can be negative, if there are no heat sources,
            #(in which case magnitude == cooling gradient)
            if total_output == 0:
                #keep cooling down
                return -self.cooling_gradient(time_span) 
            else:
                print('Warming gradient: %.3f for time span: %s' %
                      ((time_span / 60 * (total_output / 100 * 0.1)),time_span))
                return (time_span / 60 * (total_output / 100 * 0.1))
            
        def add_heat_source(self,heat_source):
            """Add heat_source to active sources"""
            if not heat_source in self.heat_sources:
                self.heat_sources.append(heat_source)
                heat_source.set_listener_callback(self.heat_source_output_changed)
                print('++ Added source %s with output %d' %
                      (heat_source.id,heat_source.heat_output))
                self.duty_process.interrupt()

        def remove_heat_source(self,heat_source):
            """Remove heat_source from active sources"""
            if heat_source in self.heat_sources:
                self.heat_sources.remove(heat_source)
                heat_source.set_listener_callback(None)
                print('-- Removed source %s with output %d' %
                      (heat_source.id,heat_source.heat_output))
                self.duty_process.interrupt()

        def heat_source_output_changed(self,heat_source):
            """React to change in output of heat_source"""
            if heat_source in self.heat_sources:
                if heat_source.heat_on:
                    print('** Source %s changed output to %d' %
                            (heat_source.id,heat_source.heat_output))
                else:
                    print('** Source %s changed output to 0' % (heat_source.id))
                self.duty_process.interrupt()


##class HeatSource(object):
##    """A simple heat source that has a constant heat output"""
##
##    def __init__(self,id,output):
##        self.id = id
##        self.output = output
        
############
## Test code
##
##
##def heat_source_activity(env,space,actions):
##    for action in actions:
##        yield env.timeout(action[0])
##        print('>> Heat source action %s' % action[1])
##        if action[1] is 'add':
##            space.add_heat_source(action[2])
##        elif action[1] is 'remove':
##            space.remove_heat_source(action[2])
##        elif action[1] is 'change':
##            action[2].output = action[3]
##            space.heat_source_output_changed(action[2])
##        else:
##            raise RuntimeError('heat_source_activity(): Unknown action type: %s'
##                               % action[1])           
##
##def test_case_1(env):
##    """Complex test case: 3 heat sources introduced during the scenario and
##    one of them removed later. Initial room temp is 290K with 288K as the
##    low equilibrium.
##    """
##    hs_1 = HeatSource('1',100)
##    hs_2 = HeatSource('2',300)
##    hs_3 = HeatSource('3',200)
##    heat_source_actions = [
##        (100,'add',hs_1),
##        (300,'add',hs_2),
##        (810,'add',hs_3),
##        (90,'remove',hs_1)
##    ]                
##    room = ContainingSpace(env,288,290,(5*5*3))
##    env.process(heat_source_activity(env,room,heat_source_actions))
##    # Execute!
##    print('==== Start of test_case_1 ====')
##    env.run(until=SIM_TIME)
##    # End of run
##    print('#### End of test_case_1 after %d seconds ####' % SIM_TIME)
##
##def test_case_2(env):
##    """No heat sources, room starts at 290K with 288K as the low equilibrium
##    """
##    room = ContainingSpace(env,288,290,(5*5*3))
##    # Execute!
##    print('==== Start of test_case_2 ====')
##    env.run(until=SIM_TIME)
##    # End of run
##    print('#### End of test_case_2 after %d seconds ####' % SIM_TIME)
##
##def test_case_3(env):
##    """One heat source introduced after 200 seconds, initial room temp is 290K
##    with low eq at 288K
##    """
##    hs_1 = HeatSource('1',300)
##    heat_source_actions = [
##        (200,'add',hs_1)
##    ]                
##    room = ContainingSpace(env,288,290,(5*5*3))
##    env.process(heat_source_activity(env,room,heat_source_actions))
##    # Execute!
##    print('==== Start of test_case_3 ====')
##    env.run(until=SIM_TIME)
##    # End of run
##    print('#### End of test_case_3 after %d seconds ####' % SIM_TIME)
##    
##def test_case_4(env):
##    """One heat source introduced after 200 seconds, initial room temp is 290K
##    with low eq at 288K, heat source removed after 400 seconds
##    """
##    hs_1 = HeatSource('1',300)
##    heat_source_actions = [
##        (200,'add',hs_1),
##        (400,'remove',hs_1)
##    ]                
##    room = ContainingSpace(env,288,290,(5*5*3))
##    env.process(heat_source_activity(env,room,heat_source_actions))
##    # Execute!
##    print('==== Start of test_case_4 ====')
##    env.run(until=SIM_TIME)
##    # End of run
##    print('#### End of test_case_4 after %d seconds ####' % SIM_TIME)
##
##def test_case_5(env):
##    """One heat source introduced after 200 seconds, initial room temp is 290K
##    with low eq at 288K, heat source output doubled after 400 seconds
##    """
##    hs_1 = HeatSource('1',300)
##    heat_source_actions = [
##        (200,'add',hs_1),
##        (400,'change',hs_1,600),
##        (400,'change',hs_1,200)
##    ]                
##    room = ContainedSpace(env,288,290,(5*5*3))
##    env.process(heat_source_activity(env,room,heat_source_actions))
##    # Execute!
##    print('==== Start of test_case_5 ====')
##    env.run(until=SIM_TIME)
##    # End of run
##    print('#### End of test_case_5 after %d seconds ####' % SIM_TIME)
##
#### run test cases
##env = simpy.Environment()
##test_case_1(env)
##
##env = simpy.Environment()
##test_case_2(env)
##
##env = simpy.Environment()
##test_case_3(env)
##
##env = simpy.Environment()
##test_case_4(env)
##
##env = simpy.Environment()
##test_case_5(env)
