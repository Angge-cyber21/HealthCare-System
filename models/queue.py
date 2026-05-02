# models/queue.py
class Queue:
    def __init__(self):
        self.items_list = []

    def enqueue(self, item):
        self.items_list.append(item)

    def dequeue(self):
        if not self.items_list:
            return None
        return self.items_list.pop(0)

    def items(self):
        return self.items_list
