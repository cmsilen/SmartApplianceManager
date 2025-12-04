class RecordsBuffer:
    def __init__(self):
        self.stored_records = {}

    def store_record(self, record, record_type):
        if record_type not in self.stored_records:
            self.stored_records[record_type] = []
        self.stored_records[record_type].append(record)

    def get_records(self):
        return self.stored_records

    def get_records_count(self):
        total = 0
        for record_type in self.stored_records:
            total += len(self.stored_records[record_type])
        return total

    def delete_records(self):
        self.stored_records = {}
