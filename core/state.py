class State:
    _id = 0

    def __init__(self, name=None):
        if name is None:
            name = f"q{State._id}"
            State._id += 1
        self.name = name

    def __repr__(self):
        return self.name
