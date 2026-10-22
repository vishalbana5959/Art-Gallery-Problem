# Algorithm and complexity

## Scope

Input: one simple polygon, integer coordinates, no holes. Coordinates are supplied
in boundary order. Output: triangulation, three-colouring, and vertex cameras
covering the polygon under ideal unlimited-range/all-direction assumptions.

Let n be the input count and m the count after cleanup, so m <= n.
The camera bound is floor(m/3). Overall solver time is O(n log n), space O(n),
using the usual unit-cost model for bounded-coordinate geometric operations.
Python integers avoid overflow. A bit-complexity analysis with unbounded coordinate
lengths would additionally count the cost of integer arithmetic.

## 1. Input preparation and validation

Check coordinate types and ranges. Remove one optional closing duplicate.
Sort a copy of the coordinates to reject other duplicates in O(n log n).
Check adjacent backtracking in one pass.

Use a Shamos-Hoey-style sweep to detect non-adjacent intersecting edges:

1. Sort vertices from top to bottom.
2. Remove edges ending at the current vertex and insert edges starting there.
3. Whenever two edges become neighbours, check their complete segments for an
   illegal intersection. Legal adjacent shared endpoints are allowed.
4. Stop at the first illegal intersection.

Between events, nonintersecting active edges keep their left-to-right order.
If any illegal intersection existed, its participating edges would become
neighbours before it; the complete-segment check detects it before their order
could become invalid. Insert/remove/neighbour queries use an AVL tree.
There are O(n) events and O(1) tree operations per event: O(n log n) total.

Only AFTER this check, remove straight intermediate boundary points in a single
pass. Removing a point lying between its neighbours leaves the boundary unchanged.
Reverse clockwise polygons and retain original vertex IDs. These steps are O(n).

## 2. Exact handling of equal heights

For the sweep only, use X = x and Y = K*y + x, where
K = max(x) - min(x) + 1. Distinct integer points have distinct transformed Y:
a one-unit change in y outweighs any difference in x.

This is an invertible, orientation-preserving linear transformation (determinant K).
It preserves straight segments, intersections, convexity and visibility.
Thus original horizontal edges and equal-height vertices require no floating
epsilon. Active-edge intersections with the sweep are compared as integer
numerator/denominator pairs by cross multiplication. At shared endpoints,
slopes resolve the order immediately above or below the event.

All reported positions, triangle areas and drawings use original coordinates.

## 3. Partition into monotone pieces

A polygon is monotone in the sweep direction if a sweep line intersects it in
at most one connected interval. Classify vertices by neighbouring heights and turn:

- Start: both neighbours below; convex.
- End: both neighbours above; convex.
- Split: both neighbours below; reflex (inward corner).
- Merge: both neighbours above; reflex.
- Regular: one neighbour above and one below.

The sweep stores downward-directed left boundary edges in the AVL tree.
Each active edge has a helper vertex: the latest relevant vertex for adding a
diagonal without crossing the polygon boundary.

- At start: insert the outgoing edge and set its helper.
- At end: connect to the incoming edge's helper if it is a merge, then remove the edge.
- At split: find the boundary directly left, connect to its helper, update that
  helper, and insert the outgoing edge.
- At merge: resolve the incoming edge's merge helper, remove the edge, then
  resolve/update the helper of the boundary directly left.
- At regular: either replace the incoming left boundary with the outgoing edge,
  or update the helper of the boundary directly left. Resolve merge helpers as needed.

This inserts O(m) noncrossing diagonals and removes split/merge obstructions.
Sorting and O(1) logarithmic operations per vertex take O(m log m).

## 4. Recover piece boundaries without quadratic copying

Do not repeatedly split large Python lists after adding a diagonal.
Instead, store each boundary edge and diagonal in both directions using lists.
Sort outgoing directions around each vertex with exact orientation comparisons.
Walk each directed edge once, keeping the face on the left.
Discard the clockwise outer face and keep the counterclockwise bounded faces.

