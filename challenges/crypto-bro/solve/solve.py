import os
import sys

import pwn

FLAG_PREFIX = "flag-"

def solve() -> str:
    sess = pwn.remote(
        host=os.environ.get("CHALLENGE_HOST") or "localhost",
        port=os.environ.get("CHALLENGE_PORT") or 9001
    )

    sess.recvuntil(":")
    sess.sendline(b"\x00" * 128)

    line = sess.recvline().strip()
    hx = line.split(b": ")[-1].decode()
    raw = bytes.fromhex(hx).decode()

    flag = raw[:raw.find(FLAG_PREFIX, 1)]

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
