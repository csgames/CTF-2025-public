import argparse
import curses
import dataclasses
import enum
import json
import queue
import string
import threading
import time
import typing
import uuid

import websockets.sync.client

ALPHABET = set(string.ascii_letters + string.digits + """!"#$%&'()*+,-./<=>?@[\\]^_`{|}~ """)

@dataclasses.dataclass
class Player:
    name: str
    x: int
    y: int

class Direction(enum.Enum):
    UP = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 3

class ColorPair(enum.Enum):
    PLAYER = 1
    FLAG = 2

class Client:
    MAP_DIMENSION = 16

    def __init__(self, socket: websockets.sync.client.ClientConnection):
        self._players: typing.List[Player] = []
        self._map: str = " " * (Client.MAP_DIMENSION * Client.MAP_DIMENSION)
        self._messages: typing.List[str] = []
        self._pickup: str = ""
        self._input = ""
        self._input_mode = False
        self._socket = socket

    def __str__(self) -> str:
        return f"Client(players={self.players}, pickup={self._pickup}, messages={self.messages})"

    @property
    def players(self) -> typing.List[Player]:
        return self._players

    @property
    def map(self) -> str:
        return self._map
    
    @property
    def messages(self) -> typing.List[str]:
        return self._messages

    def handle_message(self, message: typing.Mapping[str, typing.Any]) -> None:
        if message["type"] == "init":
            self._players = [Player(name, x, y) for name, x, y in message["data"]["players"]]
            self._map = message["data"]["map"]
            self._messages = message["data"]["messages"]
        elif message["type"] == "players":
            self._players = [Player(name, x, y) for name, x, y in message["data"]["players"]]
        elif message["type"] == "message":
            self._messages.append(message["data"]["text"])
        elif message["type"] == "pickup":
            self._map = message["data"]["map"]
            self._pickup = message["data"]["text"] or "Nothing here..."

    def handle_input(self, c: str) -> None:
        if self._pickup:
            self._pickup = ""

        if self._input_mode:
            if c == "\n":
                self.message(self._input)

                self._input = ""
                self._input_mode = False
            elif c == "KEY_BACKSPACE":
                self._input = self._input[:-1]
            elif c == ":" or c == ";":
                self._input_mode = False
            if c in ALPHABET:
                self._input = self._input + c
        else:
            if c == "KEY_UP" or c == "w":
                self.move(Direction.UP)
            elif c == "KEY_DOWN" or c == "s":
                self.move(Direction.DOWN)
            elif c == "KEY_LEFT" or c == "a":
                self.move(Direction.LEFT)
            elif c == "KEY_RIGHT" or c == "d":
                self.move(Direction.RIGHT)
            elif c == " " or c == "e":
                self.pickup()
            elif c == ":" or c == ";":
                self._input_mode = True

    def __draw_map(self, window: "curses._CursesWindow") -> None:
        for y in range(Client.MAP_DIMENSION):
            for x in range(Client.MAP_DIMENSION):
                c = self.map[y * Client.MAP_DIMENSION + x]

                if c == "~":
                    color_pair = curses.color_pair(ColorPair.FLAG.value)
                else:
                    color_pair = 0

                window.addch(y + 1, x + 1, c, color_pair)

        for p in self.players:
            window.addch(p.y + 1, p.x + 1, "X", curses.color_pair(ColorPair.PLAYER.value))

        window.border()
        window.refresh()

    def __draw_messages(self, window: "curses._CursesWindow") -> None:
        window.clear()

        max_y, _ = window.getmaxyx()

        for y, m in enumerate(self.messages[-(max_y - 2):]):
            if ":" in m:
                user, content = m[:m.index(":")], m[m.index(":")+1:]
                
                window.addstr(y + 1, 1, user, curses.color_pair(ColorPair.PLAYER.value))
                window.addstr(y + 1, 1 + len(user), f" > {content}")
            else:
                window.addstr(y + 1, 1, m)

        window.border()
        window.refresh()

    def __draw_input(self, window: "curses._CursesWindow") -> None:
        if not self._input_mode:
            return

        window.addstr(1, 1, self._input.ljust(68))
        window.border()
        window.refresh()

    def __draw_pickup(self, window: "curses._CursesWindow") -> None:
        window.clear()

        if self._pickup:
            window.addstr(1, 1, self._pickup)
            window.border()

        window.refresh()

    def draw(self, map_window: "curses._CursesWindow", message_window: "curses._CursesWindow", input_window: "curses._CursesWindow", pickup_window: "curses._CursesWindow") -> None:
        self.__draw_map(map_window)
        self.__draw_messages(message_window)
        self.__draw_input(input_window)
        self.__draw_pickup(pickup_window)

    def message(self, message: str) -> None:
        self._socket.send(json.dumps({
            "type": "message",
            "data": {
                "text": message
            }
        }))

    def move(self, direction: Direction) -> None:
        self._socket.send(json.dumps({
            "type": "move",
            "data": {
                "direction": direction.value
            }
        }))

    def pickup(self) -> None:
        self._socket.send(json.dumps({
            "type": "pickup"
        }))

