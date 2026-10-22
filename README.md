<div align="center">

📷 CCTV Placement Planner
Turn a polygonal room into a camera plan—with a geometric coverage guarantee.




A Python project combining sweep-line algorithms, monotone triangulation,
and three-colouring to place cameras at room vertices.

Quick Start · Examples · How It Works · Troubleshooting
</div>


<p align="center"><em>One room, three views: boundary → triangulation → camera placement.</em><br>
<a href="output/diagram.svg">Open the scalable SVG</a> · <a href="output/result.txt">Read the coverage certificate</a></p>

The guarantee: for a valid simple polygon with m vertices after cleanup, the
planner selects at most ⌊m/3⌋ cameras and covers the complete room under an ideal
unlimited-range, all-direction visibility model. The exact minimum camera count is
not guaranteed.

Contents
- Overview
- Features at a glance
- Quick start
- Windows and VS Code
- Google Colab
- Input format
- Examples
- Command-line reference
- Understanding the output
- Using the Python API
- How it works
- Correctness and complexity
- Project map
- Verification
- Troubleshooting
- Assumptions and limitations
- Future directions
Overview
Where should cameras be installed in a room with inward corners so that no region
is left unobserved?

This project models the room as a two-dimensional simple polygon. Each input
coordinate is a corner, and consecutive coordinates form the room boundary. The
planner validates that boundary, divides the room into triangles, colours the
vertices, and selects camera positions using the smallest colour group.

A point is visible from a camera when the straight segment joining them stays
inside or on the room boundary. Walls therefore restrict visibility, even though
camera range is unlimited in the model.

The project is a constructive application of the Art Gallery Theorem and is
useful for studying computational geometry, algorithm analysis, and geometric
surveillance planning.
Features at a glance
Capability	What the project provides
Fast geometric solver	O(n log n) worst-case time, including boundary validation
Guaranteed camera bound	At most floor(m/3) cameras for m cleaned vertices
Concave-room support	Handles inward corners as well as convex rooms
Exact calculations	Integer orientation and intersection comparisons
Flexible boundary order	Accepts clockwise or counterclockwise input
Input cleanup	Removes an optional closing duplicate and straight intermediate points
Traceable results	Preserves the original vertex IDs after cleanup and reversal
Coverage certificate	Associates every triangle with a selected camera vertex
Visual explanation	Three-panel PNG and SVG diagrams
Reusable data	Structured JSON containing geometry, colours, and camera assignments
Lightweight execution	Core solver uses the Python standard library; Matplotlib draws pictures
Large-input mode	--no-plot --quiet skips rendering and shortens console output


Quick start
Requirements: Python 3 and, for diagrams, Matplotlib. The project has been
verified with Python 3.12. No compilation step is needed.

Extract the project and open a terminal inside the folder containing main.py:
python -m pip install -r requirements.txt
python main.py examples/example_room.txt --output output/my_room --show
This runs the included seven-vertex example, opens the diagram, and saves four
files in output/my_room/:
File	Contents
diagram.png	Three-panel image of the room and solution
diagram.svg	Scalable vector version of the diagram
result.txt	Camera coordinates and triangle-wise coverage certificate
result.json	Structured geometry and solution data


Expected result for the included example: 7 cleaned vertices, 5 triangles,
2 monotone pieces, and 2 cameras at V5 (7, 9) and V2 (2, 3).

To run the built-in U-shaped room instead:
python main.py --show
That command writes to the default output/ folder and replaces existing results
with the same filenames. Use --output to keep different runs in separate folders.
Windows and VS Code
1. Extract the ZIP completely; do not run files from inside the compressed archive.
2. Open VS Code → File → Open Folder and select cctv_placement_planner.
3. Open Terminal → New Terminal.
4. Confirm that main.py, requirements.txt, examples/, and planner/ are in the
   current folder. An extra outer extraction folder is fine; open the inner project.
5. Run the two quick-start commands above.
If your Windows installation recognises py rather than python, use:
py -m pip install -r requirements.txt
py main.py examples/example_room.txt --output output/my_room --show
Paths containing spaces should be quoted:
python main.py "examples/my room.txt" --output "output/my room" --show
<details>
<summary><strong>Optional: use a virtual environment</strong></summary>

A virtual environment keeps the drawing dependency separate from other projects.

Windows PowerShell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
If PowerShell blocks activation scripts, use the environment's interpreter directly:
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe main.py examples/u_shape.txt --show
Linux or macOS
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
</details>

