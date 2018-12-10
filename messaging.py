
class MessageDispatcher:

    def __init__(self):
        self._bacteria = []
        self.message_uid = 1
    def broadcast(self, message):
        message.uid = self.message_uid
        #print('-- {} Broad casting for agent# {}'.format(message.uid, message.sender.uid))
        self.message_uid += 1

        for bacterium in self._bacteria:
            if bacterium is not message.sender:
                bacterium.receive(message)

    def register(self, bacterium):
        self._bacteria.append(bacterium)

    def unregister(self, bacterium):
        self._bacteria.remove(bacterium)


class Message:
    def __init__(self, sender):#, points, points_info):# position_of, x, y):
        self.sender = sender
        #self.uid = 0
        #self.position_of = position_of
        #self.x = x
        #self.y = y
        #self.points = points
        #self.points_info = points_info



