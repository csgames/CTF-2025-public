# Printer Jam

## Stuck On Top

The bug is having control over the format string for `printf` in the `Print` menu. This is also known as a format string vulnerability. You can try multiple offsets and you'll find that the offset `6` prints the flag:

```
%6$s
```

## Premium Logging

The goal is to overwrite `WORKER_PREMIUM` to any truthy value. The program does not have PIE enabled, so you can find the address of the value and you know it'll be at a predictable position. You can reuse the format string vulnerability to write to at that address using the [pwnlib.fmtstr](https://docs.pwntools.com/en/dev/fmtstr.html) library.

## No SSH, No Problem

The goal is to get RCE. Given you were able to read and write data, this one is just to combine both of them. You should really test on the same OS as target: `ubuntu:24.04`. You'll want to overwrite a return address on stack. You can leak stack data until you get an address that points to back to stack. Once you find that, you'll have to figure out where that address points in stack - you can probably trial and error this. Once you find a return address, just overwrite it with the `execve` at `worker_exec + 8`. The you can just run the `./help` program in the `/bin/sh` shell.

## Debugging

The goal is to execute the debug program. There's a couple `.sh` scripts that you have `sudo` permissions on. You just have to create a symlink to `/printer/debug` and queue the file. That will update the permission to allow to execute the file as your current user.
