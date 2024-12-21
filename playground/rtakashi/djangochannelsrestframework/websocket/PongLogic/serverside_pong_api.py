from .shared import SharedState
from websocket.models import GameState
from websocket.serializers import GameStateSerializer
import asyncio
from asgiref.sync import sync_to_async

async def move_paddle(action, content):
    player = content.get("player")
    if action == "move_up":
        if player == "right":
            SharedState.Paddle.right_y -= 3
        elif player == "left":
            SharedState.Paddle.left_y -= 3
    elif action == "move_down":
        if player == "right":
            SharedState.Paddle.right_y += 3
        elif player == "left":
            SharedState.Paddle.left_y += 3
    game_state = await set_game_state("playing")
    return game_state


async def init_game():
    SharedState.init()
    game_state = await set_game_state("waiting")
    return game_state

async def pause_game():
    if "game_loop" in SharedState.tasks:
        SharedState.tasks["game_loop"].cancel()
    game_state = await set_game_state("pause")
    return game_state

async def resume_game():
    if "game_loop" in SharedState.tasks:
        SharedState.tasks["game_loop"].cancel()
        from .consumers import PongLogic
        pong_logic = PongLogic()
        SharedState.tasks["game_loop"] = asyncio.create_task(pong_logic.game_loop())
    game_state = await set_game_state("playing")
    return game_state

async def set_game_state(state):
    game_state = await sync_to_async(GameState.objects.first)()
    if game_state:
        game_state.state=state
        game_state.r_player=SharedState.Paddle.right_y
        game_state.l_player=SharedState.Paddle.left_y
        game_state.ball_x=SharedState.Ball.x
        game_state.ball_y=SharedState.Ball.y
        game_state.r_score=SharedState.Score.right
        game_state.l_score=SharedState.Score.left
        await sync_to_async(game_state.save)()
    else:
        game_state = await sync_to_async(GameState.objects.create)(
            state=state,
            r_player=SharedState.Paddle.right_y,
            l_player=SharedState.Paddle.left_y,
            ball_x=SharedState.Ball.x,
            ball_y=SharedState.Ball.y,
            r_score=SharedState.Score.right,
            l_score=SharedState.Score.left
        )
    return game_state
