class TestAPI:
    def __init__(self, variable, name):
        self.name = name
        self.variable = variable

    def __eq__(self, other):
        return self.variable == other.variable

##nothing
