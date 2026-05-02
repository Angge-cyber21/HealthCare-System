class TreeNode:
    def __init__(self, name, data=None):
        self.name = name      # e.g., "Hospital", "Cardiology", "John Doe"
        self.data = data      # Store department or patient info
        self.children = []    # List of child TreeNodes

    def add_child(self, node):
        self.children.append(node)

    # Optional: Traversal methods
    def traverse_preorder(self):
        print(self.name)
        for child in self.children:
            child.traverse_preorder()