There are O(m) directed edges. Angular ordering costs at most O(m log m),
and the face walks cost O(m). Each original edge is used once by bounded faces
and each partition diagonal twice, so the sum of all piece sizes is O(m).

## 5. Triangulate each monotone piece

For each piece, identify its top/bottom vertices and its two descending chains.
Sort the vertices by sweep height and use a stack:

- If the next vertex is on the opposite chain, join it to successive stack
  vertices, producing a fan of triangles.
- If it is on the same chain, pop vertices while the next triangle lies inside
  the piece; use the cross-product sign to decide.
- At the bottom vertex, finish the remaining triangles.

Strict turn tests retain collinear stack vertices until a positive-area triangle
can be formed. Every produced triangle is stored counterclockwise.

Stack work is O(k) for a k-vertex piece. This implementation deliberately sorts
each piece in O(k log k), rather than adding code to merge its two chains.
Since the total piece size is O(m), the total is still O(m log m).

## 6. Three-colour and choose cameras

Create three edge records per triangle and sort them by endpoint IDs.
Two triangles sharing an internal edge become neighbours. Sorting takes O(m log m).
The triangle-adjacency graph (dual graph) of a simple polygon triangulation is a tree.

Give the first triangle colours 0, 1 and 2. Traverse the tree using a list as a stack.
Each next triangle shares a coloured edge with its parent. Give its new vertex
the missing colour: 3 minus the two known colours. The traversal takes O(m).

Choose the smallest colour group, place cameras there, and assign each triangle
its incident selected camera. Counting, selection and ownership are O(m).

## 7. Correctness

The monotone partition and stack triangulation create a noncrossing triangulation
whose union is the polygon. Every triangle gets one vertex of each colour.
Choosing any complete colour group therefore gives every triangle a camera at a vertex.
A triangle is convex, so this camera sees every point of that triangle.
All triangles together cover the room. The smallest of three colour groups has
at most floor(m/3) vertices. This proves coverage and the camera-count bound,
not minimum-camera optimality.

Runtime sanity checks verify m-2 triangles, positive triangle areas, exact total
area, all three colours per triangle, connected triangle traversal and the bound.
The independent test suite additionally checks containment and crossing of edges
on small inputs; those slower test-only checks are not part of the solver.

## Complexity summary

| Stage | Worst-case time | Extra space |
| --- | --- | --- |
| Duplicate detection and simplicity sweep | O(n log n) | O(n) |
| Straight-point cleanup and orientation | O(n) | O(n) |
| Monotone partition | O(m log m) | O(m) |
| Face construction including angular sorting | O(m log m) | O(m) |
| Piece sorting and stack triangulation | O(m log m) | O(m) |
| Triangle adjacency construction | O(m log m) | O(m) |
| Colour traversal and camera selection | O(m) | O(m) |
| Result checks and coverage assignments | O(m) | O(m) |
| Complete solver | **O(n log n)** | **O(n)** |

The stages run sequentially; their costs ADD rather than multiply.
AVL recursion depth is logarithmic. Polygon/triangle traversals are iterative.
No production stage scans all edge pairs, repeatedly clips ears, or uses a
sorted Python list for sweep insertion. Output files have O(m) records.
Optional Matplotlib rendering and file-system performance are not covered by
the solver's computational bound.

## References for the algorithms

The implementation is written for this project. Standard algorithm background:

- Rensselaer Polytechnic Institute, CSCI 4560/6560, Lecture 5: Triangulation, Part 2:
  https://www.cs.rpi.edu/~cutler/classes/computationalgeometry/F23/lectures/05_triangulation_part_2.pdf
- MIT 6.838, Daniel Vlasic, Polygon Triangulation lecture:
  https://groups.csail.mit.edu/graphics/classes/6.838/F01/lectures/PolygonTriangulation/index.html
- Michael I. Shamos and Dan Hoey, Geometric Intersection Problems (1976):
  https://doi.org/10.1184/R1/6622358
