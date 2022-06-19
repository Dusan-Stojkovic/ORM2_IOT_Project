import json


class TopicMessage:
    def __init__(self, j={}):
        if j['type'] == "register":
            self.type = j['type']
            self.id = j['id']
            self.ip = j['ip']
            self.attributes = j['attributes']
            self.topics = j['topics']
        elif j['type'] == "publish":
            self.type = j['type']
            self.id = j['id']
            self.ip = j['ip']
            self.topic = j['topic']
            self.value = j['value']
            self.value_type = j['value_type']
        elif j['type'] == "subscribe":
            #TODO generate new blocking thread for each one of these topics
            self.type = j['type']
            self.id = j['id']
            self.ip = j['ip']
            self.topic = j['topic']
            

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def __str__(self):
        res = ""
        if self.topic == "register":
            res = "type: {0}, id: {1}, ip: {2}, attrib: {3}, topics: {4}".format(
                    self.type,
                    self.id,
                    self.ip,
                    self.attributes,
                    self.topics)
        elif self.topic == "publish":
            res = "type: {0}, id: {1}, ip: {2}, topics_sub: {3}, value {4}".format(
                    self.type,
                    self.id,
                    self.ip,
                    self.topic,
                    self.value)
        elif self.topic == "subscribe":
            res = "type: {0}, id: {1}, ip: {2}, topic: {3}".format(self.type,
                    self.id,
                    self.ip,
                    self.topic)

        return res


if __name__ == "__main__":
    # serialization test goes here!
    print("Serialization test")
