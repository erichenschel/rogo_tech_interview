
from .term_index import TermIndex, Term

class TreeNode:
    def __init__(self):
        self.children = {}
        self.leaf = False

class Autocompleter:

    def __init__(self, term_index: TermIndex) -> None:
        self.term_index = term_index
        self.root = TreeNode()

        self.form_prefix_tree()

    def form_prefix_tree(self) -> None:
        all_terms = self.term_index.all_terms
        for term in all_terms:
            self.insert(term.value)

    def insert(self, term: str) -> None:
        node = self.root

        # for each character in the term, add a node to the prefix tree
        for char in term:
            if not node.children.get(char):
                node.children[char] = TreeNode()
            node = node.children[char]

        node.leaf = True


    def recall(self, node: TreeNode, char: str, results: list) -> list[str]:
        if node.leaf:
            results.append(char)

        for tree_char, tree_node in node.children.items():
            self.recall(tree_node, char + tree_char, results)

        return results

    def flatten(self, ls: list) -> list[list[Term]]:
        out = []
        for i in ls:
            if type(i) == list:
                out.extend(i)
            else:
                out.append(i)
        return out

    def unpack_result(self, result: list) -> list[list[Term]]:
        final_result = []
        tmp_result = [[]]

        for layer in result:
            final_result = tmp_result
            tmp_result = [[]]

            for item in layer:
                for res in final_result:
                    new_item = [res]
                    
                    if new_item == [[]]:
                        new_item = [Term(value=item)]
                    else:
                        new_item = [new_item[0], Term(value=item)]
                    tmp_result.append(self.flatten(new_item))
        
        final_result = list(filter(lambda x: len(x)==len(result), tmp_result))
        return final_result

    def suggestions(self, input: str) -> list[list[Term]]:

        # Case 1: handle empty input
        if not input:
            return []
        
        tmp_result = []
        tmp_term = ""
        node = self.root

        # get all possibilities for each layer
        for char in input:
            if not node.children.get(char):
                # takes care of partials and complete
                if char == " ":
                    result = self.recall(node, tmp_term, [])
                    tmp_result.append(result)
                    tmp_term = ""
                    node = self.root
                    continue
                return []
            
            tmp_term+=char
            node = node.children[char]

        # takes care of last string in input
        result = self.recall(node, tmp_term, [])
        tmp_result.append(result)

        # format the result
        final_results = self.unpack_result(tmp_result)

        return final_results
