class Obstacle:
    def __init__(self, id):
        self.x = 250
        if id == 1:
            self.y = 135
        elif id == 2:
            self.y = 435
        self.width = 0
        self.height = 0
        self.velocity = 2