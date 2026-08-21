"""
DIMACS .clq File Parser
=======================
Converts a DIMACS-format .clq (or .col / .mis) file to a Python
edge list in the same format used throughout this project.

DIMACS format:
  c  ...          comment line  (ignored)
  p edge N M      problem line: N nodes, M edges
  e u v           edge line: edge between nodes u and v (1-indexed)

All node indices in .clq files are 1-indexed.
This parser converts to 0-indexed to match our convention.

Usage:
    edges = parse_clq("graph.clq")
    edges = parse_clq("graph.clq", zero_indexed=True)   # default
    edges = parse_clq("graph.clq", zero_indexed=False)  # keep 1-indexed
"""

def parse_clq(filepath: str, zero_indexed: bool = True, weighted: bool = False) -> tuple:
    """
    Parse a DIMACS .clq file and return node count and edge list.

    Parameters
    ----------
    filepath     : str  — path to the .clq file
    zero_indexed : bool — if True (default), convert node indices from
                          1-based (DIMACS) to 0-based (Python convention)
    weighted     : bool — if True, parse edge weights from format "e u v w"
                          if False (default), return unweighted edges as (u, v)

    Returns
    -------
    n_nodes : int
        Number of nodes in the graph
    edges : list of tuples
        If weighted=False: list of (u, v) tuples
        If weighted=True: list of (u, v, w) tuples where w is the edge weight
        Edge list with u < v, deduplicated and sorted

    Examples
    --------
    >>> N, edges = parse_clq("graph.clq")
    >>> N, edges = parse_clq("graph.clq", zero_indexed=True)   # 0-indexed (default)
    >>> N, edges = parse_clq("graph.clq", zero_indexed=False)  # 1-indexed
    >>> N, edges = parse_clq("graph.clq", weighted=True)       # with weights
    """
    edges   = []
    n_nodes = None
    n_edges_expected = None
    offset  = 1 if zero_indexed else 0

    with open(filepath, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            parts = line.split()
            tag   = parts[0]

            if tag == 'c':
                # Comment — print for info
                print(f"  [comment] {' '.join(parts[1:])}")

            elif tag == 'p':
                # Problem line: p edge N M
                n_nodes          = int(parts[2])
                n_edges_expected = int(parts[3])
                print(f"  [problem] nodes={n_nodes}  edges={n_edges_expected}")

            elif tag == 'e':
                # Edge line: e u v [w]  (1-indexed in file, w is optional weight)
                u = int(parts[1]) - offset
                v = int(parts[2]) - offset

                # Parse weight if present and requested
                if weighted and len(parts) >= 4:
                    w = float(parts[3])
                else:
                    w = None

                if u > v:
                    u, v = v, u    # enforce u < v

                if u != v:
                    if weighted:
                        # Store as (u, v, w) with default weight 1.0 if not specified
                        edges.append((u, v, w if w is not None else 1.0))
                    else:
                        edges.append((u, v))

    # Deduplicate (some files list edges twice)
    # For weighted edges, accumulate weights for duplicates
    if weighted:
        edge_dict = {}
        for u, v, w in edges:
            key = (u, v)
            edge_dict[key] = edge_dict.get(key, 0.0) + w
        edges = sorted([(u, v, w) for (u, v), w in edge_dict.items()])
    else:
        edges = sorted(set(edges))

    print(f"\n  Parsed   : {len(edges)} edges  "
          f"(expected {n_edges_expected})")
    print(f"  Indexing : {'0-based' if zero_indexed else '1-based'}")
    print(f"  Weighted : {'Yes' if weighted else 'No'}")
    if n_nodes:
        print(f"  Nodes    : {n_nodes}")

    return n_nodes, edges