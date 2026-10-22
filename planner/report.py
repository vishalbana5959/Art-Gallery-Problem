import json
from pathlib import Path
from time import perf_counter

from .solver import solve


def run(points, output_dir="output", show=False, plot=True, quiet=False):
    start = perf_counter()
    result = solve(points)
    result["solver_seconds"] = perf_counter() - start
    folder = Path(output_dir)
    folder.mkdir(parents=True, exist_ok=True)
    lines = ["CCTV PLACEMENT PLANNER", f"Algorithm: {result['algorithm']}",
             "Solver complexity: O(n log n) time, O(n) extra space",
             f"Vertices after cleanup: {len(result['points'])}",
             f"Monotone pieces: {result['monotone_pieces']}",
             f"Triangles: {len(result['triangles'])}",
             f"Camera bound: {len(result['points']) // 3}",
             f"Selected cameras: {len(result['camera_indices'])}",
             f"Solver time (excluding drawing and file output): {result['solver_seconds']:.6f} seconds", ""]
    for v in result["camera_indices"]:
        lines.append(f"Camera V{result['vertex_ids'][v]} at {result['points'][v]}")
    lines.extend(["", "COVERAGE CERTIFICATE"])
    for i, triangle in enumerate(result["triangles"]):
        vertices = [result["vertex_ids"][v] for v in triangle]
        owner = result["vertex_ids"][result["triangle_owners"][i]]
        lines.append(f"Triangle {i + 1}: vertices {vertices}; camera V{owner}")
    lines.append("Every triangle has an incident camera. The exact minimum count is not claimed.")
    text = "\n".join(lines)
    (folder / "result.txt").write_text(text + "\n", encoding="utf-8")
    (folder / "result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    if plot:
        from .drawing import draw_solution
        draw_solution(result, folder, show)
    if quiet:
        print(f"{len(points)} input vertices; {len(result['camera_indices'])} cameras; "
              f"solver {result['solver_seconds']:.6f} s")
    else:
        print(text)
    print(f"Files saved in: {folder.resolve()}")
    return result