Google Colab
Create a new Colab notebook and run these cells in order. Upload one project ZIP
when prompted. The ZIP must contain the cctv_placement_planner project folder.

Cell 1 — upload and extract the project
from google.colab import files
import zipfile

uploaded = files.upload()
zip_name = next(iter(uploaded))
with zipfile.ZipFile(zip_name) as archive:
    archive.extractall('/content')
Cell 2 — enter the project and install Matplotlib
%cd /content/cctv_placement_planner
%pip install -q -r requirements.txt
Cell 3 — run the planner
!python main.py examples/example_room.txt --output output/colab
Cell 4 — display the saved diagram
from IPython.display import Image, display

display(Image('output/colab/diagram.png'))
Use the saved PNG for Colab display; --show is intended for a local desktop
window. To download a result from Colab:
files.download('output/colab/diagram.png')
files.download('output/colab/result.txt')
These notebook instructions are provided as cells to copy. A separate notebook
file is not included in this project archive.
Input format
A room file contains a vertex count followed by one integer x y pair per vertex.
Lines beginning with #, and comments after a #, are ignored.
# A six-vertex L-shaped room
6
0 0
8 0
8 3
3 3
3 8
0 8
Save this as examples/my_room.txt, then run:
python main.py examples/my_room.txt --output output/my_room --show
Input rules
Rule	Requirement
Vertex count	At least 3; it must match the coordinate pairs in the file
Coordinates	Integers from −1,000,000 through 1,000,000, inclusive
Boundary order	Follow the perimeter clockwise or counterclockwise
Polygon shape	One simple polygon with nonzero area
Closing edge	Added automatically from the final point back to the first
Repeated first point	Allowed once at the end; include it in the declared count
Other repeated points	Rejected
Straight intermediate points	Accepted and removed during cleanup
Horizontal/vertical edges	Supported
Equal y coordinates	Supported
Crossings and self-touching	Rejected
Holes and internal obstacles	Not supported


The implementation does not impose the earlier 300-vertex cap. Available memory,
coordinate range, and rendering cost still constrain practical input sizes.
Boundary order matters
The planner joins points in the exact order written. It does not reconstruct
an intended room from an unordered point cloud.

For example, these non-adjacent segments cross:
- (2, 3) → (1, 10)
- (10, 5) → (0, 6)
If both appear in the boundary, the polygon is invalid and the program rejects it.
Follow the perimeter of the intended room; sorting points by x or y does not, in
general, produce the correct boundary.
Before running: check the vertex count, follow the boundary around the room,
save the file, and confirm that no non-adjacent edges cross or touch.

Examples
The following results were checked against the current included input files.
Input file	Cleaned vertices	Triangles	Camera bound	Selected cameras
examples/example_room.txt	7	5	2	2
examples/rectangle.txt	4	2	1	1
examples/l_shape.txt	6	4	2	1
examples/u_shape.txt	8	6	2	2


Included seven-vertex room
python main.py examples/example_room.txt --output output/example_room --show
The included coordinates are:
7
0 0
2 3
1 10
5 7
7 9
10 5
6 0
The final point is (6, 0). Replacing it with (0, 6) while keeping the other
points in this order creates a crossing and changes the validity of the room.
<details>
<summary><strong>View the expected console result</strong></summary>


Solver time and the absolute output path depend on the machine. The geometric
result is:
CCTV PLACEMENT PLANNER
Algorithm: Sweep line + monotone triangulation
Solver complexity: O(n log n) time, O(n) extra space
Vertices after cleanup: 7
Monotone pieces: 2
Triangles: 5
Camera bound: 2
Selected cameras: 2

Camera V5 at (7, 9)
Camera V2 at (2, 3)

COVERAGE CERTIFICATE
Triangle 1: vertices [2, 6, 4]; camera V2
Triangle 2: vertices [2, 4, 3]; camera V2
Triangle 3: vertices [7, 6, 2]; camera V2
Triangle 4: vertices [1, 7, 2]; camera V2
Triangle 5: vertices [6, 5, 4]; camera V5
Every triangle has an incident camera. The exact minimum count is not claimed.
</details>