def main(stdscr: typing.Optional["curses._CursesWindow"], host: str, port: int, name: str, game_id: str, callback: typing.Optional[typing.Callable[[Client], bool]] = None) -> None:
    ws = websockets.sync.client.connect(f"ws://{host}:{port}/?name={name}&gameId={game_id}")
    client = Client(ws)

    map_window, message_window, input_window, pickup_window = [None] * 4
    input_offset = [Client.MAP_DIMENSION + 4, Client.MAP_DIMENSION]
    if stdscr:
        curses.init_pair(ColorPair.PLAYER.value, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(ColorPair.FLAG.value, curses.COLOR_YELLOW, curses.COLOR_BLACK)

        map_window = curses.newwin(Client.MAP_DIMENSION + 2, Client.MAP_DIMENSION + 2, 1, 1)
        message_window = curses.newwin(Client.MAP_DIMENSION + 2, Client.MAP_DIMENSION + 51, 1, Client.MAP_DIMENSION + 4)
        input_window = curses.newwin(3, Client.MAP_DIMENSION + 51, input_offset[1], input_offset[0])
        pickup_window = curses.newwin(3, Client.MAP_DIMENSION + 70, Client.MAP_DIMENSION + 3, 1)

        stdscr.nodelay(True)
        stdscr.clear()
        stdscr.refresh()

    message_queue = queue.Queue()
    def handle_messages():
        while True:
            try:
                message_queue.put(json.loads(ws.recv()))
            except websockets.exceptions.ConnectionClosedOK:
                break

    message_thread = threading.Thread(target=handle_messages)
    message_thread.start()

    update = False
    while True:
        while not message_queue.empty():
            message = message_queue.get_nowait()
            client.handle_message(message)
            update = True

        if update and stdscr:
            update = False
            client.draw(
                map_window,
                message_window,
                input_window,
                pickup_window
            )
            stdscr.refresh()

        if stdscr:
            try:
                if client._input_mode:
                    c = stdscr.getkey(input_offset[1] + 1, input_offset[0] + 1 + min(len(client._input),  64))
                else:
                    c = stdscr.getkey(0, 0)
                
                client.handle_input(c)

                update = True
            except KeyboardInterrupt:
                break
            except Exception as e:
                if "no input" not in str(e):
                    raise e
        elif update:
            if not callback(client):
                break

            time.sleep(0.1)

    ws.close()

def cli() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument("--host", default="localhost", help="Game server domain (ex: game.server.com)")
    parser.add_argument("--port", type=int, default=3000, help="Game port (ex: 1234)")
    parser.add_argument("--game_id", default=None, help="Game lobby ID (ex: b35t_r00m)")
    parser.add_argument("--name", default="USER", help="In-game username (ex: 1337_h4x0r)")

    args = parser.parse_args()

    curses.wrapper(
        main,
        host=args.host,
        port=args.port,
        name=args.name,
        game_id=args.game_id or str(uuid.uuid4())
    )

if __name__ == "__main__":
    cli()
