import os

KEY = os.environ["KEY"]


def build(template: str, flag: str) -> str:
    data = []
    for k, v in zip((KEY * 10).encode(), flag.encode()):
        data.append(str(k ^ v))

    code = (
        template
            .replace("{KEY}", KEY)
            .replace("{DATA}", ", ".join(data))
    )

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
