import logging

logger = logging.getLogger('ponglogic')

class Paddle:
    def __init__(self):
        self.width = 15
        self.height = 120
        self.left_y = 240
        self.right_y = 240
        self.velocity = 13
        self.left_instruction = { "move_direction": "down",
                                 "action": "stop" }
        self.right_instruction = { "move_direction": "down",
                                  "action": "stop" }
    @staticmethod
    def is_paddle_instruction_valid(paddle_instruction):
        side = paddle_instruction.get("side")
        move_direction = paddle_instruction.get("move_direction")
        action = paddle_instruction.get("action")
        if side in ["left", "right"] and move_direction in ["up", "down"] and action in ["start", "stop"]:
            return True
        logger.error(f"Invalid paddle instruction: {paddle_instruction}")
        return False

    def set_instruction(self, paddle_instruction):
        side = paddle_instruction.get("side")
        move_direction = paddle_instruction.get("move_direction")
        action = paddle_instruction.get("action")

        if Paddle.is_paddle_instruction_valid(paddle_instruction) == False:
            return

        if side == "left":
            self.left_instruction["move_direction"] = move_direction
            self.left_instruction["action"] = action
        else:
            self.right_instruction["move_direction"] = move_direction
            self.right_instruction["action"] = action

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