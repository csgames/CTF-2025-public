import abc
import enum
import sys
import termios
import tty
import typing

from .address import ROM_ADDRESS, ROM_SIZE, RAM_ADDRESS, RAM_SIZE, INPUT_ADDRESS, OUTPUT_ADDRESS
from .ops import OPS


class PFSDevice(abc.ABC):
    @abc.abstractmethod
    def contains(self, address: int) -> bool:
        return False

    @abc.abstractmethod
    def write(self, address: int, data: int) -> bool:
        pass

    @abc.abstractmethod
    def read(self, address: int) -> int | None:
        pass


class PFSBUS:
    devices: list[PFSDevice]

    def __init__(self, devices: list[PFSDevice]):
        self.devices = devices

    def write(self, address: int, data: int) -> bool:
        for device in self.devices:
            if device.contains(address):
                return device.write(address, data)

        return False

    def read(self, address: int) -> int | None:
        for device in self.devices:
            if device.contains(address):
                return device.read(address)

        return None


class PFSMemoryProtection(enum.Enum):
    READ = 1
    WRITE = 2
    READ_WRITE = 3


class PFSMemory(PFSDevice):
    base_address: int
    data: list[int]
    protection: PFSMemoryProtection

    def __init__(self, address: int, data: list[int], protection: PFSMemoryProtection):
        self.base_address = address
        self.data = data
        self.protection = protection

    def contains(self, address: int) -> bool:
        return self.base_address <= address and address < self.base_address + len(self.data)

    def write(self, address: int, data: int) -> bool:
        if self.protection not in (PFSMemoryProtection.WRITE, PFSMemoryProtection.READ_WRITE):
            return False

        self.data[address - self.base_address] = data

        return True

    def read(self, address: int) -> int | None:
        if self.protection not in (PFSMemoryProtection.READ, PFSMemoryProtection.READ_WRITE):
            return None

        return self.data[address - self.base_address]


class PFSInput(PFSDevice):
    buffer: list[int]

    def __init__(self, buffer: str | None = None):
        if buffer is not None:
            self.buffer = [v for v in buffer.encode()] + [0]
        else:
            self.buffer = []

    def contains(self, address: int) -> bool:
        return address == INPUT_ADDRESS

    def write(self, address: int, data: int) -> bool:
        return False

    def next(self) -> str:
        no = sys.stdin.fileno()
        old = termios.tcgetattr(no)

        try:
            tty.setraw(no)

            return sys.stdin.read(1)
        finally:
            termios.tcsetattr(no, termios.TCSADRAIN, old)

    def read(self, address: int) -> int:
        if len(self.buffer) == 0:
            c = self.next()

            if c == "\3":
                raise RuntimeError("Program killed")

            if c == "\r" or c == "\n":
                v = 0
            else:
                v = ord(c)

            self.buffer.append(v)

        return self.buffer.pop(0) 


class PFSOutput(PFSDevice):
    buffer: str
    enabled: bool

    def __init__(self, enabled: bool = True):
        self.buffer = ""
        self.enabled = enabled

    def contains(self, address: int) -> bool:
        return address == OUTPUT_ADDRESS

    def write(self, address: int, data: int) -> bool:
        char = chr(data) if data != 0 else "\n"

        self.buffer += char

        if self.enabled:
            print(char, end="", flush=True)

        return True

    def read(self, address: int) -> None:
        return None


class PFSCPUStatus(enum.Enum):
    Halt = 0
    OpError = 1
    StackError = 2
    ReadError = 3
    WriteError = 4
    Running = 99


