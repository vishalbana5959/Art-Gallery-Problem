"""Shared sweep-line status and O(n log n) polygon simplicity checking."""

from .avl import AVLTree
from .geometry import segments_intersect, sweep_heights


class SweepStatus:
    def __init__(self, points, heights):
        self.y = 0
        self.above = False
        self.edges = []
        for i in range(len(points)):
            j = (i + 1) % len(points)
            low, high = (i, j) if heights[i] < heights[j] else (j, i)
            self.edges.append((points[low][0], heights[low],
                               points[high][0] - points[low][0],
                               heights[high] - heights[low]))
        self.tree = AVLTree(self.less)

    def x_fraction(self, edge):
        x, y, dx, dy = self.edges[edge]
        # Intersection x coordinate = numerator / denominator; dy > 0.
        return x * dy + (self.y - y) * dx, dy

    def less(self, a, b):
        na, da = self.x_fraction(a)
        nb, db = self.x_fraction(b)
        difference = na * db - nb * da
        if difference:
            return difference < 0
        # At a shared endpoint, order by slope just above/below the event.
        slope = self.edges[a][2] * db - self.edges[b][2] * da
        if slope:
            return slope < 0 if self.above else slope > 0
        return a < b

    def left_of(self, x):
        def before(edge):
            numerator, denominator = self.x_fraction(edge)
            return numerator < x * denominator
        edge = self.tree.last_before(before)
        if edge is None:
            raise RuntimeError("No left boundary found during partitioning.")
        return edge


def check_simple(points):
    """Reject non-neighbouring edges that cross, touch or overlap.

    Whenever two edges become neighbours, check their WHOLE segments.
    Therefore the first illegal intersection is found before it can change
    the active ordering. Legal adjacent endpoint contacts are ignored here;
    adjacent overlap/backtracking is checked during input preparation.
    """
    n = len(points)
    heights = sweep_heights(points)
    status = SweepStatus(points, heights)

    def check(a, b):
        if a is None or b is None:
            return
        if (a + 1) % n == b or (b + 1) % n == a:
            return
        if segments_intersect(points[a], points[(a + 1) % n],
                              points[b], points[(b + 1) % n]):
            raise ValueError("Boundary edges cross or touch. Use a simple polygon without holes.")

    for v in sorted(range(n), key=lambda i: heights[i], reverse=True):
        status.y = heights[v]
        status.above = True
        incident = [((v - 1) % n, (v - 1) % n), (v, (v + 1) % n)]
        for edge, other in incident:
            if heights[other] > heights[v]:
                left, right = status.tree.neighbours(edge)
                check(left, edge)
                check(edge, right)
                status.tree.remove(edge)
                check(left, right)
        status.above = False
        for edge, other in incident:
            if heights[other] < heights[v]:
                status.tree.insert(edge)
                left, right = status.tree.neighbours(edge)
                check(left, edge)
                check(edge, right)
