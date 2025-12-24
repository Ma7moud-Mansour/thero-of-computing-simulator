def parse_string(grammar, string):
    def derive(symbol, pos):
        if pos > len(string):
            return None

        if symbol not in grammar.productions:
            if pos < len(string) and symbol == string[pos]:
                return pos + 1
            return None

        for production in grammar.productions[symbol]:
            cur = pos
            for sym in production:
                cur = derive(sym, cur)
                if cur is None:
                    break
            if cur is not None:
                return cur
        return None

    result = derive(grammar.start, 0)
    return result == len(string)

from cfg.parse_tree import ParseTreeNode

def parse_with_tree(grammar, string):
    def derive(symbol, pos):
        node = ParseTreeNode(symbol)


        if symbol not in grammar.productions:
            if pos < len(string) and symbol == string[pos]:
                return node, pos + 1
            return None, pos


        for production in grammar.productions[symbol]:
            cur_pos = pos
            children = []
            valid = True

            for sym in production:
                child, cur_pos = derive(sym, cur_pos)
                if child is None:
                    valid = False
                    break
                children.append(child)
            
            if valid and not production:
                children.append(ParseTreeNode("ε"))

            if valid:
                node.children = children
                return node, cur_pos

        return None, pos

    tree, pos = derive(grammar.start, 0)
    if tree and pos == len(string):
        return True, tree

    return False, None
