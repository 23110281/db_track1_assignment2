import time
import random
from database.bplustree import BPlusTree
from database.bruteforce import BruteForceDB

bpt = BPlusTree()
bf = BruteForceDB()

keys = random.sample(range(1, 100000), 10000)
for k in keys:
    bpt.insert(k, k)
    bf.insert(k)

ranges = [(random.randint(1, 40000), random.randint(60000, 100000)) for _ in range(10)]

start = time.time()
for s, e in ranges:
    bf.range_query(s, e)
print("BruteForce:", time.time() - start)

start = time.time()
for s, e in ranges:
    bpt.range_query(s, e)
print("BPlusTree:", time.time() - start)
