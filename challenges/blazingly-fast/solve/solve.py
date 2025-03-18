import os
import re
import sys
import typing

from client import main, Client, Direction

PATH = (
    [Direction.UP] * 3 
    + [Direction.LEFT] 
    + [Direction.UP] * 3 
    + [Direction.LEFT] 
    + [Direction.UP] * 7 
    + [Direction.LEFT] * 11 
    + [Direction.UP, Direction.LEFT, Direction.UP, Direction.LEFT]
) 

ACTIONS = (
    [("x", "~" * 64)] * 16
    + [("m", d) for d in PATH]
    + [("p", None), ("f", None)]
)

def solve() -> typing.Optional[str]:
    i = 0
    flag = None
    def callback(c: Client) -> bool:
        nonlocal i, flag

        command, arg = ACTIONS[i]

        if command == "x":
            c.message(arg)
        elif command == "m":
            c.move(arg)
        elif command == "p":
            c.pickup()
        elif command == "f":
            flag = c._pickup

        i += 1
        return i < len(ACTIONS)

    main(
        host=os.environ["CHALLENGE_HOST"],
        port=int(os.environ["CHALLENGE_PORT"]),
        name="solve",
        game_id=0,
        stdscr=None,
        callback=callback
    )

    return flag


def cli() -> int:
    if (solution := solve()) is None:
        return 1

    if not (flag := os.environ.get("FLAG")):
        return 0

    if os.environ.get("FLAG_TYPE") == "regex":
        is_ok = re.match(flag, solution)
    else:
        is_ok = solution == flag

    if not is_ok:
        print(f"FAIL: {solution}", file=sys.stderr)

    return 0 if is_ok else 1


if __name__ == "__main__":
    exit(cli())
