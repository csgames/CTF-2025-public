# PC from Scratch (PfS)

## Architecture

PfS is a 16-byte architecture. Any memory cells can contain at most 65_535. The following is an example of data in memory:

```
0: 0
1: 1234
2: 65535
...
```

## Bus

```         
            +--------+
         .--| Memory |
         |  +--------+
+-----+  |  +-------+
| CPU |--+--| Input |
+-----+  |  +-------+
         |  +--------+
         '--| Output |
            +--------+
```

All devices communicate over a single shared bus. 3 internal registers are used to communicate between devices.

```
ADDRESS: The address to target.
DATA: The data associated to the operation.
CONTROL: The state of the operation. 
```

### Control

The CPU can perform the following control opcodes.

```
W - Write to address.
R - Read from address.
```

The CPU waits for device interrupts. If there are not any (for example, when trying to reach un-mapped memory), the CPU may end up in an undefined state.

## Memory Layout

|   Addresses   |  Device  |
|:-------------:|----------|
| [0, 2045]     | RAM      |
| 2046          | Input    |
| 2047          | Output   |
| [2048, 65535] | ROM      |

## Random Access Memory (RAM)

- Addresses: [0, 2045]
- Size: 2046
- Protection: Read, Write, Execute

RAM is a ~2K temporary storage. It is reset on every execution.

## Read-Only Memory (ROM)

- Addresses: [2048, 65535]
- Size: 63488
- Protection: Read, Execute

ROM is a 62K permanent storage used to store a program. This works like an old-school game cartridge; ROM must be attached and cannot be modified. 

## Input

- Address: 2046
- Protection: Read

The input is a buffered device of the keyboard. Every read to `2046` will provide the next buffered ASCII character. If the buffer is empty, it will prompt the user to type more input. A null-byte (`0x00`) is added to the end of the buffer to delimit inputs.

This is a sample program that reads the input `AB`.

```python
INT 2046
LOAD
# 'A'

INT 2046
LOAD
# 'B'

INT 2046
LOAD
# 0x00
```

## Output

- Address: 2047
- Protection: Write

The output is a streaming device of the screen. Every write to `2047` with an ASCII character will be displayed to the screen. When a null-byte (`0x00`) is sent, a new line is added.

This is a sample program that prints `AB`.

```python
INT 2047
INT 65 # A
STORE

INT 2047
INT 66 # B
STORE

INT 2047
INT 0
STORE

# Print: "AB"
```

## CPU

### Registers

- `PC`: Pointer towards current operation.

All other registers are temporary internal values. Additional CPU memory is managed by an internal stack.

### Stack

The stack is an infinite temporary internal storage. Is it used to store value temporarily. It exists separate to the bus (aka, it is not possible to execute code from the stack).

Like typical stacks, it follows First In, First Out (FIFO) push/pop.

It is cleared on every restart.

### Opcodes

```
OP (C_INT, C_CHAR)
    ARG: [...]
    INP: [...]
    OUT: [...]
```

```
OP: The assembly name of the operation.
C_INT: The integer value of the opcode.
C_CHAR: The character equivalence of the opcode (all opcodes have a friendly char representation).
ARG: The additional arguments used by the opcode that follow in the code.
INP: The input stack (right-most value is top of stack).
OUT: The output stack (right-most value is top of stack).
```

#### Undefined

Undefined opcodes leave the CPU in an undetermined state.

#### Add

```
ADD (43, '+')
    INP: [left, right]
    OUT: [out]
```

Signed integer addition -> `left + right`.

#### AND

```
AND (38, '&')
    INP: [left, right]
    OUT: [out]
```

Bitwise AND -> `left | right`.

#### Divide

```
DIV (47, '/')
    INP: [left, right]
    OUT: [out]
```

Signed integer division -> `left / right`.

#### Drop

```
DROP (88, 'X')
    INP: [value]
    OUT: []
```

Remove the top value of the stack.

#### Duplicate

```
DUP (68, 'D')
    INP: [value]
    OUT: [value, value]
```

Copy the top value of the stack.

#### Equal

```
EQ (61, '=')
    INP: [left, right]
    OUT: [out]
```

