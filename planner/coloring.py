"""Build triangle neighbours, then three-colour by walking their dual tree."""


def color_vertices(n, triangles):
    edge_records = []
    for t, triangle in enumerate(triangles):
        for i in range(3):
            a, b = triangle[i], triangle[(i + 1) % 3]
            edge_records.append((min(a, b), max(a, b), t))
    # Sorting avoids relying on expected-time hash-table behaviour.
    edge_records.sort()
    neighbours = [[] for _ in triangles]
    i = 0
    while i < len(edge_records):
        j = i + 1
        while j < len(edge_records) and edge_records[j][:2] == edge_records[i][:2]:
            j += 1
        if j - i == 2:
            a, b = edge_records[i][2], edge_records[i + 1][2]
            neighbours[a].append(b)
            neighbours[b].append(a)
        elif j - i != 1:
            raise RuntimeError("More than two triangles share an edge.")
        i = j

    colors = [-1] * n
    for color, vertex in enumerate(triangles[0]):
        colors[vertex] = color
    visited = [False] * len(triangles)
    visited[0] = True
    stack = [0]
    while stack:
        current = stack.pop()
        for other in neighbours[current]:
            if visited[other]:
                continue
            triangle = triangles[other]
            missing = [v for v in triangle if colors[v] == -1]
            if len(missing) != 1:
                raise RuntimeError("Triangle adjacency is not a valid dual tree.")
            colors[missing[0]] = 3 - sum(colors[v] for v in triangle if colors[v] >= 0)
            visited[other] = True
            stack.append(other)
    if not all(visited) or -1 in colors:
        raise RuntimeError("The triangulation is disconnected.")
    return colors
