class Reverse:
    """Iterator for looping over a sequence backwards."""
    def __init__(self):
        self.data = list()

    def add(self, data):
        self.data.append(data)
        self.index = len(self.data)

    def __iter__(self):
        return self

    def next(self):
        if self.index == 0:
            raise StopIteration
        self.index = self.index - 1
        return self.data[self.index]


a = Reverse()
a.add('casa')
a.add('sitio')
a.add('fazenda')

for local in a:
    print local
