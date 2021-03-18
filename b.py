#!/usr/bin/env python3

import sys
from dataclasses import dataclass

NIL = None

class Value:
    def __init__(self, v): self.v = v
class Block(Value):
    def __repr__(self):
        return f"[{self.v}]"
class Builtin(Value):
    def __init__(self, fn):
        self.fn = fn
    def __repr__(self):
        return f"builtin()"
class Special(Builtin):
    def __repr__(self):
        return f"special()"
class Function(Value):
    def __init__(self, xname, yname, body, env):
        self.xname = xname
        self.yname = yname
        self.env = env
        self.body = body
    def __repr__(self):
        return f"func()"
class Quote(Value):
    def __repr__(self):
        return f"\[{self.v}]"
class Unquote(Value):
    def __repr__(self):
        return f"/[{self.v}]"
class Var(Value):
    def __repr__(self):
        return f"{{{self.v}}}"
class Array(Value):
    def __repr__(self):
        return "[" + " ".join(map(str, self.v)) + "]"
class Cons(Value):
    def __repr__(self):
        return f"({self.v[0]}, {self.v[1]})"

def else_(a, b, _):
    if a == NIL:
        return b
    return a

def mkfunc(a, b, env):
    if isinstance(a, Cons):
        xname, yname = a.v
    else:
        xname, yname = a.v, None
    return Function(str(xname), str(yname), b, env)

def mkarray(a, b):
    if isinstance(a, Array):
        a.v.append(b)
        return a
    return Array([a, b])


OPS = {
    "~":  Builtin(lambda a, b: a + b),
    "+":  Builtin(lambda a, b: toint(a) + toint(b)),
    "*":  Builtin(lambda a, b: toint(a) * toint(b)),
    "-":  Builtin(lambda a, b: toint(a) - toint(b)),
    ":":  Builtin(lambda a, b: Cons((a, b))),
    ",":  Builtin(mkarray),
    "\\": Special(lambda a, b, env: b),
    "|":  Special(else_),
    "->": Special(mkfunc),
}

ASSOC = {
    # (associativity_precedence, right_associativity)
    "+": (5, 0),
    "*": (6, 0),
    ":": (4, 1),
    ",": (3, 0),
    "|": (0, 1),
    "->": (0, 1),
}

def flush_til(res, ops, assoc):
    R = res.pop()
    while ops:
        if ops[-1][1] < assoc:
            break
        H = ops.pop()[0]
        L = res.pop()
        R = [L, H, R]
    return R

def shunt(xs):
    res, ops = [], []
    assert xs

    res.append(xs[0])
    for i in range(1, len(xs) - 1, 2):
        H = xs[i]
        R = xs[i + 1]

        assoc, right = 5, 0
        if isinstance(H, str) and H in ASSOC:
            assoc, right = ASSOC[H]

        res.append(flush_til(res, ops, assoc + right))
        res.append(R)
        ops.append((H, assoc))

    return flush_til(res, ops, -1)


def interpret(start_paren, quote, buf):
    if buf is None:
        buf = NIL
    elif start_paren in "(\0":
        buf = shunt(buf)
    elif start_paren == "{":
        buf[0] = Var(buf[0])
        buf = shunt(buf)
    elif start_paren == "[":
        if quote:
            buf = Quote(buf)
        else:
            buf = Array(buf)

    if quote and start_paren != "[":
        buf = Unquote(buf)

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


def _finalize(buf, leading_punct, start_paren, end_paren, quote):
    if opposite_paren(start_paren) != end_paren:
        raise ValueError(f"Parens don't match: {start_paren} <> {end_paren}")
    if len(buf) < 1:
        buf = None
    elif len(buf) > 1:
        if leading_punct:
            buf = [None, *buf]
        if len(buf) % 2 == 0:
            buf = [*buf, None]

    buf = interpret(start_paren, quote, buf)
    return buf


# TODO expected_end has to match
def parse(i, start_paren, quote, cs, xs):
    assert not cs
    buf = []
    token = None
    leading_punct = False

    while i[0] + 1 < len(xs):
        i[0] += 1
        c, c1 = xs[i[0]], xs[i[0] + 1]

        if c.isalnum() or c in "._":
            new_token = "symbol"
        elif c in '"()[]{}\0 ':
            new_token = None
        else:
            new_token = "punct"

        if new_token != token and token is not None:
            if len(buf) == 0 and token == "punct":
                leading_punct = True
            buf.append("".join(cs))
            cs.clear()

        if token is None: assert not cs

        if new_token is not None:
            cs.append(c)

        token = new_token

        if c == " ":
            continue
        if c == '"':
            x = parse_string(i, cs, xs)
            cs.clear()
            buf.append(x)
        if c in "([{":
            if c1 == "|":
                quote_ = True
                i[0] += 1
            else:
                quote_ = False
            x = parse(i, c, quote_, cs, xs)
            cs.clear()
            buf.append(x)
        elif c == "|" and c1 in ")]}":
            i[0] += 1
            c, c1 = xs[i[0]], xs[i[0] + 1]
            return _finalize(buf, leading_punct, start_paren, c, quote)
        elif c in ")]}\0":
            return _finalize(buf, leading_punct, start_paren, c, quote)

    assert False


def toint(x):
    if x is None:
        return 0
    return int(x)

def quasiquote(x, env):
    if isinstance(x, list):
        return [quasiquote(x_, env) for x_ in x]
    elif isinstance(x, Unquote):
        return exe(x.v, env)
    else:
        return x

def envget(env, key):
    while env is not None:
        cur, nxt = env
        if key in cur:
            return cur[key]
        env = nxt
    return None

def exe(x, env):
    while True:
        if isinstance(x, list):
            assert len(x) == 3
            L = exe(x[0], env)
            H = exe(x[1], env)
            R = x[2]

            # TODO handle specials before evaluating R

            if isinstance(H, str):
                # TODO variable resolution on H position
                H = envget(env, H)

            if isinstance(H, Special):
                x = H.fn(L, R, env)
                continue

            R = exe(R, env)

            if H is NIL:
                x = L
            elif isinstance(H, Builtin):
                # TODO check op dispatch
                x = H.fn(L, R)
            elif isinstance(H, Function):
                # TODO grab varnames from function
                # TODO tail-call optimization
                env_ = {}
                if H.xname is not None:
                    env_[H.xname] = L
                if H.yname is not None:
                    env_[H.yname] = R
                env = (env_, H.env)
                x = H.body
            else:
                print("H type:", type(H).__name__)
                assert False
                pass
                # TODO handle unhandled H type
        elif isinstance(x, Var):
            x = envget(env, x.v)
        elif isinstance(x, Unquote):
            x = x.v
        elif isinstance(x, Quote):
            return Block(quasiquote(x.v, env))
        elif isinstance(x, Block):
            return x
        else:
            return x



if __name__ == "__main__":
    x = " ".join(sys.argv[1:])
    x += "\0\0"

    i, cs = [-1], []
    print("X", x)
    y = parse(i, "\0", False, cs, x)
    print("Y", y)

    env = {
        "A": 123,
        **OPS,
    }
    env = (env, None)
    z = exe(y, env)
    print("Z", z)