Rectangle
python main.py examples/rectangle.txt --output output/rectangle --show
Expected: 2 triangles and 1 camera, at V2 (12, 0).
L-shaped room
python main.py examples/l_shape.txt --output output/l_shape --show
Expected: 4 triangles and 1 camera, at V4 (3, 3).
U-shaped room
python main.py examples/u_shape.txt --output output/u_shape --show
Expected: 6 triangles and 2 cameras, at V3 (10, 10) and V6 (3, 3).
Intentionally invalid boundary
python main.py examples/invalid_crossing.txt --no-plot
Expected:
Error: Boundary edges cross or touch. Use a simple polygon without holes.
This example is meant to fail. Invalid input exits with a nonzero status.
Command-line reference
python main.py [room_file] [--output DIR] [--show] [--no-plot] [--quiet]
Argument	Default	Purpose
room_file	Built-in U-shaped polygon	Read coordinates from the specified text file
--output DIR	output	Choose where result files are saved
--show	Off	Open the diagram in a local window
--no-plot	Off	Generate text/JSON without importing Matplotlib
--quiet	Off	Print a short summary; keep the full certificate in result.txt
-h, --help	—	Show command-line help


Generate results without opening a window:
python main.py examples/l_shape.txt --output output/l_shape
Run with only the Python standard library:
python main.py examples/u_shape.txt --output output/headless --no-plot --quiet
--show and --no-plot cannot be combined. --quiet changes console output,
not the completeness of saved results.

Output-folder behaviour: existing result files with the same names are
replaced. With --no-plot, old PNG/SVG files are left unchanged. Choose a new
output folder to avoid mistaking an older diagram for the current result.
Understanding the output
The three-panel diagram
Panel	What to look for
1. Room boundary	The original room outline and its vertices
2. Monotone triangulation	Triangle edges and the diagonals used to partition the room
3. Camera positions	Three-coloured vertices and the selected camera locations


Legend
- Red stars: selected cameras.
- Blue, orange, and purple points: the three vertex colour groups.
- Orange dashed lines in panel 2: monotone partition diagonals.
- Dark outline: the room boundary.
Labels such as V1 refer to the original input order. Labels are shown for rooms
with at most 30 cleaned vertices. All images use the original coordinates; the
internal sweep transformation does not alter the displayed room.

The diagram shows triangulation and camera positions. It does not calculate or
shade each camera's full visibility region.
Coverage certificate
A line such as:
Triangle 1: vertices [2, 6, 4]; camera V2
means that V2 is a selected vertex of that triangle. A triangle is convex, so a
camera at V2 can observe the complete triangle under the model assumptions.
Repeating this argument for all triangles establishes coverage of the room.

A camera may see more than its assigned triangles. The certificate records a
sufficient coverage assignment, not its complete visible region.
JSON result fields
Field	Meaning
points	Cleaned polygon coordinates in counterclockwise order
vertex_ids	Original one-based input IDs corresponding to points
triangles	Triples of zero-based indices into points
colors	Colour labels 0, 1, or 2 for cleaned vertices
camera_indices	Zero-based indices of selected camera vertices
triangle_owners	One camera index per triangle
partition_diagonals	Endpoint-index pairs for the monotone partition
monotone_pieces	Number of monotone pieces
input_vertices	Number of supplied points before cleanup
algorithm	Solver method name
solver_time_complexity	Declared asymptotic solver time
solver_space_complexity	Declared asymptotic auxiliary space
solver_seconds	Measured time for solve(), added by run()


Indexing example: if camera_indices contains 2, obtain the coordinate with
points[2] and the original printed label with vertex_ids[2]. It does not
necessarily mean V3, because cleanup and orientation reversal can change indexing.
Using the Python API
Run these examples from the project root, or make the project root available on
Python's import path.
Compute a plan without writing files
from planner import solve

points = [(0, 0), (8, 0), (8, 3), (3, 3), (3, 8), (0, 8)]
result = solve(points)

for index in result['camera_indices']:
    vertex_id = result['vertex_ids'][index]
    position = result['points'][index]
    print(f'Camera V{vertex_id} at {position}')
solve() does not import Matplotlib, write files, or modify the caller's list.
Read a room and save the complete output
from planner import read_points, run

points = read_points('examples/example_room.txt')
result = run(points, output_dir='output/python_api', show=False)
Save results without diagrams
from planner import read_points, run

points = read_points('examples/u_shape.txt')
result = run(points, output_dir='output/data_only', plot=False, quiet=True)
Function	Behaviour
read_points(filename)	Parses the text-file format into coordinate pairs
solve(points)	Validates and computes the plan; returns a result dictionary
run(points, output_dir='output', show=False, plot=True, quiet=False)	Calls the solver, adds timing, saves results, and optionally draws


How it works
1. Validate and clean the boundary
The program checks coordinate types, coordinate bounds, duplicate vertices,
backtracking edges, boundary intersections, and nonzero area. A sweep line and
an AVL tree detect illegal intersections without comparing every edge pair.