Checks `left == right`. If `true` -> `1` else `false` -> `0`.

#### Greater Than

```
GT (62, '>')
    INP: [left, right]
    OUT: [out]
```

Signed check `left > right`. If `true` -> `1` else `false` -> `0`.

#### Halt

```
HLT (0, '\0')
    INP: []
    OUT: []
```

Stops the CPU (end of program).

#### Integer

```
INT (73, 'I')
    ARG: [value]
    OUT: [value]
```

Take one operand from program and pushes it onto the stack.

#### Jump

```
JMP (74, 'J')
    IN: [address]
    OUT: []
```

Sets `PC` to `address`.

#### Jump Not Zero

```
JNZ (90, 'Z')
    IN: [address, condition]
    OUT: []
```

Sets `PC` to `address` if `condition != 0`. Otherwise, `PC++`.

#### Less Than

```
LT (60, '<')
    IN: [left, right]
    OUT: [out]
```

Signed check `left < right`. If `true` -> `1` else `false` -> `0`.

#### Load

```
LOAD (76, 'L')
    IN: [address]
    OUT: [value]
```

Loads a value from a specific address and pushes it to the stack.

#### Modulo

```
MOD (37, '%')
    IN: [left, right]
    OUT: [out]
```

Unsigned integer modulo -> `left % right`.

#### Multiply

```
MUL (42, '*')
    IN: [left, right]
    OUT: [out]
```

Signed integer multiplication -> `left * right`.

#### Not Equal

```
NEQ (33, '!')
    IN: [left, right]
    OUT: [out]
```

#### OR

```
OR (124, '|')
    IN: [left, right]
    OUT: [out]
```

Bitwise OR following `left | right`.

#### Rotate

```
ROT (82, 'R')
    IN: [a, b, c]
    OUT: [b, c, a]
```

Rotate top 3 items of stack clockwise.

#### Shift Left

```
SHL (123, "{")
    IN: [value, shift]
    OUT: [value]
```

Unsigned bitwise shift left.

#### Shift Right

```
SHR (125, "}")
    IN: [value, shift]
    OUT: [value]
```

Bitwise shift right.

#### Store

```
STORE (83, 'S')
    IN: [address, value]
    OUT: []
```

Store a value to a specific address.

#### Substract

```
SUB (45, '-')
    IN: [left, right]
    OUT: [out]
```

Signed integer subtraction -> `left - right`.

#### Swap

```
SWAP (87, 'W')
    IN: [left, right]
    OUT: [right, left]
```

Swaps top 2 values of stack.

#### XOR

```
XOR (94, '^')
    IN: [left, right]
    OUT: [out]
```

Bitwise XOR -> `left ^ right`.

## Hello World

`hello.sm`

```
$SECTION RAM

@zero
    $ZEROS 1

@print_ptr
    $ZEROS 1

$SECTION ROM

@main
# INP: []
# OUT: []

    @main_init
        INT @main_init_end
        INT @msg
        INT @print
        JMP
    @main_init_end

    @main_end
        HLT

@print 
# INP: [return, address]
# OUT: []

    @print_init
        # @print_ptr = address
        INT @print_ptr
        SWAP
        STORE

    @print_loop
        # *@print_ptr == 0 -> @print_loop_end
        INT @print_loop_end
        INT @print_ptr
        LOAD
        LOAD
        INT 0
        EQ
        JNZ

        # Push to OUT
        INT OUT
        INT @print_ptr
        LOAD
        LOAD
        STORE

        # Increment @print_ptr
        INT @print_ptr
        DUP
        LOAD
        INT 1
        ADD
        STORE

        # Loop
        INT @print_loop
        JMP
    @print_loop_end

    @print_end
        # Print
        INT OUT
        INT 0
        STORE

        # Return
        JMP

@msg
    $DATA "Hello World!" 0
```

`hello.sx`

```
73 2055 73 2094 73 2056 74 0 73 1 87 83 73 2088 73 1 76 76 73 0 61 90 73 2047 73 1 76 76 83 73 1 68 76 73 1 43 83 73 2060 74 73 2047 73 0 83 74 72 101 108 108 111 32 87 111 114 108 100 33 0
```
