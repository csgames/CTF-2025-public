import io
import os

from pfs.asm import PFSASM


def build(template: str, flag: str) -> str:
    asm = PFSASM()

    code = template.replace("{DATA}", ", ".join("0" for _ in range(len(flag))))

    out_file = io.StringIO()

    asm.asm(io.StringIO(code), out_file)

    out_file.seek(0)

    raw = out_file.read()

    key = [int(v) for v in raw.split(" ")]

    data = []
    for k, v in zip(key, flag.encode()):
        data.append(k ^ v)

    data_str = ", ".join(str(v) for v in data)

    code = template.replace("{DATA}", data_str)

    return code


def cli() -> None:
    with open("challenge.sm.template") as h:
        template = h.read()

    flag = os.environ["FLAG"]

    code = build(template, flag)

    with open("challenge.sm", "w") as h:
        h.write(code)


if __name__ == "__main__":
    cli()
