#!/usr/bin/env python3


import sys

NULL = None

def asnum(x):
    return int(x or 0)

OP = {
    "+": lambda x, y: asnum(x) + asnum(y),
    "*": lambda x, y: asnum(x) * asnum(y),
    "-": lambda x, y: asnum(x) - asnum(y),
}

def execute(st, sn):
    n = sn.pop()
    lvl = st[-n:]
    for _ in range(n):
        st.pop()

    print("LVL", lvl)
    x = lvl[0]
    for i in range(1, n - 1, 2):
        op = OP[lvl[i]]
        x = op(x, lvl[i + 1])
    if n % 2 == 0:
        op = OP[lvl[-1]]
        x = op(x, NULL)

    st.append(x)
    sn[-1] += 1


def push_cs(cs, sn, token):
    if not cs:
        return

    if sn[-1] == 0 and token == "punc":
        st.append(NULL); sn[-1] += 1
    st.append("".join(cs)); sn[-1] += 1


if __name__ == "__main__":
    x = " ".join(sys.argv[1:])

    sn, st = [0, 0], []

    cs = []
    token = None


    for c in x:
        if c.isnumeric():
            token_ = "number"
        elif c.isalpha() or c in "._":
            token_ = "alpha"
        elif c in "()":
            token_ = None
        elif c == " ":
            continue
        else:
            token_ = "punc"

        if token_ is None:
            push_cs(cs, sn, token)
            cs = []
        elif token == token_:
            cs.append(c)
        else:
            push_cs(cs, sn, token)
            cs = [c]

        token = token_

        if c == "(":
            sn += [0]
        elif c == ")":
            execute(st, sn)
            # TODO assert sn and sn[-1] >= 0

    push_cs(cs, sn, token)
    print(st, sn)
    execute(st, sn)


    print(st)
