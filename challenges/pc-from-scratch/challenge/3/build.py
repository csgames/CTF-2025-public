import os


def build(template: str, flag: str) -> str:
    code = (
        template
            .replace("{FLAG}", flag)
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
