#!/usr/bin/env python3

import sys
from dataclasses import dataclass

NIL = None

class Value:
    def __init__(self, v): self.v = v
class Var(Value): pass
class Array(Value): pass

def interpret(block_type, buf):
    if len(buf) == 0:
        return NIL
    elif block_type == "(":
        # TODO shunting yard
        y = buf
        return y
    elif block_type == "[":
        return Array(buf)
    elif block_type == "{":
        buf[0] = Var(buf[0])

    elif block_type == "[|":

        pass

        #(x, y => {x}, {y} = {{y}}, {{x}})
        #[| 1 + {| x |} + 3 |]
        #foo = (x, y -> {|x|} + {y})


    return buf

def parse_string(i, cs, xs):
    assert len(cs) == 0
    escape = False
    while i[0] < len(xs):
        i[0] += 1
        c = xs[i[0]]

        if escape:
            if c == "n":
                cs.append("\n")
            elif c == "t":
                cs.append("\t")
            elif c == '"':
                cs.append(c)
            elif c == "\\":
                cs.append(c)
            else:
                raise ValueError(f"invalid escape in string: \{c}")
            escape = False
            continue

        if c == '"':
            return "".join(cs)
        if c == "\\":
            escape = True
            continue

        cs.append(c)

    cs = "".join(cs)
    raise ValueError(f"unterminated string: {cs}")

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
        if c == '"':
            x = parse_string(i, cs, xs)
            cs.clear()
            buf.append(x)
        if c == "(":
            x = parse(i, cs, xs)
            cs.clear()
            buf.append(x)
        elif c in ")\0":
            if len(buf) < 1:
                buf = None
            elif len(buf) > 1:
                if leading_punct:
                    buf = [None, *buf]
                if len(buf) % 2 == 0:
                    buf = [*buf, None]

            buf = interpret("(", buf)
            return buf

def toint(x):
    if x is None:
        return 0
    return int(x)


def exe_(x):
    if isinstance(x, list):
        return exe(x)
    return x



def exe(xs):
    assert len(xs) % 2 == 1

    L = exe_(xs[0])
    for i in range(1, len(xs), 2):
        H = exe_(xs[i])
        R = exe_(xs[i + 1])

        op = {
            "~": lambda a, b: a + b,
            "+": lambda a, b: toint(a) + toint(b),
            "*": lambda a, b: toint(a) * toint(b),
            "-": lambda a, b: toint(a) - toint(b),
        }[H]

        L = op(L, R)

    return L



if __name__ == "__main__":
    x = " ".join(sys.argv[1:])
    x += "\0"

    i, cs = [-1], []
    print("X", x)
    y = parse(i, cs, x)
    print("Y", y)

    z = exe(y)
    print("Z", z)