After validation, straight intermediate vertices are removed in one pass. A
clockwise boundary is reversed. Original IDs are retained for readable results.
2. Make sweep heights distinct
For internal sweep calculations, the program uses:
X = x
Y = K*y + x
K = max(x) - min(x) + 1
Since coordinates are integers, distinct points have distinct transformed heights.
This invertible transformation preserves intersections and turn directions while
handling horizontal edges and repeated y values without a floating-point epsilon.
Reported positions remain in the original coordinate system.
3. Partition the room into monotone pieces
A piece is monotone in the sweep direction when each sweep line intersects it in
at most one connected interval.

Vertices are classified as start, end, split, merge, or regular.
The sweep maintains active left boundaries and their helper vertices, inserting
noncrossing diagonals to resolve split and merge corners.

An AVL tree keeps insertion, deletion, and left-boundary searches logarithmic.
Directed-edge lists recover the resulting piece boundaries without repeatedly
copying and splitting entire polygon lists.
4. Triangulate each piece with a stack
Each piece's vertices are sorted in sweep order. A stack connects vertices while
respecting the left and right boundary chains, creating a noncrossing triangulation.
For m cleaned room vertices, the final result contains m − 2 triangles.
5. Three-colour the vertices
Triangle neighbours are identified by shared edges. Their adjacency graph is a
tree for a triangulated simple polygon.

The first triangle receives colours 0, 1, and 2. During a traversal, each next
triangle shares a coloured edge with its parent. Its new vertex receives the
remaining colour:
new_colour = 3 - first_known_colour - second_known_colour
6. Select cameras and verify the result
The planner chooses the smallest colour group and places cameras at all its
vertices. It assigns each triangle its selected incident camera and checks the
triangle count, colours, areas, connectivity, and camera bound.

For the full geometric explanation, see [ALGORITHM.md](ALGORITHM.md).
Correctness and complexity
Why the placement covers the room
1. The triangulation covers the complete polygon.
2. Every triangle has one vertex of each colour.
3. Selecting all vertices of one colour gives every triangle a camera.
4. A camera at a triangle vertex sees every point in that convex triangle.
If the colour groups have sizes c₀, c₁, and c₂, then:
c₀ + c₁ + c₂ = m
min(c₀, c₁, c₂) ≤ floor(m/3)
This establishes both coverage and the camera-count bound. It does not establish
that no other placement could use fewer cameras.
Complexity by stage
Let n be the input count and m ≤ n the count after cleanup.
Stage	Worst-case time
Duplicate detection and boundary-simplicity sweep	O(n log n)
Straight-point cleanup and orientation	O(n)
Monotone partitioning	O(m log m)
Piece-boundary construction, including angular sorting	O(m log m)
Sorting pieces and stack triangulation	O(m log m)
Building triangle adjacency	O(m log m)
Colour traversal and camera selection	O(m)
Coverage assignments and internal checks	O(m)
Complete geometric solver	O(n log n)


Auxiliary space: O(n).

The stages execute sequentially, so their costs add. Sorting each monotone piece
is included in the bound; this implementation does not claim a fully linear
piece-triangulation stage including ordering.

The analysis uses the standard unit-cost arithmetic model for geometric
operations. Exact Python integers avoid overflow. Rendering time, output-device
performance, and file-system delays are separate from the solver's bound. Text
and JSON outputs contain O(m) records.
Project map
Path	Responsibility
main.py	Command-line arguments and program entry point
requirements.txt	Matplotlib dependency for diagrams
ALGORITHM.md	Detailed algorithm, proof outline, and complexity analysis
examples/	Included valid rooms and an intentionally invalid crossing
output/	Included sample outputs; default destination for new runs
planner/__init__.py	Public read_points, solve, and run imports
planner/solver.py	Input preparation and complete solving pipeline
planner/geometry.py	Exact orientation, area, intersection, and sweep-height operations
planner/avl.py	Balanced search tree for active-edge operations
planner/sweep.py	Sweep-line ordering and polygon-simplicity validation
planner/triangulation.py	Monotone partitioning, face walks, and stack triangulation
planner/coloring.py	Triangle adjacency and three-colouring
planner/drawing.py	Three-panel Matplotlib PNG/SVG output
planner/report.py	Timing, console report, and text/JSON file output


