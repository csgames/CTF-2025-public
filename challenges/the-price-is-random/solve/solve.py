import os
import re
import sys
import typing

import randcrack
import requests

FAIL_RE = re.compile(r"\$(\d+)")
FLAG_RE = re.compile(r"<h5.*?>(.*?)</h5>")


def load_game(sess: requests.Session, url: str) -> None:
    sess.get(f"{url}/play")


def bid(sess: requests.Session, url: str, amount: int) -> typing.Optional[int]:
    res = sess.post(f"{url}/play", data={
        "bid": amount
    })

    match = FAIL_RE.findall(res.text.replace("\n", ""))

    if match:
        return int(match[0])
    else:
        return None


def read_flag(sess: requests.Session, url: str, amount: int) -> str:
    res = sess.post(f"{url}/play", data={
        "bid": amount
    })

    return FLAG_RE.findall(res.text)[0]


def solve() -> str:
    url = f"http://{os.environ.get('CHALLENGE_HOST') or 'localhost'}:{os.environ['CHALLENGE_PORT'] or 5000}"

    sess = requests.Session()
    load_game(sess, url=url)

    rc = randcrack.RandCrack()

    count = 0
    while count < 624:
        value = bid(sess, url=url, amount=0)

        if value:
            count += 1
            rc.submit(value)

    for _ in range(5):
        amount = rc.predict_getrandbits(32)
        bid(sess, url=url, amount=amount)

    return read_flag(sess, url=url, amount=rc.predict_getrandbits(32))


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

