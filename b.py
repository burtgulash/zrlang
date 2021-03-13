#!/usr/bin/env python3

import sys

def interpret(buf):
    return buf


def parse(i, cs, xs):
    assert not cs
    buf = []
    token = None
    leading_punct = False

    while i[0] < len(xs):
        i[0] += 1
        c = xs[i[0]]

        if c.isalnum() or c in "._":
            token_ = "symbol"
        elif c in '"()[]{}\0 ':
            token_ = None
        else:
            token_ = "punct"

        if token_ != token and token is not None:
            if len(buf) == 0 and token == "punct":
                leading_punct = True
            buf.append("".join(cs))
            cs.clear()

        if token is None: assert not cs

        if token_ is not None:
            cs.append(c)

        token = token_

        if c == " ":
            continue
        if c == "(":
            x = parse(i, cs, xs)
            buf.append(x)
        elif c in ")\0":
            if len(buf) < 1:
                buf = None
            elif len(buf) > 1:
                if leading_punct:
                    buf = [None, *buf]
                if len(buf) % 2 == 0:
                    buf = [*buf, None]

            buf = interpret(buf)
            return buf





if __name__ == "__main__":
    x = " ".join(sys.argv[1:])
    x += "\0"

    i, cs = [-1], []
    print("X", x)
    y = parse(i, cs, x)
    print("Y", y)
