import os


P = int(os.environ["P"])
Q = int(os.environ["Q"])
E = 3


def rsa_encrypt(data: bytes) -> bytes:
    msg = int.from_bytes(data, "little")

    n = P * Q

    out = pow(msg, E, n)

    return out.to_bytes(1024, "little").rstrip(b"\0")


def rsa_decrypt(data: bytes) -> bytes:
    enc = int.from_bytes(data, "little")

    n = P * Q
    phi_n = (P - 1) * (Q - 1)
    d = pow(E, -1, phi_n)

    out = pow(enc, d, n)

    return out.to_bytes(1024, "little").rstrip(b"\0")


def build(template: str, flag: str) -> tuple[str, str]:
    flag_raw = flag.encode()

    enc = rsa_encrypt(flag_raw)
    dec = rsa_decrypt(enc)

    assert flag_raw == dec, f"{flag} failed to encrypt/decrypt"

    n = P * Q
    n_bytes = n.to_bytes(10, "little")

    code = (
        template
            .replace("{N}", ", ".join(str(v) for v in n_bytes))
            .replace("{N_SIZE}", str(len(n_bytes)))
            .replace("{E}", str(E))
    )

    return code, enc.hex().upper()


def cli() -> None:
    with open("challenge.sm.template") as h:
        template = h.read()

    flag = os.environ["FLAG"]

    code, enc = build(template, flag)

    with open("challenge.sm", "w") as h:
        h.write(code)

    with open("output", "w") as h:
        h.write(enc)


if __name__ == "__main__":
    cli()
