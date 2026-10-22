"""Public solver: worst-case O(n log n) time and O(n) extra space."""

from pathlib import Path

from .coloring import color_vertices
from .geometry import area_twice, cross
from .sweep import check_simple
from .triangulation import triangulate


def prepare_polygon(points):
    if len(points) < 3:
        raise ValueError("Use at least three vertices in boundary order.")
    for p in points:
        if (not isinstance(p, (list, tuple)) or len(p) != 2
                or any(type(value) is not int or abs(value) > 1000000 for value in p)):
            raise ValueError("Each point needs two integers between -1000000 and 1000000.")
    points = [tuple(p) for p in points]
    ids = list(range(1, len(points) + 1))
    if points[0] == points[-1]:
        points.pop()
        ids.pop()
    ordered = sorted(points)
    if len(points) < 3 or any(ordered[i] == ordered[i - 1] for i in range(1, len(ordered))):
        raise ValueError("At least three distinct vertices are needed; repeated vertices are invalid.")
    n = len(points)
    keep = []
    for i in range(n):
        a, b, c = points[i - 1], points[i], points[(i + 1) % n]
        turn = cross(a, b, c)
        if turn == 0:
            dot = (a[0] - b[0]) * (c[0] - b[0]) + (a[1] - b[1]) * (c[1] - b[1])
            if dot > 0:
                raise ValueError(f"Edges overlap or turn back at V{ids[i]}.")
        else:
            keep.append(i)
    # Validate BEFORE removing collinear points, so illegal contacts cannot vanish.
    check_simple(points)
    if area_twice(points) == 0:
        raise ValueError("The room must have nonzero area.")
    # Removing straight intermediate points does not alter other turn directions.
    points, ids = [points[i] for i in keep], [ids[i] for i in keep]
    if area_twice(points) < 0:
        points.reverse()
        ids.reverse()
    return points, ids


def solve(points):
    input_count = len(points)
    points, ids = prepare_polygon(points)
    triangles, diagonals, piece_count = triangulate(points)
    n = len(points)
    if len(triangles) != n - 2:
        raise RuntimeError("Triangle count check failed.")
    colors = color_vertices(n, triangles)
    smallest = min(range(3), key=colors.count)
    cameras = [v for v in range(n) if colors[v] == smallest]
    owners = [next(v for v in t if colors[v] == smallest) for t in triangles]
    if len(cameras) > n // 3:
        raise RuntimeError("Camera bound check failed.")
    total_area = 0
    for triangle in triangles:
        if sorted(colors[v] for v in triangle) != [0, 1, 2]:
            raise RuntimeError("Triangle colouring check failed.")
        area = cross(*(points[v] for v in triangle))
        if area <= 0:
            raise RuntimeError("A triangle has nonpositive area.")
        total_area += area
    if total_area != area_twice(points):
        raise RuntimeError("Triangle areas do not add up to the room area.")
    return {"points": points, "vertex_ids": ids, "triangles": triangles,
            "colors": colors, "camera_indices": cameras, "triangle_owners": owners,
            "partition_diagonals": diagonals, "monotone_pieces": piece_count,
            "input_vertices": input_count, "algorithm": "Sweep line + monotone triangulation",
            "solver_time_complexity": "O(n log n)", "solver_space_complexity": "O(n)"}


def read_points(filename):
    text = Path(filename).read_text(encoding="utf-8-sig")
    words = "\n".join(line.split("#")[0] for line in text.splitlines()).split()
    try:
        numbers = [int(value) for value in words]
    except ValueError:
        raise ValueError("The input file must contain integer numbers only.") from None
    if not numbers or numbers[0] < 3:
        raise ValueError("The first number must be a vertex count of at least three.")
    if len(numbers) != 1 + 2 * numbers[0]:
        raise ValueError("The declared vertex count does not match the coordinates.")
    return list(zip(numbers[1::2], numbers[2::2]))
