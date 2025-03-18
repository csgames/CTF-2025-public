#!/usr/bin/env python

import signal

from pfs.emu import PFSEMU


signal.signal(signal.SIGALRM, lambda x, y: exit(1))


def main():
    with open("/app/challenge.sx") as h:
        rom = [int(v) for v in h.read().split(" ")]
    
    emu = PFSEMU(rom)

    signal.alarm(30)    

    try:
        while emu.step():
            continue
    except:
        pass


if __name__ == "__main__":
    main()
