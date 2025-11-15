class MemoryManager:
    def __init__(self):
        self.store = {}

    def add(self, key, value):
        """
        Overwrites key with value. For lists you can choose to extend instead.
        """
        self.store[key] = value

    def get(self, key, default=None):
        return self.store.get(key, default)

    def append(self, key, value):
        """
        Append value to a list at key; create list if not present.
        """
        if key not in self.store or not isinstance(self.store[key], list):
            self.store[key] = []
        self.store[key].append(value)

    def find(self, key, predicate):
        """
        Return items in a stored list satisfying predicate.
        """
        data = self.store.get(key, [])
        return [d for d in data if predicate(d)]
