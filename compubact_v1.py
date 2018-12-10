# Print Your code here
print('Hello in console window')

def compbact(env,id,queue,event_type,interval):
    filter = lambda ev: ev[1] == event_type # event filter function
    while True:
        print('%s starts sleeping at %.1f' % (id,env.now))
        yield env.timeout(interval)

        print('%s checks event queue at %.1f' % (id,env.now))
        event = yield queue.get(filter)
        print('%s processes event %s of %s at %.1f' % \
              (id,event[0],event[1],env.now) )
        processing_time = 0.5
        yield env.timeout(processing_time)

def eventsource(env,id,queue,interval):
    event_no = 0
    while True:
        event_no = event_no + 1
        if ((event_no % 2) == 1):
            event = (event_no,'A')
        else:
            event = (event_no,'B')
        print('%s enqueues event %d of %s at %.1f' % \
              (id,event[0],event[1],env.now))
        yield queue.put(event)
        
        print('%s sleeps at %.1f' % (id,env.now))
        yield env.timeout(interval)
        
import simpy
env = simpy.Environment()
event_queue = simpy.FilterStore(env)
env.process(compbact(env,'001',event_queue,'A',5))
env.process(compbact(env,'002',event_queue,'B',3))
env.process(eventsource(env,'source',event_queue,2))

env.run(until=20)