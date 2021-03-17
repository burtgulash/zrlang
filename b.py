#!/usr/bin/env python3

import sys
from dataclasses import dataclass

NIL = None

class Value:
    def __init__(self, v): self.v = v
class Var(Value): pass
class Array(Value):
    def __repr__(self):
        return "[" + " ".join(map(str, self.v)) + "]"

def interpret(start_paren, buf):
    if buf is None:
        return NIL
    elif start_paren == "(":
        # TODO shunting yard
        y = buf
        return y
    elif start_paren == "[":
        return Array(buf)
    elif start_paren == "{":
        buf[0] = Var(buf[0])

    elif start_paren == "[|":

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


def opposite_paren(start):
    return ")]}\0"["([{\0".index(start)]


def _finalize(buf, leading_punct, start_paren, end_paren):
    if opposite_paren(start_paren) != end_paren:
        raise ValueError(f"Parens don't match: {start_paren} <> {end_paren}")
    if len(buf) < 1:
        buf = None
    elif len(buf) > 1:
        if leading_punct:
            buf = [None, *buf]
        if len(buf) % 2 == 0:
            buf = [*buf, None]

    buf = interpret(start_paren, buf)
    return buf


# TODO expected_end has to match
def parse(i, start_paren, quote, cs, xs):
    assert not cs
    buf = []
    token = None
    leading_punct = False

    while i[0] + 1 < len(xs) - 1:
        i[0] += 1
        c, c1 = xs[i[0]], xs[i[0] + 1]

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
        if c in "([{":
            if c1 == "|":
                quote = True
                i[0] += 1
            else:
                quote = False
            x = parse(i, c, quote, cs, xs)
            cs.clear()
            buf.append(x)
        elif c == "|" and c1 in ")]}":
            i[0] += 1
            return _finalize(buf, leading_punct, start_paren, xs[i[0]])
        elif c in ")]}":
            return _finalize(buf, leading_punct, start_paren, c)

    i[0] += 1
    assert i[0] == len(xs) - 1
    assert xs[i[0]] == "\0"
    return _finalize(buf, leading_punct, start_paren, "\0")



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
            None: lambda a, b: a, # NOP
        }[H]

        L = op(L, R)

    return L



if __name__ == "__main__":
    x = " ".join(sys.argv[1:])
    x += "\0"

    i, cs = [-1], []
    print("X", x)
    y = parse(i, "\0", False, cs, x)
    print("Y", y)

    z = exe(y)
    print("Z", z)
