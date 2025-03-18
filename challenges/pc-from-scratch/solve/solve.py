import io
import os
import os.path
import re
import sys
import typing

import pwn

from pfs.asm import PFSASM
from pfs.emu import PFSEMU


REL_PATH = os.path.abspath(os.path.dirname(__file__))


def flag0(build_path: str) -> str:
    with open(os.path.join(build_path, "0", "challenge.sx")) as h:
        rom = [int(v) for v in h.read().split(" ")]

    emu = PFSEMU(rom, output=False)

    while emu.step():
        pass

    return emu.output.buffer.strip()


def flag1(build_path: str) -> str:
    with open(os.path.join(build_path, "1", "challenge.sx")) as h:
        rom = [int(v) for v in h.read().split(" ")]

    emu = PFSEMU(rom, output=False)

    # Write canary.
    emu.ram.data[128] = 1337

    while emu.step():
        # Catch the program overwriting memory.
        if emu.ram.data[128] != 1337:
            break

    # Read flag in memory
    return bytes(emu.ram.data[512:]).split(b"\0")[0].decode()


def flag2(build_path: str) -> str:
    with open(os.path.join(build_path, "2", "challenge.sx")) as h:
        rom = [int(v) for v in h.read().split(" ")]

    with open(os.path.join(build_path, "2", "output")) as h:
        output = h.read().strip()

    # RSA public key
    e = rom[3]
    n_size = rom[4]
    n = int.from_bytes(rom[5:5+n_size], "little")

    # Find factors on https://factordb.com/
    p = 669711457553
    q = 700596383621

    assert n % p == 0
    assert n % q == 0

    # RSA private key
    phi_n = (p - 1) * (q - 1)
    d = pow(e, -1, phi_n)

    # RSA decrypt
    c = int.from_bytes(bytes.fromhex(output), "little")

    m = pow(c, d, n)

    return m.to_bytes(32, "little").rstrip(b"\0").decode()


def flag3(host: str = "localhost", port: int = 9001) -> str:
    # Assemble solution
    sx_file = io.StringIO()
    with open(os.path.join(REL_PATH, "3", "solve.sm")) as h:
        PFSASM(keep_ram=True).asm(h, sx_file)

    sx_file.seek(0)
    sx = sx_file.read()

    # Connect to test server
    sess = pwn.remote(host=host, port=port)

    # Send solution
    sess.recvuntil(b">")
    sess.sendline(sx)

    # Read flag
    sess.recvline()
    flag = sess.recvline()[5:-1]

    return flag.decode()


def main(build_path: str, challenge: int, host: str = "localhost", port: int = 9001) -> typing.Optional[str]:
    if challenge == 0:
        return flag0(build_path)
    elif challenge == 1:
        return flag1(build_path)
    elif challenge == 2:
        return flag2(build_path)
    elif challenge == 3:
        return flag3(host, port)

    return None


def solve() -> typing.Optional[str]:
    return main(
        build_path=os.environ.get("BUILD_PATH") or os.path.join(REL_PATH, "..", "build"),
        challenge=int(os.environ.get("CHALLENGE_ID") or "0"),
        host=os.environ.get("CHALLENGE_HOST") or "localhost",
        port=os.environ.get("CHALLENGE_PORT") or 9001
    )


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