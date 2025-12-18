class ParseTreeNode:
    def __init__(self, symbol):
        self.symbol = symbol
        self.children = []

    def add_child(self, node):
        self.children.append(node)