class PFSCPU:
    stack: list[int]
    bus: PFSBUS
    pc: int
    status: PFSCPUStatus
    op_fn_map: dict[int, typing.Callable[["PFSCPU"], None]]

    MAX_SIGNED =  32_767
    MAX_UNSIGNED = 65_535

    def __init__(self, bus: PFSBUS, pc: int):
        self.pc = pc
        self.stack = []
        self.status = PFSCPUStatus.Running
        self.bus = bus

        self.op_fn_map = {}
        for op in OPS:
            fn_name = op.name.lower().replace(" ", "_")

            fn = getattr(self, fn_name)

            self.op_fn_map[op.id] = fn

    def step(self) -> bool:
        if self.status != PFSCPUStatus.Running:
            return False

        op = self.bus.read(self.pc)

        if op not in self.op_fn_map:
            self.status = PFSCPUStatus.OpError
            return False

        self.op_fn_map[op]()

        return self.status == PFSCPUStatus.Running
    
    def truncate(self, value: int) -> int:
        return value % (self.MAX_UNSIGNED + 1)

    def signed(self, value: int) -> int:
        value = self.truncate(value)

        if value > self.MAX_SIGNED:
            value -= (self.MAX_UNSIGNED + 1)

        return value

    def unsigned(self, value: int) -> int:
        if value < 0:
            value = (self.MAX_UNSIGNED + 1) + value

        return self.truncate(value)

    def pop(self, count: int) -> list[int] | None:
        if len(self.stack) < count:
            return None

        return [self.stack.pop() for _ in range(count)]

    def push(self, value: int) -> None:
        self.stack.append(value)

    ########
    # Flow #
    ########

    def halt(self) -> None:
        self.status = PFSCPUStatus.Halt

    def jump(self) -> None:
        if (args := self.pop(1)) is None:
            self.status = PFSCPUStatus.StackError
            return

        address, = args

        self.pc = address

    def jump_not_zero(self) -> None:
        if (args := self.pop(2)) is None:
            self.status = PFSCPUStatus.StackError
            return

        condition, address = args

        if condition != 0:
            self.pc = address
        else:
            self.pc += 1

    ########
    # Math #
    ########

    def add(self) -> None:
        if (args := self.pop(2)) is None:
            self.status = PFSCPUStatus.StackError
            return

        right, left = args

        self.push(self.unsigned(self.signed(left) + self.signed(right)))

        self.pc += 1

    def subtract(self) -> None:
        if (args := self.pop(2)) is None:
            self.status = PFSCPUStatus.StackError
            return

        right, left = args

        self.push(self.unsigned(self.signed(left) - self.signed(right)))

        self.pc += 1

    def multiply(self) -> None:
        if (args := self.pop(2)) is None:
            self.status = PFSCPUStatus.StackError
            return

        right, left = args

        self.push(self.unsigned(self.signed(left) * self.signed(right)))

        self.pc += 1

    def divide(self) -> None:
        if (args := self.pop(2)) is None:
            self.status = PFSCPUStatus.StackError
            return

        right, left = args

        self.push(self.unsigned(self.signed(left) // self.signed(right)))

        self.pc += 1

    def modulo(self) -> None:
        if (args := self.pop(2)) is None:
            self.status = PFSCPUStatus.StackError
            return

        right, left = args

        self.push(left % right)

        self.pc += 1

    def shift_left(self) -> None:
        if (args := self.pop(2)) is None:
            self.status = PFSCPUStatus.StackError
            return
        
        shift, value = args

        self.push(self.truncate(value << shift))

        self.pc += 1

    def shift_right(self) -> None:
        if (args := self.pop(2)) is None:
            self.status = PFSCPUStatus.StackError
            return

        shift, value = args

        self.push(value >> shift)

        self.pc += 1

    def bitwise_and(self) -> None:
        if (args := self.pop(2)) is None:
            self.status = PFSCPUStatus.StackError
            return

        right, left = args

        self.push(left & right)

        self.pc += 1

    def bitwise_or(self) -> None:
        if (args := self.pop(2)) is None:
            self.status = PFSCPUStatus.StackError
            return

        right, left = args

        self.push(left | right)

        self.pc += 1

    def bitwise_xor(self) -> None:
        if (args := self.pop(2)) is None:
            self.status = PFSCPUStatus.StackError
            return

        right, left = args

        self.push(left ^ right)

        self.pc += 1

    ##############
    # Comparison #
    ##############

    def greater_than(self) -> None:
        if (args := self.pop(2)) is None:
            self.status = PFSCPUStatus.StackError
            return

        right, left = args

        self.push(1 if self.signed(left) > self.signed(right) else 0)

        self.pc += 1

    def less_than(self) -> None:
        if (args := self.pop(2)) is None:
            self.status = PFSCPUStatus.StackError
            return

        right, left = args

        self.push(1 if self.signed(left) < self.signed(right) else 0)

        self.pc += 1

    def equal(self) -> None:
        if (args := self.pop(2)) is None:
            self.status = PFSCPUStatus.StackError
            return

        right, left = args

        self.push(1 if left == right else 0)

        self.pc += 1

    def not_equal(self) -> None:
        if (args := self.pop(2)) is None:
            self.status = PFSCPUStatus.StackError
            return

        right, left = args

        self.push(1 if left != right else 0)

        self.pc += 1

    #########
    # Stack #
    #########

    def integer(self) -> None:
        value = self.bus.read(self.pc + 1)

        if value is None:
            self.status = PFSCPUStatus.ReadError
            return

        self.push(value)

        self.pc += 2

    def drop(self) -> None:
        if not self.stack:
            self.status = PFSCPUStatus.StackError
            return

        self.pop(1)

        self.pc += 1

    def swap(self) -> None:
        if (args := self.pop(2)) is None:
            self.status = PFSCPUStatus.StackError
            return

        right, left = args

        self.push(right)
        self.push(left)

        self.pc += 1

    def duplicate(self) -> None:
        if (args := self.pop(1)) is None:
            self.status = PFSCPUStatus.StackError
            return

        val, = args

        self.push(val)
        self.push(val)

        self.pc += 1

    def rotate(self) -> None:
        if (args := self.pop(3)) is None:
            self.status = PFSCPUStatus.StackError
            return
        
        a, b, c = args

        self.push(a)
        self.push(c)
        self.push(b)

        self.pc += 1

    ##########
    # Memory #
    ##########

    def load(self) -> None:
        if (args := self.pop(1)) is None:
            self.status = PFSCPUStatus.StackError
            return

        address, = args

        value = self.bus.read(address)

        if value is None:
            self.status = PFSCPUStatus.ReadError
            return

        self.push(value)

        self.pc += 1

    def store(self) -> None:
        if (args := self.pop(2)) is None:
            self.status = PFSCPUStatus.StackError
            return

        value, address = args

        if not self.bus.write(address, value):
            self.status = PFSCPUStatus.WriteError
            return

        self.pc += 1


class PFSEMU:
    cpu: PFSCPU
    bus: PFSBUS
    input: PFSInput
    output: PFSOutput
    rom: PFSMemory
    ram: PFSMemory

    def __init__(self, rom: list[int], input: str | None = None, output: bool = True):
        self.input = PFSInput(buffer=input)
        self.output = PFSOutput(enabled=output)
        self.ram = PFSMemory(RAM_ADDRESS, [0] * RAM_SIZE, PFSMemoryProtection.READ_WRITE)
        self.rom = PFSMemory(ROM_ADDRESS, rom[:ROM_SIZE], PFSMemoryProtection.READ)

        self.bus = PFSBUS([
            self.input,
            self.output,
            self.ram,
            self.rom
        ])

        self.cpu = PFSCPU(self.bus, ROM_ADDRESS)

    def step(self) -> bool:
        return self.cpu.step()
