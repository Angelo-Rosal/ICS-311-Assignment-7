import mainVer2 as m

cases = [
    "aaabbbbccaaa",
    "",
    "Hellooo!!!",
    "A"*256,
    "jjjjjjjjjjjdddddddddddddddddweeeeeeeeeeeeeeeeeeeeeeeeeeeeffffffffeeeeegggggbbbbbbb",
]

g = m.Graph()
a = g.add_person("A")
b = g.add_person("B")

for s in cases:
    msg = m.send_rle(g, a.id, b.id, s)
    back = m.recv_rle(msg)
    print(repr(s), "=>", msg.body, "=>", repr(back))
print("----------FINISHED----------")
