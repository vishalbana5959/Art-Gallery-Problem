def cross(a, b, c):
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def area_twice(points):
    return sum(points[i][0] * points[(i + 1) % len(points)][1]
               - points[i][1] * points[(i + 1) % len(points)][0]
               for i in range(len(points)))


def on_segment(a, b, p):
    return (cross(a, b, p) == 0
            and min(a[0], b[0]) <= p[0] <= max(a[0], b[0])
            and min(a[1], b[1]) <= p[1] <= max(a[1], b[1]))


def segments_intersect(a, b, c, d):
    x, y = cross(a, b, c), cross(a, b, d)
    z, w = cross(c, d, a), cross(c, d, b)
    if x * y < 0 and z * w < 0:
        return True
    return (on_segment(a, b, c) or on_segment(a, b, d)
            or on_segment(c, d, a) or on_segment(c, d, b))


def sweep_heights(points):
    """Use Y = K*y + x to give every distinct integer point a unique height.

    K is larger than the complete x range. This invertible transformation
    preserves intersections and turns. Original coordinates stay unchanged.
    """
    xs = [p[0] for p in points]
    k = max(xs) - min(xs) + 1
    return [k * y + x for x, y in points]
