import time
import tracemalloc
from .bplustree import BPlusTree
from .bruteforce import BruteForceDB

class PerformanceAnalyzer:
    def __init__(self):
        pass

    def measure_time_and_memory(self, func, *args):
        """Measures the execution time and peak memory usage of a function."""
        tracemalloc.start()
        start_time = time.time()
        
        result = func(*args)
        
        end_time = time.time()
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        execution_time = end_time - start_time
        return execution_time, peak

    def profile_insertion(self, keys):
        bpt = BPlusTree(order=50)
        def insert_bpt():
            for k in keys:
                bpt.insert(k, k)
        bpt_time, bpt_mem = self.measure_time_and_memory(insert_bpt)

        bf = BruteForceDB()
        def insert_bf():
            for k in keys:
                bf.insert(k)
        bf_time, bf_mem = self.measure_time_and_memory(insert_bf)

        return {
            'bplus_tree': {'time': bpt_time, 'memory': bpt_mem, 'instance': bpt},
            'bruteforce': {'time': bf_time, 'memory': bf_mem, 'instance': bf}
        }
        
    def profile_search(self, bpt, bf, keys_to_search):
        def search_bpt():
            for k in keys_to_search:
                bpt.search(k)
        bpt_time, bpt_mem = self.measure_time_and_memory(search_bpt)

        def search_bf():
            for k in keys_to_search:
                bf.search(k)
        bf_time, bf_mem = self.measure_time_and_memory(search_bf)

        return {
            'bplus_tree': {'time': bpt_time, 'memory': bpt_mem},
            'bruteforce': {'time': bf_time, 'memory': bf_mem}
        }

    def profile_deletion(self, bpt, bf, keys_to_delete):
        def delete_bpt():
            for k in keys_to_delete:
                bpt.delete(k)
        bpt_time, bpt_mem = self.measure_time_and_memory(delete_bpt)

        def delete_bf():
            for k in keys_to_delete:
                bf.delete(k)
        bf_time, bf_mem = self.measure_time_and_memory(delete_bf)

        return {
            'bplus_tree': {'time': bpt_time, 'memory': bpt_mem},
            'bruteforce': {'time': bf_time, 'memory': bf_mem}
        }

    def profile_range_query(self, bpt, bf, ranges):
        def range_bpt():
            for start, end in ranges:
                bpt.range_query(start, end)
        bpt_time, bpt_mem = self.measure_time_and_memory(range_bpt)

        def range_bf():
            for start, end in ranges:
                bf.range_query(start, end)
        bf_time, bf_mem = self.measure_time_and_memory(range_bf)

        return {
            'bplus_tree': {'time': bpt_time, 'memory': bpt_mem},
            'bruteforce': {'time': bf_time, 'memory': bf_mem}
        }
