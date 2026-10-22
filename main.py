"""Run: python main.py [room_file] [--output DIR] [--show] [--no-plot]."""

import argparse

from planner import read_points, run

EXAMPLE = [(0, 0), (10, 0), (10, 10), (7, 10),
           (7, 3), (3, 3), (3, 10), (0, 10)]


def main():
    parser = argparse.ArgumentParser(description="CCTV placement with an O(n log n) solver")
    parser.add_argument("room_file", nargs="?", help="Input text file; omitted = built-in U-shaped room")
    parser.add_argument("--output", default="output", help="Output folder (default: output)")
    parser.add_argument("--show", action="store_true", help="Open the generated diagram")
    parser.add_argument("--no-plot", action="store_true", help="Skip pictures; Matplotlib is not needed")
    parser.add_argument("--quiet", action="store_true", help="Print a short summary for large inputs")
    args = parser.parse_args()
    if args.show and args.no_plot:
        parser.error("--show cannot be used with --no-plot")
    try:
        points = read_points(args.room_file) if args.room_file else EXAMPLE
        run(points, args.output, args.show, not args.no_plot, args.quiet)
    except (ValueError, OSError) as error:
        parser.exit(1, f"Error: {error}\n")
    except ImportError:
        parser.exit(1, "Drawing needs Matplotlib. Run: python -m pip install -r requirements.txt\n"
                    "Or use --no-plot to run without it.\n")


if __name__ == "__main__":
    main()
