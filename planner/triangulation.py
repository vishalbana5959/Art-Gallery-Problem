"""Sweep into monotone pieces, then triangulate each piece with a stack."""

from functools import cmp_to_key

from .geometry import area_twice, cross, sweep_heights
from .sweep import SweepStatus


def monotone_diagonals(points, heights):
    n = len(points)
    kinds = []
    for v in range(n):
        previous, following = (v - 1) % n, (v + 1) % n
        convex = cross(points[previous], points[v], points[following]) > 0
        if heights[previous] < heights[v] > heights[following]:
            kinds.append("start" if convex else "split")
        elif heights[previous] > heights[v] < heights[following]:
            kinds.append("end" if convex else "merge")
        else:
            kinds.append("regular")

    status = SweepStatus(points, heights)
    helper = [-1] * n
    diagonals = []

    def connect_merge(v, edge):
        h = helper[edge]
        if h < 0:
            raise RuntimeError("Missing helper vertex.")
        if kinds[h] == "merge":
            diagonals.append((v, h))

    for v in sorted(range(n), key=lambda i: heights[i], reverse=True):
        previous, following = (v - 1) % n, (v + 1) % n
        status.y = heights[v]
        kind = kinds[v]

        if kind == "start":
            status.tree.insert(v)
            helper[v] = v
        elif kind == "end":
            connect_merge(v, previous)
            status.tree.remove(previous)
        elif kind == "split":
            left = status.left_of(points[v][0])
            diagonals.append((v, helper[left]))
            helper[left] = v
            status.tree.insert(v)
            helper[v] = v
        elif kind == "merge":
            connect_merge(v, previous)
            status.tree.remove(previous)
            left = status.left_of(points[v][0])
            connect_merge(v, left)
            helper[left] = v
        elif heights[following] < heights[v]:
            # A regular vertex on a left boundary replaces its active edge.
            connect_merge(v, previous)
            status.tree.remove(previous)
            status.tree.insert(v)
            helper[v] = v
        else:
            left = status.left_of(points[v][0])
            connect_merge(v, left)
            helper[left] = v
    return diagonals


def collect_faces(points, diagonals):
    """Walk faces without repeatedly copying/splitting whole polygon lists.

    Store each edge in both directions in ordinary lists. The reverse of
    directed edge h is h ^ 1 (0 and 1, 2 and 3, ...). At a vertex, take the
    outgoing edge just clockwise from the reverse to keep the face on the left.
    """
    n = len(points)
    edges = [(i, (i + 1) % n) for i in range(n)] + diagonals
    starts, ends = [], []
    outgoing = [[] for _ in points]
    for a, b in edges:
        for u, v in ((a, b), (b, a)):
            outgoing[u].append(len(starts))
            starts.append(u)
            ends.append(v)
    next_edge = [-1] * len(starts)

    def angle_compare(a, b):
        origin = points[starts[a]]
        pa, pb = points[ends[a]], points[ends[b]]
        ax, ay = pa[0] - origin[0], pa[1] - origin[1]
        bx, by = pb[0] - origin[0], pb[1] - origin[1]
        half_a = 0 if ay > 0 or (ay == 0 and ax >= 0) else 1
        half_b = 0 if by > 0 or (by == 0 and bx >= 0) else 1
        if half_a != half_b:
            return half_a - half_b
        turn = ax * by - ay * bx
        if turn:
            return -1 if turn > 0 else 1
        raise RuntimeError("Overlapping edges in the monotone subdivision.")

    for around in outgoing:
        around.sort(key=cmp_to_key(angle_compare))
        for i, edge in enumerate(around):
            next_edge[edge ^ 1] = around[i - 1]

    visited = [False] * len(starts)
    faces = []
    for first in range(len(starts)):
        if visited[first]:
            continue
        face = []
        edge = first
        while not visited[edge]:
            visited[edge] = True
            face.append(starts[edge])
            edge = next_edge[edge]
        if edge != first:
            raise RuntimeError("Invalid subdivision boundary.")
        if area_twice([points[v] for v in face]) > 0:
            faces.append(face)  # The outside face has clockwise orientation.
    return faces


def triangulate_monotone(points, heights, face):
    """O(m log m) sorting plus O(m) stack work for an m-vertex piece.

    Sorting each piece is simpler than merging its two boundary chains;
    total time is still O(n log n), since total piece size is O(n).
    """
    m = len(face)
    order = sorted(range(m), key=lambda i: heights[face[i]], reverse=True)
    top, bottom = order[0], order[-1]
    left_length = (bottom - top) % m
    left_chain = [(i - top) % m < left_length for i in range(m)]
    triangles = []

    # Verify both boundary chains descend; this check is linear in piece size.
    for step in (1, -1):
        i = top
        while i != bottom:
            j = (i + step) % m
            if heights[face[j]] >= heights[face[i]]:
                raise RuntimeError("Partition produced a non-monotone piece.")
            i = j

    def add(a, b, c):
        a, b, c = face[a], face[b], face[c]
        turn = cross(points[a], points[b], points[c])
        if turn == 0:
            raise RuntimeError("A zero-area triangle was produced.")
        triangles.append((a, b, c) if turn > 0 else (a, c, b))

    stack = order[:2]
    for position in range(2, m - 1):
        current = order[position]
        if left_chain[current] != left_chain[stack[-1]]:
            while len(stack) > 1:
                last = stack.pop()
                add(current, last, stack[-1])
            stack = [order[position - 1], current]
        else:
            last = stack.pop()
            while stack:
                turn = cross(points[face[current]], points[face[last]],
                             points[face[stack[-1]]])
                inside = turn < 0 if left_chain[current] else turn > 0
                if not inside:
                    break
                add(current, last, stack[-1])
                last = stack.pop()
            stack.extend([last, current])
    while len(stack) > 1:
        last = stack.pop()
        add(bottom, last, stack[-1])
    return triangles


def triangulate(points):
    heights = sweep_heights(points)
    diagonals = monotone_diagonals(points, heights)
    faces = collect_faces(points, diagonals)
    triangles = []
    for face in faces:
        triangles.extend(triangulate_monotone(points, heights, face))
    return triangles, diagonals, len(faces)
