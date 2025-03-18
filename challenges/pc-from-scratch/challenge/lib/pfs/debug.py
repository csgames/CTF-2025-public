from .emu import PFSEMU
from .ops import OPS


class PFSDebug:
    emu: PFSEMU

    def __init__(self, rom: list[int], input: str | None = None, output: bool = True):
        self.emu = PFSEMU(rom, input, output)

    def debug_instruction(self) -> None:
        pc = self.emu.cpu.pc

        op_id = self.emu.bus.read(pc)

        for op in OPS:
            if op.id == op_id:
                break
        else:
            op = None

        label = "?"
        rom_args = []
        stack_args = []
        if op:
            label = op.label

            for i in range(op.args):
                rom_args.append(str(self.emu.bus.read(pc + i + 1)))

            for i in range(op.in_stack):
                j = len(self.emu.cpu.stack) - i - 1

                if j < 0:
                    break

                stack_args.append(str(self.emu.cpu.stack[j]))

        print(f"{pc}: {label} ({', '.join(rom_args)}) [{", ".join(stack_args[::-1])}]")

    def debug_memory(self) -> None:
        print(f"  STATUS: {self.emu.cpu.status.name}")
        print(f"  STACK: {', '.join(str(v) for v in self.emu.cpu.stack[::-1])}")
        print(f"  IN: {bytes(self.emu.input.buffer)}")
        print(f"  RAM: {self.emu.ram.data[:256]}")

    def step(self) -> bool:
        self.debug_instruction()

        state = self.emu.step()

        self.debug_memory()

        return state
