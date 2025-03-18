# PC from Scratch

## Hello World

Just have to figure out that `sb3` was a saved project file for [Scratch](https://scratch.mit.edu/). When the project run with the provided input, the flag will be written to the "terminal".

## Risky Adventure Map

The name is a hint `Risky Adventure Map -> RAM`. Monitor the writes to memory. At one point, the flag will be written in the upper section of RAM. Make sure to pause when it does because the scripts also erases the flag (gives a little extra difficulty).

## Really Secure Algorithm

The name is again a hint `Really Secure Algorithm -> RSA`. The whole code is just an implementation of RSA. The reason it's so big is because I had to implement my own big number operations (add, multiply/modulus) from scratch. 

Before starting, you should really turn on `Edit > Turn On Turbo Mode`. It will make the program run significantly faster. 

### RSA

Encryption:

```
c = (m ** e) % n

m: plain message (integer)
e: public exponent
n: modulus
c: encrypted message (integer)
```

Decryption (goal):

```
m = (c ** d) % n

m: plain message (integer)
d: private exponent
n: modulus
c: encrypted message (integer)
```

### Finding e

Try a really small input. The value is determined from the input's ASCII table. The best typeable input is ` ` (space) which will be `0x20`. The program output will be:

```
< 0080
```

The challenge mentions `little byte`, which a hint for `little endian`. The output would therefore be `0x8000`.

Given the value is small enough, it should not be impacted by the modulus and therefore the equation would be:

```
0x20 ** e = 0x8000
```

This can be solved using:

```
log(0x20 ** e) = log(0x8000)
e * log(0x20) = log(0x8000)
e = log(0x8000) / log(0x20)
e = 3
```

This would make sense, `3` is the smallest prime option:

```
e = 3
```

### Finding n

Try any input that large enough that is computable in a reasonable amount of time. I used `aaaaa` which will be `0x6161616161`. The program output will be:

```
< 328C7DF9A8EC30A9F80B
```

This is again in little endian so the value is actually `0x0BF8A930ECA8F97D8C32`. We are trying to solve for:

```
(0x6161616161 ** 3) % n = 0x0BF8A930ECA8F97D8C32
```

The `n` value should be somewhere in the ROM, so we can just try many bytes until a value satifies the equation:

```python
m = int.from_bytes(b"aaaaa")
e = 3
m_e = m ** e

c = 0x0BF8A930ECA8F97D8C32

with open("challenge.sx") as h:
    data = [int(v) for v in h.read().split(" ")]

for size in range(2, 20):
    for i in range(len(data)):
        buffer = data[i:i+size]
        if any(v > 0xFF for v in buffer):
            continue

        n = int.from_bytes(bytes(buffer), "little")

        if m_e % n == c:
            print(hex(n))
```

The output can be validated:

```
(0x6161616161 ** 3) % 0x635b3e4ead4228e638d5 = 0x0BF8A930ECA8F97D8C32
```

This confirms that:

```
n = 469197425231180645939413
```

### Finding d

Now that we have all the public parts, we need to find the private components. [RsaCtfTool](https://github.com/RsaCtfTool/RsaCtfTool) is probably the best for this. We can also just try a very common exploit where the factors of `n` are already solved on [factordb](https://factordb.com).

If we try it, we find that:

```
669711457553 * 700596383621 = 469197425231180645939413
```

This all we need to calculate `d`:

```
φ(n) = (p - 1) * (q - 1) = (669711457553 - 1) * (700596383621 - 1) = 469197425229810338098240

d = pow(e, -1, φ(n))
d = pow(3, -1, 469197425229810338098240) = 312798283486540225398827
```

```
d = 312798283486540225398827
```

### Decryption

Take the little endian of the output:

```
FB6CC393880D08F46E51 -> 516EF4080D8893C36CFB
```

And then just decrypt the message:

```
m = (0x516EF4080D8893C36CFB ** 312798283486540225398827) % 469197425231180645939413
m = pow(0x516EF4080D8893C36CFB, 312798283486540225398827, 469197425231180645939413)
m = 156799941828338652376166
```

If we convert this to bytes:

```
m = 0x213424522b2d67616c66 = "!4$R+-galf"
```

This is in little endian so just got to flip:

```
m = flag-R$4!
```

## PfSaaS

If you convert the challenge to bytes, you'll notice that there is a flag placeholder:

```
flag-placeholder
```

The flag is static so lazy solution is just to read a byte per session:

```
INT OUT
INT READ_ADDRESS
LOAD
STORE
```

You can also be fancy and read it in one shot like in [my solve](3/solve.sm).
