


class Link:

    def __init__(self, switch_a, port_a, switch_z, port_z):
        if switch_a < switch_z:
            self.switch_a = switch_a
            self.switch_z = switch_z
            self.port_a = int(port_a)
            self.port_z = int(port_z)
        else:
            self.switch_a = switch_z
            self.switch_z = switch_a
            self.port_a = int(port_z)
            self.port_z = int(port_a)

    @property
    def simple(self):
        link = self.switch_a, self.switch_z
        return link

    def __getitem__(self, mid):
        if mid == 0:
            return self.switch_a
        else:
            return self.switch_z

    def __str__(self, full_name=False):
        if full_name:
            side_a = self.switch_a, self.port_a
            side_z = self.switch_z, self.port_z
            link = side_a, side_z
            return str(link)
        link = self.switch_a, self.switch_z
        return str(link)

    def __eq__(self, link):
        if self.switch_a == link.switch_a and self.switch_z == link.switch_z:
            if self.port_a == link.port_a and self.port_z == link.port_z:
                return True
        if self.switch_z == link.switch_a and self.switch_a == link.switch_z:
            if self.port_a == link.port_z and self.port_z == link.port_a:
                return True
        return False
