import logging
import math

logger = logging.getLogger("ponglogic")


class Utils:
    @staticmethod
    def set_game_setting(pong_info, game_setting):
        ball_size_choise = game_setting.ball_size
        ball_v_choise = game_setting.ball_velocity
        map_choise = game_setting.map
        logger.info(
            f"map: {map_choise}, ball_size: {ball_size_choise}, ball_v: {ball_v_choise}"
        )
        if ball_size_choise == "big":
            pong_info.ball.radius = pong_info.ball.BIG_RADIUS
        elif ball_size_choise == "normal":
            pong_info.ball.radius = pong_info.ball.NORMAL_RADIUS
        elif ball_size_choise == "small":
            pong_info.ball.radius = pong_info.ball.SMALL_RADIUS
        if ball_v_choise == "fast":
            pong_info.ball.velocity = pong_info.ball.FAST_VELOCITY
        elif ball_v_choise == "normal":
            pong_info.ball.velocity = pong_info.ball.NORMAL_VELOCITY
        elif ball_v_choise == "slow":
            pong_info.ball.velocity = pong_info.ball.SLOW_VELOCITY
        if map_choise == "b":
            pong_info.is_obstacle_exist = True
            pong_info.obstacle1.width = 500
            pong_info.obstacle1.height = 30
            pong_info.obstacle2.width = 500
            pong_info.obstacle2.height = 30
        elif map_choise == "c":
            pong_info.blind.width = 300
            pong_info.blind.height = 600
        logger.info(
            f"map: {map_choise}, ball_size: {pong_info.ball.radius}, ball_v: {pong_info.ball.velocity}"
        )

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
    def walls_collision(ball_velocity, pong_info):
        if Utils.has_collided_with_wall(pong_info.ball, pong_info.game_window) == True:
            ball_velocity["y"] *= -1
            pong_info.ball.angle = 2 * math.pi - pong_info.ball.angle
            pong_info.ball.angle = Utils.normalize_angle(pong_info.ball.angle)
            pong_info.ball.set_direction()

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
    def left_paddle_collision(ball_velocity, pong_info):
        if (
            Utils.has_collided_with_paddle_left(pong_info.ball, pong_info.paddle)
            == True
        ):
            is_left = True
            # 左パドル上部の衝突判定
            if (
                Utils.has_collided_with_paddle_top(
                    pong_info.ball, pong_info.paddle, is_left
                )
                == True
            ):
                is_top = True
            else:
                is_top = False
            Utils.update_ball_angle(pong_info.ball, pong_info.paddle, is_left, is_top)
            ball_velocity["x"], ball_velocity["y"] = Utils.update_ball_velocity(
                is_top, ball_velocity
            )

    @staticmethod
    def right_paddle_collision(ball_velocity, pong_info):
        # 右パドル衝突判定
        if (
            Utils.has_collided_with_paddle_right(
                pong_info.ball, pong_info.paddle, pong_info.game_window
            )
            == True
        ):
            is_left = False
            # 右パドル上部衝突判定
            if (
                Utils.has_collided_with_paddle_top(
                    pong_info.ball, pong_info.paddle, is_left
                )
                == True
            ):
                is_top = True
            else:
                is_top = False
            Utils.update_ball_angle(pong_info.ball, pong_info.paddle, is_left, is_top)
            ball_velocity["x"], ball_velocity["y"] = Utils.update_ball_velocity(
                is_top, ball_velocity
            )

    @staticmethod
    def paddles_collision(ball_velocity, pong_info):
        Utils.left_paddle_collision(ball_velocity, pong_info)
        Utils.right_paddle_collision(ball_velocity, pong_info)

    @staticmethod
    def has_collided_with_obstacle_top_or_bottom(ball, obstacle):
        if (
            ball.x + ball.radius > obstacle.x
            and ball.x - ball.radius < obstacle.x + obstacle.width
        ) and (
            ball.y + ball.radius == obstacle.y
            or ball.y - ball.radius == obstacle.y + obstacle.height
        ):
            return True

    @staticmethod
    def has_collided_with_obstacle_left_or_right(ball, obstacle):
        if (
            (
                ball.x + ball.radius == obstacle.x
                or ball.x - ball.radius == obstacle.x + obstacle.width
            )
            and ball.y + ball.radius >= obstacle.y
            and ball.y - ball.radius <= obstacle.y + obstacle.height
        ):
            return True

    @staticmethod
    def obstacles_collision(ball_velocity, pong_info):
        if pong_info.is_obstacle_exist == True:
            if (
                Utils.has_collided_with_obstacle_top_or_bottom(
                    pong_info.ball, pong_info.obstacle1
                )
                == True
                or Utils.has_collided_with_obstacle_top_or_bottom(
                    pong_info.ball, pong_info.obstacle2
                )
                == True
            ):
                ball_velocity["y"] *= -1
                pong_info.ball.angle = 2 * math.pi - pong_info.ball.angle
                pong_info.ball.angle = Utils.normalize_angle(pong_info.ball.angle)
                pong_info.ball.set_direction()
            if (
                Utils.has_collided_with_obstacle_left_or_right(
                    pong_info.ball, pong_info.obstacle1
                )
                == True
                or Utils.has_collided_with_obstacle_left_or_right(
                    pong_info.ball, pong_info.obstacle2
                )
                == True
            ):
                ball_velocity["x"] *= -1
                pong_info.ball.angle = math.pi - pong_info.ball.angle
                pong_info.ball.angle = Utils.normalize_angle(pong_info.ball.angle)
                pong_info.ball.set_direction()

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
    def adjust_ball_position(
        ball, paddle, velocity, game_window, obstacle_exist, obstacle1, obstacle2
    ):
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
        if obstacle_exist == True:
            if (
                ball.y + ball.radius > obstacle1.y
                and ball.y + ball.radius - obstacle1.y <= abs(velocity["y"])
                and ball.x + ball.radius > obstacle1.x
                and ball.x - ball.radius < obstacle1.x + obstacle1.width
                and ball.direction["facing_down"]
            ):
                ball.y = obstacle1.y - ball.radius
            elif (
                ball.y - ball.radius < obstacle1.y + obstacle1.height
                and obstacle1.y + obstacle1.height - ball.y + ball.radius
                <= abs(velocity["y"])
                and ball.x + ball.radius > obstacle1.x
                and ball.x - ball.radius < obstacle1.x + obstacle1.width
                and ball.direction["facing_up"]
            ):
                ball.y = obstacle1.y + obstacle1.height + ball.radius
            if (
                ball.y + ball.radius >= obstacle1.y
                and ball.y - ball.radius <= obstacle1.y + obstacle1.height
                and ball.x + ball.radius > obstacle1.x
                and ball.x + ball.radius - obstacle1.x <= abs(velocity["x"])
                and ball.direction["facing_right"]
            ):
                ball.x = obstacle1.x - ball.radius
            elif (
                ball.y + ball.radius >= obstacle1.y
                and ball.y - ball.radius <= obstacle1.y + obstacle1.height
                and ball.x - ball.radius < obstacle1.x + obstacle1.width
                and obstacle1.x + obstacle1.width - ball.x + ball.radius
                <= abs(velocity["x"])
                and ball.direction["facing_left"]
            ):
                ball.x = obstacle1.x + obstacle1.width + ball.radius
            # 障害物2に衝突しそうかどうか
            if (
                ball.y + ball.radius > obstacle2.y
                and ball.y + ball.radius - obstacle2.y <= abs(velocity["y"])
                and ball.x + ball.radius > obstacle2.x
                and ball.x - ball.radius < obstacle2.x + obstacle2.width
                and ball.direction["facing_down"]
            ):
                ball.y = obstacle2.y - ball.radius
            elif (
                ball.y - ball.radius < obstacle2.y + obstacle2.height
                and obstacle2.y + obstacle2.height - ball.y + ball.radius
                <= abs(velocity["y"])
                and ball.x + ball.radius > obstacle2.x
                and ball.x - ball.radius < obstacle2.x + obstacle2.width
                and ball.direction["facing_up"]
            ):
                ball.y = obstacle2.y + obstacle2.height + ball.radius
            if (
                ball.y + ball.radius >= obstacle2.y
                and ball.y - ball.radius <= obstacle2.y + obstacle2.height
                and ball.x + ball.radius > obstacle2.x
                and ball.x + ball.radius - obstacle2.x <= abs(velocity["x"])
                and ball.direction["facing_right"]
            ):
                ball.x = obstacle2.x - ball.radius
            elif (
                ball.y + ball.radius >= obstacle2.y
                and ball.y - ball.radius <= obstacle2.y + obstacle2.height
                and ball.x - ball.radius < obstacle2.x + obstacle2.width
                and obstacle2.x + obstacle2.width - ball.x + ball.radius
                <= abs(velocity["x"])
                and ball.direction["facing_left"]
            ):
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
    def generate_pong_data(pong_info, first):
        pong_data = {
            "id": pong_info.setting_id,
            "left_paddle_y": pong_info.paddle.left_y,
            "right_paddle_y": pong_info.paddle.right_y,
            "ball_x": pong_info.ball.x,
            "ball_y": pong_info.ball.y,
            "ball_radius": pong_info.ball.radius,
            "left_score": pong_info.score.left,
            "right_score": pong_info.score.right,
        }
        if first:
            pong_data.update(
                {
                    "obstacle1_x": pong_info.obstacle1.x,
                    "obstacle1_y": pong_info.obstacle1.y,
                    "obstacle1_width": pong_info.obstacle1.width,
                    "obstacle1_height": pong_info.obstacle1.height,
                    "obstacle2_x": pong_info.obstacle2.x,
                    "obstacle2_y": pong_info.obstacle2.y,
                    "obstacle2_width": pong_info.obstacle2.width,
                    "obstacle2_height": pong_info.obstacle2.height,
                    "blind_x": pong_info.blind.x,
                    "blind_y": pong_info.blind.y,
                    "blind_width": pong_info.blind.width,
                    "blind_height": pong_info.blind.height,
                }
            )
        return pong_data

    @staticmethod
    def generate_game_over_message(pong_info, message):
        game_over_message = {
            "type": message,
            "winner": pong_info.winner,
            "left_score": pong_info.score.left,
            "right_score": pong_info.score.right,
        }
        return game_over_message
