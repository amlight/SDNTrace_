from libs.core.singleton import Singleton


class Links:

    __metaclass__ = Singleton

    def __init__(self):
        self.links = []

    def check_if_exist(self, new_link):
        existing = False
        for link in self.links:
            if new_link == link:
                existing = True
        return existing

    def add_link(self, new_link):
        if not self.check_if_exist(new_link):
            self.links.append(new_link)
            print("New Link Detected: %s:%s - %s:%s" %
                  (new_link.switch_a, new_link.port_a,
                   new_link.switch_z, new_link.port_z))

    @property
    def simple(self):
        new_list = []
        for link in self.links:
            new_link = link.switch_a, link.switch_z
            new_list.append(new_link)
        return new_list

    def remove_switch(self, switch):
        for link in self.links:
            if link.switch_a == switch or link.switch_z == switch:
                self.links.remove(link)

    def __str__(self):
        string = ""
        for link in self.links:
            if link is not None:
                string += str(link)
        return string

    def __len__(self):
        return len(self.links)
