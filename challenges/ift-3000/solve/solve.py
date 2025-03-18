import json
import os.path
import re
import subprocess
import sys
import tempfile
import typing


def solve_brainfuck(path: str) -> str:
    with open(path) as h:
        file = h.read()

    output = []
    
    value = 0
    for c in file:
        if c == "+":
            value += 1
        elif c == "-":
            value -= 1
        elif c == ".":
            output.append(chr(value))
        elif c == "[":
            break

    return "".join(output)


def solve_php(path: str) -> typing.Optional[str]:
    proc = subprocess.run(["php", path], capture_output=True)

    return proc.stdout.split(b"\n")[-1].decode().strip() 


def solve_python(path: str) -> typing.Optional[str]:
    proc = subprocess.run(["python", path], capture_output=True)

    return proc.stdout.strip().decode()[2:-1]


def solve_c(path: str) -> typing.Optional[str]:
    with tempfile.TemporaryDirectory() as temp_dir:
        c_target = os.path.join(temp_dir, "code.c")
        exe_target = os.path.join(temp_dir, "code")

        with open(path) as rh:
            with open(c_target, "w") as wh:
                wh.write(rh.read())

        subprocess.run(["gcc", "-Wno-implicit-int", "-Wno-implicit-function-declaration", c_target, "-o", exe_target], capture_output=True)

        proc = subprocess.run([exe_target], capture_output=True)

    return proc.stdout.decode()


SCRIPT_RE = re.compile(r"<script>(.*?)</script>")
def solve_js(path: str) -> typing.Optional[str]:
    # Intended solution is to run in a browser.
    # This is expensive for testing, so "hacking a browser" in NodeJS.

    with open(path) as h:
        file = h.read()

    document = {
        "body": {
            "innerText": re.sub(r"  +", " ", file.replace("\n", " "))
        }
    }

    js_eval = SCRIPT_RE.findall(file)[0]
    js_code = f'let document = {json.dumps(document)}; {js_eval}'

    with tempfile.TemporaryDirectory() as temp_dir:
        js_target = os.path.join(temp_dir, "code.js")

        with open(js_target, "w") as h:
            h.write(js_code)

        proc = subprocess.run(["node", js_target], capture_output=True)

    return proc.stdout.strip().decode()


def solve_file(path: str) -> typing.Optional[str]:
    part1 = solve_brainfuck(path)
    part2 = solve_php(path)
    part3 = solve_python(path)
    part4 = solve_c(path)
    part5 = solve_js(path)

    return f"flag-{part1}-{part2}-{part3}-{part4}-{part5}"


def solve() -> typing.Optional[str]:
    build_folder = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "build"
    )

    language = os.environ.get("LANG") or "en"

    if language == "fr":
        file_name = "devoir.txt"
    else:
        file_name = "assignment.txt"

    rel_path = os.path.join(build_folder, file_name)
    path = os.path.abspath(rel_path)

    return solve_file(path)


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
