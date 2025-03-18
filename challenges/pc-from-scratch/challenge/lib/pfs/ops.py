import dataclasses


@dataclasses.dataclass
class OPEntry:
    id: int
    name: str
    label: str
    args: int
    in_stack: int
    out_stack: int


OPS: list[OPEntry] = [
    OPEntry(
        id=ord("+"),
        name="Add",
        label="ADD",
        args=0,
        in_stack=2,
        out_stack=1
    ),
    OPEntry(
        id=ord("&"),
        name="Bitwise AND",
        label="AND",
        args=0,
        in_stack=2,
        out_stack=1
    ),
    OPEntry(
        id=ord("/"),
        name="Divide",
        label="DIV",
        args=0,
        in_stack=2,
        out_stack=1
    ),
    OPEntry(
        id=ord("X"),
        name="Drop",
        label="DROP",
        args=0,
        in_stack=1,
        out_stack=0
    ),
    OPEntry(
        id=ord("D"),
        name="Duplicate",
        label="DUP",
        args=0,
        in_stack=1,
        out_stack=2
    ),
    OPEntry(
        id=ord("="),
        name="Equal",
        label="EQ",
        args=0,
        in_stack=2,
        out_stack=1
    ),
    OPEntry(
        id=ord(">"),
        name="Greater Than",
        label="GT",
        args=0,
        in_stack=2,
        out_stack=1
    ),
    OPEntry(
        id=0,
        name="Halt",
        label="HLT",
        args=0,
        in_stack=0,
        out_stack=0
    ),
    OPEntry(
        id=ord("I"),
        name="Integer",
        label="INT",
        args=1,
        in_stack=0,
        out_stack=1
    ),
    OPEntry(
        id=ord("J"),
        name="Jump",
        label="JMP",
        args=0,
        in_stack=1,
        out_stack=0
    ),
    OPEntry(
        id=ord("Z"),
        name="Jump Not Zero",
        label="JNZ",
        args=0,
        in_stack=2,
        out_stack=0
    ),
    OPEntry(
        id=ord("<"),
        name="Less Than",
        label="LT",
        args=0,
        in_stack=2,
        out_stack=1
    ),
    OPEntry(
        id=ord("L"),
        name="Load",
        label="LOAD",
        args=0,
        in_stack=1,
        out_stack=1
    ),
    OPEntry(
        id=ord("%"),
        name="Modulo",
        label="MOD",
        args=0,
        in_stack=2,
        out_stack=1
    ),
    OPEntry(
        id=ord("*"),
        name="Multiply",
        label="MUL",
        args=0,
        in_stack=2,
        out_stack=1
    ),
    OPEntry(
        id=ord("!"),
        name="Not Equal",
        label="NEQ",
        args=0,
        in_stack=2,
        out_stack=1
    ),
    OPEntry(
        id=ord("|"),
        name="Bitwise OR",
        label="OR",
        args=0,
        in_stack=2,
        out_stack=1
    ),
    OPEntry(
        id=ord("R"),
        name="Rotate",
        label="ROT",
        args=0,
        in_stack=3,
        out_stack=3
    ),
    OPEntry(
        id=ord("{"),
        name="Shift Left",
        label="SHL",
        args=0,
        in_stack=2,
        out_stack=1
    ),
    OPEntry(
        id=ord("}"),
        name="Shift Right",
        label="SHR",
        args=0,
        in_stack=2,
        out_stack=1
    ),
    OPEntry(
        id=ord("S"),
        name="Store",
        label="STORE",
        args=0,
        in_stack=2,
        out_stack=1
    ),
    OPEntry(
        id=ord("-"),
        name="Subtract",
        label="SUB",
        args=0,
        in_stack=2,
        out_stack=1
    ),
    OPEntry(
        id=ord("W"),
        name="Swap",
        label="SWAP",
        args=0,
        in_stack=2,
        out_stack=2
    ),
    OPEntry(
        id=ord("^"),
        name="Bitwise XOR",
        label="XOR",
        args=0,
        in_stack=2,
        out_stack=2
    ),
]