Suggested reading order: main.py → planner/solver.py → planner/geometry.py
→ planner/sweep.py → planner/triangulation.py → planner/coloring.py.
Read planner/avl.py alongside the sweep code to understand logarithmic searches.
Verification
The solver performs these checks during ordinary execution:
- The cleaned polygon produces exactly m − 2 triangles.
- Each triangle has positive area.
- Triangle areas sum exactly to the polygon area.
- Each triangle contains all three vertex colours.
- The triangle traversal reaches the complete triangulation.
- The selected camera count satisfies floor(m/3).
For a quick reproducible check, run the included examples without drawing:
python main.py examples/rectangle.txt --output output/check_rectangle --no-plot --quiet
python main.py examples/l_shape.txt --output output/check_l_shape --no-plot --quiet
python main.py examples/u_shape.txt --output output/check_u_shape --no-plot --quiet
python main.py examples/example_room.txt --output output/check_example --no-plot --quiet
Compare their camera and triangle counts with the examples table.
The intentionally invalid example should return the crossing error shown above.

These are smoke checks, not an exhaustive proof. The construction and correctness
argument are described in [ALGORITHM.md](ALGORITHM.md). This archive does not
include a standalone automated test suite or a benchmark script.
Troubleshooting
Symptom	What to check or do
python is not recognised	On Windows, try py; otherwise confirm Python is installed and available in the terminal
can't open file ... main.py	Open the inner project folder containing main.py, then run the command again
No module named planner	Run from the project root and keep the planner/ folder beside main.py
Drawing needs Matplotlib	Run python -m pip install -r requirements.txt using the same interpreter as the program, or use --no-plot
Input file cannot be found	Check its path relative to the current terminal folder; quote paths containing spaces
Declared vertex count does not match	Count coordinate pairs and update the first number; save the file before running
Integer-number or coordinate error	Use integer x/y pairs within the supported range; remove commas and brackets from text-file coordinates
Boundary edges cross or touch	Recheck perimeter order, including the automatic last-to-first edge; avoid non-adjacent contacts
Edges overlap or turn back	A boundary segment reverses along an existing segment; correct that corner's coordinates/order
Repeated-vertex error	Remove duplicates except for the optional single closing copy of the first vertex
Diagram does not open	Without --show, it is saved but no window opens; inspect diagram.png in the output folder
Diagram does not open in Colab	Display the saved PNG with IPython.display.Image
Diagram looks like an older input	--no-plot leaves old images unchanged; rerun with plotting or use a new output folder
Some vertex labels are missing	Straight points are removed; labels are also omitted when more than 30 cleaned vertices remain
Camera order differs from input order	The solver normalises orientation; use original vertex_ids to interpret the result
Large diagrams take a long time	Use --no-plot --quiet to run and save the geometric solution without rendering


<details>
<summary><strong>Why did a convex room get more cameras than expected?</strong></summary>

The method chooses one complete colour class from its triangulation. It guarantees
coverage and the floor(m/3) bound, but it does not minimise camera count for each
individual room. A convex room can be visible from one vertex even when this
particular construction selects additional cameras.
</details>

<details>
<summary><strong>Why is the camera bound based on fewer vertices than my file contains?</strong></summary>


An optional repeated closing point and redundant straight intermediate points are
removed. They do not change the room shape. The camera bound and triangle count
use the cleaned polygon; original vertex IDs are kept so camera locations can
still be traced back to the input.
</details>

Assumptions and limitations
Model assumption	Practical implication
Two-dimensional room	Camera height and three-dimensional occlusion are excluded
Simple polygon without holes	Enclosed pillars, interior obstacles, and disconnected rooms are excluded
Vertex-mounted point cameras	Arbitrary wall/interior mounting positions are not searched
Unlimited range	Distance-based image quality and detection limits are excluded
All-direction field of view	Directional lenses and camera orientation are not modelled
Sufficient-camera construction	The result need not be the minimum-camera arrangement
Geometry-only planning	Power, wiring, cost, mounting feasibility, and privacy zones are excluded


The result is a geometric coverage plan under these assumptions. Physical
surveillance installation requires additional constraints beyond this model.
Future directions
Potential extensions—not currently implemented—include:
- Range-limited and directional cameras.
- Full visibility-region visualisation for each selected camera.
- Interactive room drawing and coordinate editing.
- Support for interior obstacles and polygonal holes with revised coverage logic.
- Optimisation methods for reducing camera count.
- Installation costs, mounting constraints, and privacy-aware regions.
<div align="center">

Developed by Vishal Rajput
B.Tech, Computer Science & Engineering · IIIT Kalyani

Geometry in. A camera plan out.
</div>