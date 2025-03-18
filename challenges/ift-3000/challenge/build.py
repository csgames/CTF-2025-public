import argparse
import base64
import hashlib
import os
import os.path
import re
import typing

## Config

FLAG_RE = r"flag(-\d_.+){5}"
MAX_EQUATION_COUNT = 128
VALID_EQUATION_INDEX = int(MAX_EQUATION_COUNT * 3 / 4)

## Common

DIR = os.path.dirname(os.path.abspath(__file__))

def remove_whitespace(text: str) -> str:
    return text.replace("\n", "").replace(" ", "").strip()

## Brainfuck

def build_brainfuck(flag_part: str):
    with open(os.path.join(DIR, "header.txt")) as h:
        header = h.read().strip()

    brainfuck = text_to_brainfuck(flag_part)

    i = 0
    buffer = []
    for c in header:
        if c == "$":
            if i < len(brainfuck):
                c = brainfuck[i]
                i += 1
            else:
                c = "-"

        buffer.append(c)

    return "".join(buffer) + "  []"

def text_to_brainfuck(text: str) -> str:
    buffer = []

    prev = 0
    for next in [ord(c) for c in text]:
        delta = next - prev

        if delta > 0:
            buffer.append("+" * delta)
        elif delta < 0:
            buffer.append("-" * -delta)

        buffer.append(".")

        prev = next

    return "".join(buffer)

## PHP

PHP_VAR_RE = r"\$[a-zA-Z_]+"

def build_php(flag_part: str, previous: str):
    with open(os.path.join(DIR, "code.php")) as h:
        code = h.read()

    key = hashlib.md5(previous.encode()).hexdigest()
    data = bytes([ord(k) ^ ord(c) for k, c in zip(key, flag_part)])

    code = code.replace("HEADER_SIZE", hex(len(previous)))
    code = code.replace("DATA", str(data)[2:-1])

    code = mangle_php(code)

    return code

def mangle_php(code: str) -> str:
    # Remove PHP headers
    code = code.replace("<?php", "").replace("?>", "")

    # Replace variables
    variables = set(re.findall(PHP_VAR_RE, code))
    for i, variable in enumerate(sorted(variables)):
        code = code.replace(variable, f"$v{i}") 

    code = remove_whitespace(code)

    # Replace PHP headers
    code = f"<?php {code}?>"

    return code

## JavaScript

def build_javascript(flag_part: str, previous: str):
    with open(os.path.join(DIR, "code.js")) as h:
        code = h.read()

    render_html = re.sub(r"  +", " ", previous.replace("\n", " "))
    offset = int(len(render_html) * 4 / 5) 

    key = bytes([ord(c) for c in render_html[offset:offset + len(flag_part)]])
    data = bytes([k ^ ord(c) for k, c in zip(key, flag_part)])

    code = code.replace("OFFSET", str(offset))
    code = code.replace("DATA", ", ".join(str(c) for c in data))

    code = remove_whitespace(code)

    return code

def mangle_javascript(code: str) -> str:
    code = remove_whitespace(code)

    return code

## HTML

def build_html(language: str, js: str, php: str):
    with open(os.path.join(DIR, f"code-{language}.html")) as h:
        code = h.read()

    js_eval = f"eval(atob(\"{base64.b64encode(js.encode()).decode()}\"))"

    php_inner = php.replace("<?php", "").replace("?>", "")
    php_eval = f"<?= eval(hex2bin(\"{''.join(hex(ord(c))[2:] for c in php_inner)}\"))?>"

    code = code.replace("JS", js_eval)
    code = code.replace("PHP", php_eval)

    code = code.strip()

    return code

## Python

def build_python(flag_part: str, previous: str):
    with open(os.path.join(DIR, "code.py")) as h:
        code = h.read()

    key = hashlib.sha256(previous.encode()).digest()
    data = bytes([k ^ ord(c) for k, c in zip(key, flag_part)])

    code = code.replace("SIZE", str(len(previous)))
    code = code.replace("DATA", str(data))

    return code

## C

def build_c(flag_part: str, previous: str):
    with open(os.path.join(DIR, "code.c")) as h:
        eval_code = h.read()

    offset = int(len(previous) * 4 / 5)
    eval_code = eval_code.replace("OFFSET", str(offset))

    eval_code = eval_code.strip()

    key = previous[offset:offset + len(flag_part)].encode()
    data = bytes([k ^ ord(c) for k, c in zip(key, flag_part)])

    code = build_equation_c(data, previous) + "\n" + eval_code

    return code.strip() + "\n"

