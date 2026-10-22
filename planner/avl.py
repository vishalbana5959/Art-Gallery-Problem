"""A small balanced search tree: insert, remove and neighbours in O(log n).

The sweep line supplies less(a, b), which compares two active edge numbers.
Rotations keep the height logarithmic, even for already sorted input.
"""


class Node:
    def __init__(self, key):
        self.key = key
        self.left = None
        self.right = None
        self.height = 1


def height(node):
    return node.height if node else 0


def update(node):
    node.height = 1 + max(height(node.left), height(node.right))


def rotate_left(node):
    top = node.right
    node.right = top.left
    top.left = node
    update(node)
    update(top)
    return top


def rotate_right(node):
    top = node.left
    node.left = top.right
    top.right = node
    update(node)
    update(top)
    return top


def balance(node):
    update(node)
    difference = height(node.left) - height(node.right)
    if difference > 1:
        if height(node.left.left) < height(node.left.right):
            node.left = rotate_left(node.left)
        return rotate_right(node)
    if difference < -1:
        if height(node.right.right) < height(node.right.left):
            node.right = rotate_right(node.right)
        return rotate_left(node)
    return node


class AVLTree:
    def __init__(self, less):
        self.root = None
        self.less = less

    def insert(self, key):
        self.root = self._insert(self.root, key)

    def _insert(self, node, key):
        if node is None:
            return Node(key)
        if key == node.key:
            raise RuntimeError("An active edge was inserted twice.")
        if self.less(key, node.key):
            node.left = self._insert(node.left, key)
        else:
            node.right = self._insert(node.right, key)
        return balance(node)

    def remove(self, key):
        self.root = self._remove(self.root, key)

    def _remove(self, node, key):
        if node is None:
            raise RuntimeError("An active edge could not be found.")
        if key == node.key:
            if node.left is None:
                return node.right
            if node.right is None:
                return node.left
            successor = node.right
            while successor.left:
                successor = successor.left
            node.key = successor.key
            node.right = self._remove(node.right, successor.key)
        elif self.less(key, node.key):
            node.left = self._remove(node.left, key)
        else:
            node.right = self._remove(node.right, key)
        return balance(node)

    def neighbours(self, key):
        """Return the keys immediately before and after an existing key."""
        before = after = None
        node = self.root
        while node:
            if key == node.key:
                if node.left:
                    child = node.left
                    while child.right:
                        child = child.right
                    before = child.key
                if node.right:
                    child = node.right
                    while child.left:
                        child = child.left
                    after = child.key
                return before, after
            if self.less(key, node.key):
                after = node.key
                node = node.left
            else:
                before = node.key
                node = node.right
        raise RuntimeError("Cannot find neighbours of a missing edge.")

    def last_before(self, is_before):
        """Find the last key satisfying a monotone left-of-query test."""
        answer = None
        node = self.root
        while node:
            if is_before(node.key):
                answer = node.key
                node = node.right
            else:
                node = node.left
        return answer
