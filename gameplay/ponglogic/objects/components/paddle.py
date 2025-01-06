class Paddle:
    def __init__(self):
        self.width = 15
        self.height = 120
        self.left_y = 240
        self.right_y = 240
        self.velocity = 3
        self.left_instruction = { "move_direction": "down",
                                 "action": "stop" }
        self.right_instruction = { "move_direction": "down",
                                  "action": "stop" }

    def set_instruction(self, data):
        side = data.get("side")
        if side == "left":
            self.left_instruction["move_direction"] = data.get("move_direction")
            self.left_instruction["action"] = data.get("action")
        else:
            self.right_instruction["move_direction"] = data.get("move_direction")
            self.right_instruction["action"] = data.get("action")

    def update_position(self, game_window):
        if self.left_instruction["action"] == "start":
            if self.left_instruction["move_direction"] == "up":
                self.left_y -= self.velocity
                if self.left_y < 0:
                    self.left_y = 0
            else:
                self.left_y += self.velocity
                if self.left_y + self.height > game_window.height:
                    self.left_y = game_window.height - self.height

        if self.right_instruction["action"] == "start":
            if self.right_instruction["move_direction"] == "up":
                self.right_y -= self.velocity
                if self.right_y < 0:
                    self.right_y = 0
            else:
                self.right_y += self.velocity
                if self.right_y + self.height > game_window.height:
                    self.right_y = game_window.height - self.height