import json


class TopicMessage:
    def __init__(self, j={}, alive=True):
        if j == {}:
            self.id = 0
            self.ip = '127.0.0.1'
            self.manual = True
            self.actuators = []
            self.sensors = []
            self.keep_alive = alive
        else:
            self.id = j['id']
            self.ip = j['ip']
            self.manual = j['manual']
            self.actuators = j['actuators']
            self.sensors = j['sensors']
            self.keep_alive = True

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def __str__(self):
        res = "id: {0}\nip: {1}\nmanual: {2}\nactuators: {3}\nsensors: {4}\n".format(
            self.id, self.ip, self.manual, self.actuators, self.sensors)
        return res


if __name__ == "__main__":
    # serialization test goes here!
    print("Serialization test")
