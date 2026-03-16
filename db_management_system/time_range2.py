import time
import random
from database.bplustree import BPlusTree
from database.bruteforce import BruteForceDB

# Higher order like a real database page
bpt = BPlusTree(order=100)
bf = BruteForceDB()

keys = random.sample(range(1, 1000000), 100000)
for k in keys:
    bpt.insert(k, k)
    bf.insert(k)

# Narrow query to highlight O(log N) vs O(N)
ranges = [(random.randint(10000, 800000), 0) for _ in range(100)]
ranges = [(s, s + 100) for s, _ in ranges]

start = time.time()
for s, e in ranges:
    bf.range_query(s, e)
print("BruteForce (Narrow Ranges):", time.time() - start)

start = time.time()
for s, e in ranges:
    bpt.range_query(s, e)
print("BPlusTree (Narrow Ranges):", time.time() - start)