def build_equation_c(data: bytes, previous: str) -> str:
    sections = []
    for i, (equation, answer) in enumerate(build_equations(previous)):
        prefix = "#if" if i == 0 else "#elif"

        if i < VALID_EQUATION_INDEX:
            answer = answer + 1

        equality = f"({equation}) == {answer}"

        if i == VALID_EQUATION_INDEX:
            body = data
        else:
            body = hashlib.sha256(data + equality.encode()).digest()[:len(data)]

        body_str = str(body)[2:-1]
        body_str = body_str.replace('"', '\\"')

        section = f"{prefix} {equality}\n#define data \"{body_str}\"\n"

        sections.append(section)

    return "".join(sections) + "#endif\n"

def build_equations(previous: str) -> typing.List[typing.Tuple[str, int]]:
    equation_answers = []

    seed = hashlib.sha256(previous.encode()).digest()
    for _ in range(MAX_EQUATION_COUNT):
        equation, answer = build_equation(seed)

        if answer < 2147483647 and answer > -2147483648:
            equation_answers.append((equation, answer))

        seed = hashlib.sha256(seed).digest()

    return equation_answers

DIV_OPERATORS = ["/", "%"]
OPERATORS = ["+", "-", *DIV_OPERATORS, "|", "^", "&", "S"]

def build_equation(seed: bytes) -> typing.Tuple[str, int]:
    if len(seed) % 2 != 1:
        seed = seed[:-1]

    parts = []
    for i, v in enumerate(seed):
        if i % 2 == 0:
            if len(parts) > 0 and parts[-1] in DIV_OPERATORS and v == 0:
                v = 1

            parts.append(str(v))
        else:
            op = OPERATORS[v % len(OPERATORS)]

            if op == "S":
                if len(parts) > 3:
                    break
                else:
                    op = "+"

            parts.append(op)

    equation_c = " ".join(parts)
    answer = eval(equation_c.replace("/", "//"))

    return equation_c, answer

## Document

def read_flag() -> str:
    text = os.environ.get("FLAG")

    assert text, "FLAG not defined"
    assert re.match(FLAG_RE, text), "Flag does not match regex"

    return text

def read_description(language: str) -> str:
    with open(os.path.join(DIR, f"description-{language}.txt")) as h:
        text = h.read().strip()

    text = text.replace("FLAG_RE", FLAG_RE)

    return text

HEADER_START = "#define _ /*//////////////////////////////////////////////////////////////////////"
HEADER_END = "#*////////////////////////////////////////////////////////////////////////////////"

def build_header(flag: str, language: str) -> str:
    flag_parts = flag.split("-")

    buffer = [
        HEADER_START,
        "#"
    ]

    for line in build_brainfuck(flag_parts[1]).split("\n"):
        buffer.append("# " + line)

    buffer.append("#")

    for line in read_description(language).split("\n"):
        buffer.append("# " + line)

    buffer += [
        "#",
        HEADER_END
    ]

    return "\n".join(line.strip() for line in buffer) + "\n"

DOCUMENTATION_START = "#define documentation /*"
DOCUMENTATION_END = "#*/"

def build_documentation(flag: str, language: str, previous: str) -> str:
    flag_parts = flag.split("-")

    buffer = [
        DOCUMENTATION_START
    ]

    js = build_javascript(flag_parts[5], previous)
    php = build_php(flag_parts[2], previous)
    html = build_html(language, js, php)

    for line in html.split("\n"):
        buffer.append("#" + line)

    buffer += [
        DOCUMENTATION_END
    ]

    return "\n".join(buffer) + "\n"

def build_body(flag: str, previous: str) -> str:
    flag_parts = flag.split("-")

    python = build_python(flag_parts[3], previous)
    python_eval = f"eval(__import__(\"base64\").b64decode(\"{ base64.b64encode(python.encode()).decode() }\"))"

    c = build_c(flag_parts[4], python_eval[5:-1])

    return c + "\n" + python_eval

def build(language: str) -> str:
    flag = read_flag()

    buffer = []

    header = build_header(flag, language)
    buffer += [header, "\n"]

    documentation = build_documentation(flag, language, "".join(buffer))
    buffer += [documentation, "\n"]

    body = build_body(flag, "".join(buffer))
    buffer += [body, "\n"]

    output = "".join(buffer)
    output = output.strip() + "\n"

    return output

# CLI

def cli():
    parser = argparse.ArgumentParser()

    parser.add_argument("language", choices=["fr", "en"])

    args = parser.parse_args()

    print(build(args.language))

if __name__ == "__main__":
    cli()
