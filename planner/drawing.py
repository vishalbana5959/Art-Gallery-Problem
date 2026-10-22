"""Optional Matplotlib output; geometry itself has no external dependency."""


def draw_solution(result, folder, show=False):
    import matplotlib.pyplot as plt
    from matplotlib.collections import LineCollection, PolyCollection

    points = result["points"]
    triangles = result["triangles"]
    cameras = result["camera_indices"]
    palette = ["#2674c9", "#da8b00", "#8049b7"]
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    boundary = points + [points[0]]
    x, y = zip(*boundary)
    faces = [[points[v] for v in triangle] for triangle in triangles]
    for panel, ax in enumerate(axes):
        ax.fill(x, y, color="#eff6fa")
        if panel > 0:
            ax.add_collection(PolyCollection(faces, facecolor="#66b9a5",
                                             edgecolor="#536674", linewidth=0.6, alpha=0.3))
        ax.plot(x, y, color="#28475c", linewidth=1.5)
        if panel == 1 and result["partition_diagonals"]:
            lines = [[points[a], points[b]] for a, b in result["partition_diagonals"]]
            ax.add_collection(LineCollection(lines, colors="#b76b20", linewidths=1.5,
                                             linestyles="dashed"))
        vertex_colors = [palette[c] for c in result["colors"]] if panel == 2 else "#28475c"
        ax.scatter(*zip(*points), c=vertex_colors, s=18, zorder=3)
        if len(points) <= 30:
            for v, point in enumerate(points):
                ax.annotate(f"V{result['vertex_ids'][v]}", point, xytext=(4, 6),
                            textcoords="offset points", fontsize=8)
        if panel == 2:
            ax.scatter(*zip(*(points[v] for v in cameras)), marker="*", color="crimson",
                       s=160, zorder=4)
        ax.set_aspect("equal")
        ax.margins(0.15)
        ax.grid(alpha=0.18)
        ax.set_xlabel("x")
        ax.set_ylabel("y")
    axes[0].set_title("1. Room boundary")
    axes[1].set_title("2. Monotone triangulation")
    axes[2].set_title(f"3. Camera positions ({len(cameras)})")
    fig.suptitle("CCTV Placement Planner - O(n log n) solver", fontsize=14)
    fig.text(0.5, 0.035, "Red stars: cameras. Orange dashed lines: monotone partition diagonals.\n"
             "Ideal unlimited range and all-direction view; minimum count is not claimed.",
             ha="center", fontsize=9)
    fig.tight_layout(rect=(0, 0.12, 1, 0.92))
    fig.savefig(folder / "diagram.png", dpi=160)
    fig.savefig(folder / "diagram.svg")
    if show:
        plt.show()
    plt.close(fig)
