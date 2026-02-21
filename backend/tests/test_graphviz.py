from graphviz import Digraph

d = Digraph()
d.node("A", "A")
d.node("B", "B")
d.edge("A", "B")

d.render("venv_test", format="png", cleanup=True)
print("Graphviz OK")