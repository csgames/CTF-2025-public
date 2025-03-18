# IFT-3000

This challenge is a [polyglot program](https://en.wikipedia.org/wiki/Polyglot_(computing)). The goal is to find the programming languages that are supported. The regex hints that there are 5 with the count selector (`{5}`).

Both french and english versions of the program produce the same flag. Some of the code differs because the program references itself when running. Therefore the *WHOLE* file has to be run, not parts of it.

## Brainfuck

### Location

Hidden inside the IFT-3000 header.

### Run

https://minond.xyz/brainfuck/

### Output

`1_brainfuck`

### Explanation

Brainfuck ignores every non-operator character. This means it will only operate on the code defined by the `+-.` characters. When reaching `[]`, it will be stuck in an infinite loop. This prevents interprets from reading the non-brainfuck code following the header.

Note: Brainfuck compilers may break because of unbalanced square brackets later in the program. An interpreter should be used instead.

## PHP

### Location

Hidden inside the JavaScript backtrick string. It can be found by the inline PHP tag `<?= .. ?>`.

### Run

https://www.programiz.com/php/online-compiler/

### Output

Starts with the source code but suddenly end with `2_php8`.

### Explanation

PHP considers non-PHP code as plaintext. Once execution reaches the PHP tag `<?=`, it will run `eval(hex2bin(...))`. The program inside the hex is an [XOR decryption](https://en.wikipedia.org/wiki/XOR_cipher) that uses the `md5` hash of the header as a key.

## Python

### Location

Last line of the file.

### Run

https://www.online-python.com/

### Output

`3_python38` as a byte string.

### Explanation

Python comments are in the `# ...` form. All lines up until the last one are considered comments. The last line is a base64 eval. The program inside the base64 is an [XOR decryption](https://en.wikipedia.org/wiki/XOR_cipher) that uses the `sha256` hash of the header and documentation as a key.

## C

### Location

The tower of `#if`/`#elif` with the last `eval`.

### Run

https://www.programiz.com/c-programming/online-compiler/

### Output

`4_c99`

### Explanation

C multi-line comments `/* ... */` are hidden inside the `#define`s. All lines up to the first `#if` are comments.

The tower of `#if`/`#elif` are conditional compilations. The first valid equation will `#define` the `data` to the valid encrypted data.

The `#define eval(_) ...` is a macro with the whole C program. It uses some tricks like [implicit int](https://gcc.gnu.org/onlinedocs/gcc/Warning-Options.html#index-Wimplicit-int) and [implicit function declaration](https://gcc.gnu.org/onlinedocs/gcc/Warning-Options.html#index-Wimplicit-function-declaration) to shrink the size of the program. It is an [XOR decryption](https://en.wikipedia.org/wiki/XOR_cipher) that uses the Python program as the key through the `#_` [macro parameter stringizing](https://gcc.gnu.org/onlinedocs/cpp/Stringizing.html).

## HTML/JS

### Location

The documentation.

### Run

https://www.programiz.com/html/online-compiler/

### Output

`5_htmljs` in the debug console.

### Explanation

[Browsers try really hard not to fail](https://html.spec.whatwg.org/multipage/parsing.html#parsing). Notice that even if the page renders like the documentation HTML, the actual HTML strips the `<html>` and `<head>` tags and places the whole content in the body. The `<title>`, `<script>`, and `<style>` tags all work as expected in the `<body>` tag.

The script tag is an eval of base64 JavaScript program. The program is an [XOR decryption](https://en.wikipedia.org/wiki/XOR_cipher) that uses the plain header at an offset as the key.

## Flag

Combine the output parts in the previous sections following the regex to get the flag.
