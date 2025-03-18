import argparse
import io

from .asm import PFSASM
from .debug import PFSDebug
from .emu import PFSEMU


def cli() -> None:
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers(dest="cmd")

    asm = subparsers.add_parser("asm", help="PFS Assembler")

    asm.add_argument("in_file", help="Path to file to assemble")
    asm.add_argument("-o", "--out_file", help="Path to output file. If none, will output to console.", default=None, required=False)
    asm.add_argument("-k", "--keep_ram", help="Keep RAM data", action="store_true", default=False)

    emu = subparsers.add_parser("run", help="PFS Emulator")

    emu.add_argument("exe", help="Path to file to run")
    emu.add_argument("-i", "--input", help="Default input buffer", default=None)
    emu.add_argument("-n", "--no_output", help="Is output enabled?", action="store_true", default=False)

    debug = subparsers.add_parser("debug", help="PFS Debug")

    debug.add_argument("exe", help="Path to file to run")
    debug.add_argument("-i", "--input", help="Default input buffer", default=None)

    args = parser.parse_args()

    if hasattr(args, "exe"):
        with open(args.exe) as h:
            data = h.read()

            if "@" in data:
                asm = PFSASM()

                rom = io.StringIO()
                asm.asm(io.StringIO(data), rom)

                rom.seek(0)
                data = rom.read()

            rom = [int(i) for i in data.split(" ")]

    if args.cmd == "asm":
        asm = PFSASM(
            keep_ram=args.keep_ram
        )

        asm.asm(args.in_file, args.out_file)
    elif args.cmd == "run":
        emu = PFSEMU(
            rom=rom,
            input=args.input,
            output=not args.no_output
        )

        while emu.step():
            continue

        exit(emu.cpu.status.value)
    elif args.cmd == "debug":
        debug = PFSDebug(
            rom=rom,
            input=args.input,
            output=False
        )

        while debug.step():
            continue

        exit(debug.emu.cpu.status.value)