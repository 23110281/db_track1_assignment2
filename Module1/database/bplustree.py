import bisect
import graphviz

class BPlusTreeNode:
    def __init__(self, is_leaf=False):
        self.is_leaf = is_leaf
        self.keys = []
        self.children = []
        self.next = None

class BPlusTree:
    def __init__(self, order=4):
        self.root = BPlusTreeNode(is_leaf=True)
        self.order = order

    def search(self, key):
        node = self.root
        while not node.is_leaf:
            i = bisect.bisect_right(node.keys, key)
            node = node.children[i]
        
        i = bisect.bisect_left(node.keys, key)
        if i < len(node.keys) and node.keys[i] == key:
            return node.children[i]
        return None

    def insert(self, key, value):
        root = self.root
        if len(root.keys) == self.order - 1:
            new_root = BPlusTreeNode(is_leaf=False)
            self.root = new_root
            new_root.children.append(root)
            self._split_child(new_root, 0)
            self._insert_non_full(new_root, key, value)
        else:
            self._insert_non_full(root, key, value)

    def _insert_non_full(self, node, key, value):
        if node.is_leaf:
            i = bisect.bisect_left(node.keys, key)
            if i < len(node.keys) and node.keys[i] == key:
                node.children[i] = value
            else:
                node.keys.insert(i, key)
                node.children.insert(i, value)
        else:
            i = bisect.bisect_right(node.keys, key)
            if len(node.children[i].keys) == self.order - 1:
                self._split_child(node, i)
                if key > node.keys[i]:
                    i += 1
            self._insert_non_full(node.children[i], key, value)

    def _split_child(self, parent, index):
        order = self.order
        node = parent.children[index]
        new_node = BPlusTreeNode(is_leaf=node.is_leaf)
        
        mid = order // 2
        
        if node.is_leaf:
            new_node.keys = node.keys[mid:]
            new_node.children = node.children[mid:]
            node.keys = node.keys[:mid]
            node.children = node.children[:mid]
            
            new_node.next = node.next
            node.next = new_node
            
            parent.keys.insert(index, new_node.keys[0])
            parent.children.insert(index + 1, new_node)
        else:
            new_node.keys = node.keys[mid+1:]
            new_node.children = node.children[mid+1:]
            up_key = node.keys[mid]
            node.keys = node.keys[:mid]
            node.children = node.children[:mid+1]
            
            parent.keys.insert(index, up_key)
            parent.children.insert(index + 1, new_node)

    def delete(self, key):
        if not self.root.keys:
            return False
            
        deleted = self._delete(self.root, key)
        
        # If the root becomes empty but has a child, make the child the new root
        if not self.root.keys and not self.root.is_leaf:
            self.root = self.root.children[0]
            
        return deleted

    def _delete(self, node, key):
        min_keys = (self.order // 2) - 1 if self.order % 2 == 0 else self.order // 2

        if node.is_leaf:
            i = bisect.bisect_left(node.keys, key)
            if i < len(node.keys) and node.keys[i] == key:
                node.keys.pop(i)
                node.children.pop(i)
                return True
            return False
        else:
            i = bisect.bisect_right(node.keys, key)
            deleted = self._delete(node.children[i], key)
            
            if deleted:
                if len(node.children[i].keys) < min_keys:
                    self._fill_child(node, i)
                    
            return deleted

    def _fill_child(self, node, index):
        min_keys = (self.order // 2) - 1 if self.order % 2 == 0 else self.order // 2
        
        # Try borrowing from previous sibling
        if index > 0 and len(node.children[index - 1].keys) > min_keys:
            self._borrow_from_prev(node, index)
            
        # Try borrowing from next sibling
        elif index < len(node.children) - 1 and len(node.children[index + 1].keys) > min_keys:
            self._borrow_from_next(node, index)
            
        # Merge if borrowing is not possible
        else:
            if index < len(node.children) - 1:
                self._merge(node, index)
            else:
                self._merge(node, index - 1)

    def _borrow_from_prev(self, node, index):
        child = node.children[index]
        sibling = node.children[index - 1]
        
        if child.is_leaf:
            child.keys.insert(0, sibling.keys.pop(-1))
            child.children.insert(0, sibling.children.pop(-1))
            node.keys[index - 1] = child.keys[0]
        else:
            child.keys.insert(0, node.keys[index - 1])
            node.keys[index - 1] = sibling.keys.pop(-1)
            child.children.insert(0, sibling.children.pop(-1))

    def _borrow_from_next(self, node, index):
        child = node.children[index]
        sibling = node.children[index + 1]
        
        if child.is_leaf:
            child.keys.append(sibling.keys.pop(0))
            child.children.append(sibling.children.pop(0))
            node.keys[index] = sibling.keys[0]
        else:
            child.keys.append(node.keys[index])
            node.keys[index] = sibling.keys.pop(0)
            child.children.append(sibling.children.pop(0))

    def _merge(self, node, index):
        child = node.children[index]
        sibling = node.children[index + 1]
        
        if child.is_leaf:
            child.keys.extend(sibling.keys)
            child.children.extend(sibling.children)
            child.next = sibling.next
            node.keys.pop(index)
            node.children.pop(index + 1)
        else:
            child.keys.append(node.keys.pop(index))
            child.keys.extend(sibling.keys)
            child.children.extend(sibling.children)
            node.children.pop(index + 1)

    def update(self, key, new_value):
        node = self.root
        while not node.is_leaf:
            i = bisect.bisect_right(node.keys, key)
            node = node.children[i]
        
        i = bisect.bisect_left(node.keys, key)
        if i < len(node.keys) and node.keys[i] == key:
            node.children[i] = new_value
            return True
        return False

    def range_query(self, start_key, end_key):
        node = self.root
        while not node.is_leaf:
            i = bisect.bisect_right(node.keys, start_key)
            node = node.children[i]
            
        results = []
        while node:
            for k, v in zip(node.keys, node.children):
                if start_key <= k <= end_key:
                    results.append((k, v))
                elif k > end_key:
                    return results
            node = node.next
        return results

    def get_all(self):
        node = self.root
        while not node.is_leaf:
            node = node.children[0]
            
        results = []
        while node:
            for k, v in zip(node.keys, node.children):
                results.append((k, v))
            node = node.next
        return results

    def visualize_tree(self):
        dot = graphviz.Digraph(comment='B+ Tree')
        dot.attr(rankdir='TB')
        if not self.root.keys:
            return dot
        self._add_nodes(dot, self.root)
        self._add_edges(dot, self.root)
        
        node = self.root
        while not node.is_leaf:
            if not node.children: break
            node = node.children[0]
            
        prev_name = None
        while node:
            node_name = str(id(node))
            if prev_name:
                dot.edge(prev_name, node_name, constraint='false', style='dashed')
            prev_name = node_name
            node = node.next
            
        return dot

    def _add_nodes(self, dot, node):
        node_name = str(id(node))
        # Build strict valid HTML labels to bypass flat edge GraphViz bugs
        cells = [f'<td port="f{i}">{str(k)}</td>' for i, k in enumerate(node.keys)]
        html_label = f'<<table border="1" cellborder="1" cellspacing="0"><tr>{"".join(cells)}</tr></table>>'
        dot.node(node_name, label=html_label, shape='none')
        if not node.is_leaf:
            for child in node.children:
                self._add_nodes(dot, child)

    def _add_edges(self, dot, node):
        if not node.is_leaf:
            node_name = str(id(node))
            for child in node.children:
                child_name = str(id(child))
                dot.edge(node_name, child_name)
                self._add_edges(dot, child)
