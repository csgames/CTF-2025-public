import abc
import collections
import dataclasses
import io
import re

from .address import INPUT_ADDRESS, OUTPUT_ADDRESS, ROM_ADDRESS, RAM_ADDRESS
from .ops import OPS, OPEntry


@dataclasses.dataclass
class Node(abc.ABC):
    pass


@dataclasses.dataclass
class OPValue(abc.ABC):
    pass


@dataclasses.dataclass
class OPNumber(OPValue):
    value: int


@dataclasses.dataclass
class OPLabel(OPValue):
    name: str


@dataclasses.dataclass
class OP(Node):
    entry: OPEntry
    args: list[OPValue]


@dataclasses.dataclass
class Label(Node):
    name: str


@dataclasses.dataclass
class Data(Node):
    value: list[int]


class PFSASM:
    keep_ram: bool

    KEY_RE = re.compile(r"\bIN\b")
    SCREEN_RE = re.compile(r"\bOUT\b")
    RAM_RE = re.compile(r"\bRAM\b")
    ROM_RE = re.compile(r"\bROM\b")
    COMMENT_RE = re.compile(r"#.*?$", re.MULTILINE)

    def __init__(self, keep_ram: bool = False):
        self.keep_ram = keep_ram

    def parse_arg(self, arg: str) -> OPValue | None:
        arg = arg.strip()

        if arg.startswith("0x"):
            return OPNumber(int(arg, 16))
        elif arg.startswith("0b"):
            return OPNumber(int(arg, 2))
        elif arg[0].isdecimal():
            return OPNumber(int(arg))
        elif arg.startswith("@"):
            return OPLabel(name=arg)

        return None

    def parse_data(self, line: str) -> list[int] | None:
        args = line.lstrip()[5:].strip()

        i = 0
        out = []
        while i < len(args):
            c = args[i]

            if c.isspace() or c == ",":
                i += 1
            elif c.isdigit():
                j = i + 1

                if c == "0" and j < len(args):
                    if args[j] == "x" or args[j] == "b":
                        j += 1

                while j < len(args):
                    if not args[j].isalnum():
                        break

                    j += 1

                value = eval(args[i:j])

                out.append(value)

                i = j
            elif c == '"':
                j = i + 1

                while True:
                    j = args.find('"', j)

                    if j == -1:
                        return None

                    if args[j - 1] != "\\":
                        break

                    j += 1
                
                value = eval(args[i:j + 1])

                out += [ord(c) for c in value]

                i = j + 1
            else:
                return None

        return out

    def parse(self, file: io.StringIO) -> dict[int, list[Node]]:
        out = collections.defaultdict(list)

        asm = file.read()
        asm = self.KEY_RE.sub(str(INPUT_ADDRESS), asm)
        asm = self.SCREEN_RE.sub(str(OUTPUT_ADDRESS), asm)
        asm = self.RAM_RE.sub(str(RAM_ADDRESS), asm)
        asm = self.ROM_RE.sub(str(ROM_ADDRESS), asm)
        asm = self.COMMENT_RE.sub("", asm)

        i = 0

        for line in asm.strip().split("\n"):
            ci = i

            line = line.strip()

            if not line:
                continue

            args = line.split(" ")

            label = args.pop(0).strip()

            for entry in OPS:
                if entry.label == label:
                    break
            else:
                entry = None

            node = None

            if entry is None:
                if label == "$DATA":
                    value = self.parse_data(line)

                    if value is None:
                        assert False, f"Invalid data: {line}"

                    node = Data(value=value)

                    i += len(value)
                elif label == "$ZEROS":
                    arg_p = self.parse_arg(args[0])

                    if not isinstance(arg_p, OPNumber):
                        assert False, f"Invalid zeros: {line}"

                    node = Data(value=[0] * arg_p.value)

                    i += arg_p.value
                elif label == "$SECTION":
                    i = eval(line[8:].strip())
                elif label.startswith("@"):
                    node = Label(name=label)
                else:
                    assert False, f"Unhandled: {line}"
            else:
                assert len(args) == entry.args, f"Invalid argument count for {line}"

                parsed_args = []

                for arg in args:
                    arg_p = self.parse_arg(arg)

                    if arg_p is None:
                        assert False, f"Invalid arguments: {arg}"

                    parsed_args.append(arg_p)

                node = OP(entry=entry, args=parsed_args)
                i += 1 + entry.args

            if node is None:
                continue

            out[ci].append(node)

        out = dict(out)

        return out

    def bytecode(self, line_nodes: dict[int, list[Node]], base: int) -> list[str]:
        labels: dict[str, int] = {}

        for line, nodes in line_nodes.items():
            for node in nodes:
                if isinstance(node, Label):
                    labels[node.name] = line

        lines: dict[int, list[int]] = {}
        size = 0

        for line, nodes in line_nodes.items():
            value = []
            
            for node in nodes:
                if isinstance(node, OP):
                    value.append(node.entry.id)

                    for arg in node.args:
                        if isinstance(arg, OPLabel):
                            value.append(labels[arg.name])
                        elif isinstance(arg, OPNumber):
                            value.append(arg.value)
                        else:
                            assert False, f"Unhandled {arg}"
                elif isinstance(node, Data):
                    value += node.value
                elif isinstance(node, Label):
                    continue

                break

            if value:
                lines[line] = value

                offset = line + len(value)

                if offset > size:
                    size = offset

        out = [0 for _ in range(size - base)]

        for line, values in lines.items():
            if line < base:
                continue

            for i, v in enumerate(values):
                vi = (line - base) + i
                out[vi] = v

        return out

    def asm(self, in_file: str | io.StringIO, out_file: str | io.StringIO | None = None) -> None:
        if isinstance(in_file, str):
            with open(in_file) as h:
                asm = self.parse(h)
        else:
            asm = self.parse(in_file)

        if self.keep_ram:
            base = RAM_ADDRESS
        else:
            base = ROM_ADDRESS 

        bytecode = self.bytecode(asm, base)

        out = " ".join(str(v) for v in bytecode)

        if isinstance(out_file, str):
            with open(out_file, "w") as h:
                h.write(out)
        elif out_file is None:
            print(out)
        else:
            out_file.write(out)
