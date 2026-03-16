import graphviz
from database.bplustree import BPlusTree

bpt = BPlusTree(order=4)
keys = [10, 20, 5, 6, 12, 30, 7, 17]
for k in keys:
    bpt.insert(k, f"Value_{k}")

dot = bpt.visualize_tree()
try:
    dot.render('/tmp/test_gv', format='svg')
    print("SUCCESS")
except Exception as e:
    print(f"FAILED: {e}")
    print("Source was:")
    print(dot.source)
