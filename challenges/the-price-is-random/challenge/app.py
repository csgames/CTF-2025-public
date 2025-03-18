import dataclasses
import json
import os
import random
import threading
import uuid

import flask

#############
# Constants #
#############

MAX_PLAY = 10
MIN_WIN = 5

PRIZE_POOL_SIZE = 1024

########
# Game #
########

@dataclasses.dataclass
class Game:
    play: int = dataclasses.field(default=0)
    win: int = dataclasses.field(default=0)

    current: int = dataclasses.field(default=0)
    prizes: list[int] = dataclasses.field(default_factory=list)

    lock: threading.Lock = dataclasses.field(default_factory=lambda: threading.Lock())

    def __post_init__(self) -> None:
        self.next_prizes()

    def next_round(self) -> None:
        self.play = 0
        self.win = 0

    def next_prizes(self) -> None:
        self.prizes = [random.getrandbits(32) for _ in range(PRIZE_POOL_SIZE)]

def init_app():
    # App
    app = flask.Flask(__name__)
    app.secret_key = os.environ.get("SECRET_KEY") or "SECRET_KEY"

    # App contants
    PRIZES = json.load(open("prizes.json"))
    FLAG = os.environ.get("FLAG") or "FLAG"

    # Game database
    GAMES: dict[str, Game] = {}

    @app.route("/")
    def home():
        return flask.render_template("home.jinja2")

    @app.route("/play", methods=["GET", "POST"])
    def play():
        nonlocal GAMES

        # Create a new session
        if "game_id" not in flask.session:
            flask.session["game_id"] = str(uuid.uuid4())

        # Get/create a new game
        if flask.session["game_id"] in GAMES:
            game = GAMES[flask.session["game_id"]]
        else:
            game = GAMES[flask.session["game_id"]] = Game()

        with game.lock:
            # If player lost the round -> Game Over
            if game.play >= MAX_PLAY:
                game.next_round()

                return flask.render_template("game_over.jinja2")

            # Pick a random prize
            prize_id = random.randint(0, len(PRIZES) - 1)
            prize = PRIZES[prize_id]

            # Show next prize if no bid is placed
            if flask.request.method == "GET":
                return flask.render_template("play.jinja2", **prize)

            # Get player bid
            try:
                bid = int(flask.request.form["bid"])
            except:
                bid = 0

            # Get prize value
            prize_price = game.prizes[game.current]

            # Update play and next prize
            game.play += 1
            game.current += 1

            if game.current >= PRIZE_POOL_SIZE:
                game.next_prizes()

            # If bid != prize -> Lose
            if bid != prize_price:
                return flask.render_template("play.jinja2", status=2, price=prize_price, **prize)

            # If bid == prize -> Win
            game.win += 1

            if game.win >= MIN_WIN:
                # If player won many times in a round -> Flag
                return flask.render_template("flag.jinja2", flag=FLAG)
            else:
                # Otherwise -> Continue winning
                return flask.render_template("play.jinja2", status=1, **prize)

    return app

if __name__ == "__main__":
    init_app().run(
        host="0.0.0.0",
        debug=os.environ.get("DEBUG") or False
    )
