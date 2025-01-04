import math


class Utils:
    @staticmethod
    def set_game_setting(pong_info, game_setting):
        ball_size_choise = game_setting.ball_size
        ball_v_choise = game_setting.ball_velocity
        map_choise = game_setting.map
        print(f"map: {map_choise}, ball_size: {ball_size_choise}, ball_v: {ball_v_choise}")
        if ball_size_choise == "big":
            pong_info.ball.radius = 20
        elif ball_size_choise == "normal":
            pong_info.ball.radius = 10
        elif ball_size_choise == "small":
            pong_info.ball.radius = 5
        if ball_v_choise == "fast":
            pong_info.ball.velocity = 7
        elif ball_v_choise == "normal":
            pong_info.ball.velocity = 5
        elif ball_v_choise == "slow":
            pong_info.ball.velocity = 3
        if map_choise == "b":
            pong_info.is_obstacle_exist = True
            pong_info.obstacle1.width = 500
            pong_info.obstacle1.height = 30
            pong_info.obstacle2.width = 500
            pong_info.obstacle2.height = 30
        elif map_choise == "c":
            pong_info.blind.width = 300
            pong_info.blind.height = 600
        print(f"map: {map_choise}, ball_size: {pong_info.ball.radius}, ball_v: {pong_info.ball.velocity}")

    @staticmethod
    def normalize_angle(angle):
        return angle % (2 * math.pi)

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
    def has_collided_with_obstacles_top_or_bottom(ball, obstacle):
        if ((ball.x + ball.radius > obstacle.x and ball.x - ball.radius < obstacle.x + obstacle.width)
            and (ball.y + ball.radius == obstacle.y or ball.y - ball.radius == obstacle.y + obstacle.height)):
            return True
        
    @staticmethod
    def has_collided_with_obstacles_left_or_right(ball, obstacle):
        if ((ball.x + ball.radius == obstacle.x or ball.x - ball.radius == obstacle.x + obstacle.width)
            and ball.y + ball.radius >= obstacle.y and ball.y - ball.radius <= obstacle.y + obstacle.height):
            return True

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
    def adjust_ball_position(ball, paddle, velocity, game_window, obstacle_exist, obstacle1, obstacle2):
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
        # 障害物1に衝突しそうかどうか
        if (obstacle_exist == True):
            if (ball.y + ball.radius > obstacle1.y and ball.y + ball.radius - obstacle1.y <= abs(velocity["y"])
                and ball.x + ball.radius > obstacle1.x and ball.x - ball.radius < obstacle1.x + obstacle1.width
                and ball.direction["facing_down"]):
                ball.y = obstacle1.y - ball.radius
            elif (ball.y - ball.radius < obstacle1.y + obstacle1.height and obstacle1.y + obstacle1.height - ball.y + ball.radius <= abs(velocity["y"])
                  and ball.x + ball.radius > obstacle1.x and ball.x - ball.radius < obstacle1.x + obstacle1.width
                  and ball.direction["facing_up"]):
                ball.y = obstacle1.y + obstacle1.height + ball.radius
            if (ball.y + ball.radius >= obstacle1.y and ball.y - ball.radius <= obstacle1.y + obstacle1.height
                and ball.x + ball.radius > obstacle1.x and ball.x + ball.radius - obstacle1.x <= abs(velocity["x"])
                and ball.direction["facing_right"]):
                ball.x = obstacle1.x - ball.radius
            elif (ball.y + ball.radius >= obstacle1.y and ball.y - ball.radius <= obstacle1.y + obstacle1.height
                  and ball.x - ball.radius < obstacle1.x + obstacle1.width and obstacle1.x + obstacle1.width - ball.x + ball.radius <= abs(velocity["x"])
                  and ball.direction["facing_left"]):
                ball.x = obstacle1.x + obstacle1.width + ball.radius
            # 障害物2に衝突しそうかどうか
            if (ball.y + ball.radius > obstacle2.y and ball.y + ball.radius - obstacle2.y <= abs(velocity["y"])
                and ball.x + ball.radius > obstacle2.x and ball.x - ball.radius < obstacle2.x + obstacle2.width
                and ball.direction["facing_down"]):
                ball.y = obstacle2.y - ball.radius
            elif (ball.y - ball.radius < obstacle2.y + obstacle2.height and obstacle2.y + obstacle2.height - ball.y + ball.radius <= abs(velocity["y"])
                  and ball.x + ball.radius > obstacle2.x and ball.x - ball.radius < obstacle2.x + obstacle2.width
                  and ball.direction["facing_up"]):
                ball.y = obstacle2.y + obstacle2.height + ball.radius
            if (ball.y + ball.radius >= obstacle2.y and ball.y - ball.radius <= obstacle2.y + obstacle2.height
                and ball.x + ball.radius > obstacle2.x and ball.x + ball.radius - obstacle2.x <= abs(velocity["x"])
                and ball.direction["facing_right"]):
                ball.x = obstacle2.x - ball.radius
            elif (ball.y + ball.radius >= obstacle2.y and ball.y - ball.radius <= obstacle2.y + obstacle2.height
                  and ball.x - ball.radius < obstacle2.x + obstacle2.width and obstacle2.x + obstacle2.width - ball.x + ball.radius <= abs(velocity["x"])
                  and ball.direction["facing_left"]):
                ball.x = obstacle2.x + obstacle2.width + ball.radius

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
            obstacle.y + obstacle.height + obstacle.velocity <= game_window.height - 100 and
            obstacle.y + obstacle.velocity >= 100):
            obstacle.y += obstacle.velocity
        else:
            obstacle.velocity *= -1