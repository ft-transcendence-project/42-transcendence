import math


class Utils:
    @staticmethod
    def normalize_angle(angle):
        return angle % (2 * math.pi)

    @staticmethod
    def set_direction(ball):
        if math.pi <= ball.angle and ball.angle <= math.pi * 2:
            ball.direction["facing_up"] = True
            ball.direction["facing_down"] = False
        else:
            ball.direction["facing_up"] = False
            ball.direction["facing_down"] = True
        if (math.pi / 2) <= ball.angle and ball.angle <= (math.pi * 3 / 2):
            ball.direction["facing_left"] = True
            ball.direction["facing_right"] = False
        else:
            ball.direction["facing_left"] = False
            ball.direction["facing_right"] = True

        # print("ball.direction_left: ", ball.direction["facing_left"])

    @staticmethod
    def has_collided_with_wall(ball, game_window):
        if (
            (
                ball.y + ball.radius >= game_window.height
                and ball.direction["facing_down"]
            )
            or ball.y - ball.radius <= 0
            and ball.direction["facing_up"]
        ):
            return True
        else:
            return False

    @staticmethod
    def has_collided_with_paddle_left(ball, paddle):
        if (
            (
                ball.x - ball.radius == paddle.width
                and paddle.left_y + paddle.height >= ball.y - ball.radius
                and ball.y + ball.radius >= paddle.left_y
                and ball.direction["facing_left"]
            )
            or (
                ball.x - ball.radius <= paddle.width
                and paddle.left_y + paddle.height / 2 >= ball.y
                and ball.y >= paddle.left_y - ball.radius
                and ball.direction["facing_left"]
            )
            or (
                ball.x - ball.radius <= paddle.width
                and paddle.left_y + paddle.height / 2 <= ball.y
                and ball.y <= paddle.left_y + paddle.height + ball.radius
                and ball.direction["facing_left"]
            )
        ):
            return True
        else:
            return False

    @staticmethod
    def has_collided_with_paddle_right(ball, paddle, game_window):
        if (
            (
                ball.x + ball.radius == game_window.width
                and paddle.right_y <= ball.y
                and ball.y <= paddle.right_y + paddle.height
                and ball.direction["facing_right"]
            )
            or (
                ball.x + ball.radius >= game_window.width - paddle.width
                and paddle.right_y + paddle.height / 2 >= ball.y
                and ball.y >= paddle.right_y - ball.radius
                and ball.direction["facing_right"]
            )
            or (
                ball.x + ball.radius >= game_window.width - paddle.width
                and paddle.right_y + paddle.height / 2 <= ball.y
                and ball.y <= paddle.right_y + paddle.height + ball.radius
                and ball.direction["facing_right"]
            )
        ):
            return True
        else:
            return False

    @staticmethod
    def has_collided_with_paddle_top(ball, paddle, is_left):
        if is_left == True:
            if ball.y <= paddle.left_y + paddle.height / 2:
                return True
            else:
                return False
        else:
            if ball.y <= paddle.right_y + paddle.height / 2:
                return True
            else:
                return False

    @staticmethod
    def update_ball_angle(ball, paddle, is_left, is_top):
        # 左パドルの上部に衝突した時
        if is_left == True and is_top == True:
            collision_distance = (paddle.left_y + paddle.height / 2) - ball.y
            # 左パドルの最上部に衝突したか
            if collision_distance > paddle.height / 2:
                ball.angle = ball.bound_angle.get("left_top")
            else:
                ball.angle = (ball.bound_angle["left_top"] - 2 * math.pi) / (
                    paddle.height / 2
                ) * collision_distance + 2 * math.pi
        # 左パドルの下部に衝突した時
        elif is_left == True and is_top == False:
            collision_distance = ball.y - (paddle.left_y + paddle.height / 2)
            # パドルの最下部に衝突したか
            if collision_distance > paddle.height / 2:
                ball.angle = ball.bound_angle.get("left_bottom")
            else:
                ball.angle = (
                    ball.bound_angle.get("left_bottom")
                    / (paddle.height / 2)
                    * collision_distance
                )
        # 右パドルの上部に衝突した時
        elif is_left == False and is_top == True:
            collision_distance = (paddle.right_y + paddle.height / 2) - ball.y
            # 右パドルの最上部に衝突したか
            if collision_distance > paddle.height / 2:
                ball.angle = ball.bound_angle.get("right_top")
            else:
                ball.angle = (
                    math.pi
                    + (ball.bound_angle["right_top"] - math.pi)
                    / (paddle.height / 2)
                    * collision_distance
                )
        # 右パドルの下部に衝突した時
        else:
            collision_distance = ball.y - (paddle.right_y + paddle.height / 2)
            # 右パドルの最下部に衝突したか
            if collision_distance > paddle.height / 2:
                ball.angle = ball.bound_angle.get("right_bottom")
            else:
                ball.angle = (
                    math.pi
                    - (math.pi - ball.bound_angle["right_bottom"])
                    / (paddle.height / 2)
                    * collision_distance
                )

    @staticmethod
    def adjust_ball_position(ball, paddle, velocity, game_window):
        # 左パドルに衝突しそうかどうか
        if (
            ball.x - ball.radius > paddle.width
            and ball.x + velocity["x"] - ball.radius < paddle.width
            and ball.direction["facing_left"]
        ):
            ball.x = paddle.width + ball.radius
        else:
            ball.x += velocity["x"]
        # 右パドルに衝突しそうかどうか
        if (
            ball.x + ball.radius < game_window.width - paddle.width
            and ball.x + velocity["x"] + ball.radius > game_window.width - paddle.width
            and ball.direction["facing_right"]
        ):
            ball.x = game_window.width - paddle.width - ball.radius
        else:
            ball.y += velocity["y"]
        # 上の壁に衝突しそうかどうか
        if ball.y - ball.radius < 0:
            ball.y = ball.radius
        # 下の壁に衝突しそうかどうか
        if ball.y + ball.radius > game_window.height:
            ball.y = game_window.height - ball.radius

    def update_ball_velocity(is_top, velocity):
        if is_top == True:
            velocity["x"] *= -1
            velocity["y"] = -1 * abs(velocity["y"])
        else:
            velocity["x"] *= -1
            velocity["y"] = abs(velocity["y"])
        return velocity["x"], velocity["y"]

    @staticmethod
    def update_obstacle_position(obstacle, game_window):
        if (
            obstacle.y + obstacle.height + obstacle.velocity <= game_window.height - 100
            and obstacle.y + obstacle.velocity >= 100
        ):
            obstacle.y += obstacle.velocity
        else:
            obstacle.velocity *= -1
