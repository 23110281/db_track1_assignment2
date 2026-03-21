from .bplustree import BPlusTree

class Table:
    def __init__(self, name):
        self.name = name
        self.index = BPlusTree()

    def insert(self, key, record):
        self.index.insert(key, record)

    def select(self, key):
        return self.index.search(key)

    def delete(self, key):
        return self.index.delete(key)

    def update(self, key, new_record):
        return self.index.update(key, new_record)

    def range_query(self, start_key, end_key):
        return self.index.range_query(start_key, end_key)
