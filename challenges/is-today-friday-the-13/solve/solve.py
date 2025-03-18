import os
import sys
import re
import requests

def solve() -> str:
    url = f"http://{os.environ.get('CHALLENGE_HOST') or 'localhost'}:{os.environ['CHALLENGE_PORT'] or 5000}"

    res = requests.post(f"{url}/is-today-friday-the-13th",
        json={
            "format": "%A%t%d -d 2024-09-13"
        }
    )

    data = res.json()

    return data["msg"]

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
