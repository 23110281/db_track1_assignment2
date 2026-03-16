class DatabaseManager:
    def __init__(self):
        self.tables = {}

    def create_table(self, table_name, table):
        self.tables[table_name] = table

    def get_table(self, table_name):
        return self.tables.get(table_name)

    def drop_table(self, table_name):
        if table_name in self.tables:
            del self.tables[table_name]
