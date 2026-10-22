# CCTV Placement Planner — O(n log n)

A Python-only replacement for the original ear-clipping project.
It places ideal cameras at polygon vertices so the entire room is covered.
The number of cameras is at most floor(m/3), where m is the number of vertices
remaining after straight points and an optional closing duplicate are removed.
The exact minimum number of cameras is NOT claimed.

## What changed

- Ear clipping was replaced by sweep-line monotone partitioning and stack triangulation.
- Pairwise boundary checks were replaced by an O(n log n) sweep-line check.
- Repeated list deletion during cleanup was replaced by a linear pass.
- Three-colouring now traverses neighbouring triangles, rather than reversing ears.
- All core geometry uses exact integer arithmetic.
- The original 300-vertex cap was removed. Large inputs can use `--no-plot --quiet`.
- Input format, the `solve/read_points/run` interface, and all four output formats remain.

There is no C++, compiler, Makefile, geometry package, or web application.
Only Matplotlib is needed for pictures. The solver and tests need only Python.

## Start on Windows / VS Code

1. Extract this ZIP completely.
2. Open the extracted `cctv_planner_nlogn` folder in VS Code.
3. Open **Terminal > New Terminal**. The terminal folder must contain `main.py`.
4. Run:

```text
python -m pip install -r requirements.txt
python main.py examples/example_room.txt --output output/my_room --show
```

If Windows recognises `py` instead of `python`, replace `python` with `py`.

Other runs:

```text
python main.py
python main.py examples/u_shape.txt --output output/u_shape
python main.py examples/rectangle.txt --output output/rectangle
python main.py examples/l_shape.txt --output output/l_shape
```

Running without an input file uses the original built-in U-shaped room.
Input files stay in `examples/`. Results are written to `output/` or the folder
specified with `--output`. Use a separate output folder for each saved example.

## Your own room

Create `examples/my_room.txt`:

```text
6
0 0
8 0
8 3
3 3
3 8
0 8
```

Then run:

```text
python main.py examples/my_room.txt --output output/my_room --show
```

Rules:

- First number: vertex count, at least 3. Then exactly that many `x y` pairs.
- Walk around the boundary, clockwise OR counterclockwise. Do not sort by x or y.
- Coordinates must be integers between -1,000,000 and 1,000,000.
- Horizontal/vertical edges, equal y coordinates, and extra straight points work.
- Repeating the first point at the very end is allowed; count it in the file count.
- Other repeated vertices, self-intersections, self-touching, and overlapping edges are rejected.
- Use one simple polygon with no holes. `#` starts a comment.

## Google Colab

The included `Run_in_Colab.ipynb` contains ready-to-run cells.
Open that notebook in Colab and follow its instructions, or start a new notebook:

**Cell 1 — upload this project ZIP and extract it**

```python
from google.colab import files
import zipfile

uploaded = files.upload()
zip_name = next(iter(uploaded))
with zipfile.ZipFile(zip_name) as archive:
    archive.extractall('/content')
```

**Cell 2 — enter the project and install the drawing dependency**

```python
%cd /content/cctv_planner_nlogn
%pip install -q -r requirements.txt
```

**Cell 3 — run and display the result**

```python
!python main.py examples/example_room.txt --output output/colab
from IPython.display import Image, display
display(Image('output/colab/diagram.png'))
```

Do not use `--show` in Colab; display the saved image instead.

You can also call the program directly from Python:

```python
from planner import run

points = [(0, 0), (8, 0), (8, 3), (3, 3), (3, 8), (0, 8)]
result = run(points, output_dir='output/custom')
```

## Output

- `diagram.png`: boundary, triangulation, and cameras in three panels.
- `diagram.svg`: scalable copy of the same figure.
- `result.txt`: camera coordinates and a triangle-by-triangle coverage certificate.
- `result.json`: triangles, colours, cameras, original vertex IDs, and metadata.

Red stars are cameras. Orange dashed lines are monotone partition diagonals.
Pictures always use the ORIGINAL coordinates, not the internal sweep heights.
Vertex labels are omitted above 30 vertices to keep diagrams legible.
JSON indices are zero-based; printed vertex IDs such as V5 are one-based original IDs.

For the supplied 11-vertex example, this version produces 9 triangles and selects
V5 at (11, 3) and V9 at (3, 3): 2 cameras, within the bound of 3.
Camera positions may differ from the old project because the triangulation changed.
Pre-generated outputs for this example are in `output/example_room/`.

## Complexity and large inputs

```text
python main.py examples/my_room.txt --output output/large --no-plot --quiet
```

`--no-plot` avoids Matplotlib entirely and generates only text/JSON.
If that output folder already has diagram.png/diagram.svg, those older pictures
are left unchanged; use a new folder to avoid mixing results from different runs.
`--quiet` avoids printing thousands of triangle lines; the complete certificate
is still saved in result.txt.

For n input vertices, the **complete geometric solver**, including validation,
cleanup, triangulation, colouring setup, camera selection, and checks, has:

- **O(n log n) worst-case time**, under the standard constant-cost arithmetic model.
- **O(n) auxiliary space**.

The bound does not rely on random balancing, a hash-table assumption, or an
unvalidated polygon. An AVL tree gives worst-case logarithmic sweep operations.
Output text/JSON contains O(n) records. Matplotlib rendering is separate and is
not part of the geometric complexity claim; the reported solver timer excludes it.
See `ALGORITHM.md` for the per-stage analysis and correctness explanation.

## Tests and timing

```text
python -m unittest discover -s tests -v
python benchmark.py
python benchmark.py --sizes 1000 5000 10000 20000 --repeat 3
```

Tests include independent, intentionally quadratic checks on small inputs.
Those checks are never used by `main.py` or `solve()`.
The benchmark uses concave comb rooms with many active edges, not only easy convex rooms.
Timings illustrate scaling; they do not replace the complexity proof.

## Files to study

1. `main.py`: command-line interface.
2. `planner/solver.py`: complete pipeline and input preparation.
3. `planner/geometry.py`: cross product and segment tests.
4. `planner/sweep.py`: fast validation and active-edge ordering.
5. `planner/triangulation.py`: partitioning, face walking, and stack triangulation.
6. `planner/coloring.py`: three-colouring using triangle neighbours.
7. `planner/avl.py`: standard balanced binary search tree.
8. `planner/drawing.py` and `planner/report.py`: optional pictures and result files.

The tree and directed-edge lists are the extra machinery needed for the requested
general-polygon time bound. They are kept in small separate functions with comments.

## Assumptions

Unlimited-range, all-direction, point cameras in a two-dimensional room.
No holes, internal obstacles, physical mounting constraints, or optimal-camera guarantee.
This is a geometric educational planner, not a real-camera visibility simulator.

## Updating your earlier report

The previous report describes ear clipping and O(n³), so it no longer describes
this version. Use `REPORT_UPDATE.md` for replacement algorithm, complexity, results,
and limitations text. Take new screenshots because camera positions have changed.
