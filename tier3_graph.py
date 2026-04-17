"""
Tier 3 (Bonus): Extension Sharing Graph
- Builds a graph where nodes are extensions and edges mean ≥1 shared instruction
- Saves a PNG visualisation and prints a text adjacency list
"""

from collections import defaultdict
from pathlib import Path


def build_sharing_graph(ext_map: dict[str, list[str]]) -> dict[str, set[str]]:
    """
    Return adjacency dict: ext -> {other_exts that share ≥1 instruction}.
    """
    # Invert: mnemonic -> [extensions]
    mnemonic_to_exts: dict[str, list[str]] = defaultdict(list)
    for ext, mnemonics in ext_map.items():
        for m in mnemonics:
            mnemonic_to_exts[m].append(ext)

    graph: dict[str, set[str]] = defaultdict(set)
    for exts in mnemonic_to_exts.values():
        if len(exts) < 2:
            continue
        for i, a in enumerate(exts):
            for b in exts[i + 1:]:
                graph[a].add(b)
                graph[b].add(a)

    return dict(graph)


def print_text_graph(graph: dict[str, set[str]]) -> None:
    """Print a simple adjacency list."""
    print("\n=== Tier 3: Extension Sharing Graph (text) ===")
    if not graph:
        print("  No shared instructions found between extensions.")
        return
    for node in sorted(graph):
        neighbours = ", ".join(sorted(graph[node]))
        print(f"  {node:<30} <-> {neighbours}")


def save_visual_graph(graph: dict[str, set[str]], out_path: Path = Path("extension_graph.png")) -> None:
    """Save a matplotlib/networkx graph PNG. Skips gracefully if libs missing."""
    try:
        import networkx as nx
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("  [graph] matplotlib/networkx not installed — skipping PNG.")
        return

    G = nx.Graph()
    for node, neighbours in graph.items():
        for nb in neighbours:
            G.add_edge(node, nb)

    if G.number_of_nodes() == 0:
        print("  [graph] No edges to draw.")
        return

    plt.figure(figsize=(14, 10))
    pos = nx.spring_layout(G, seed=42, k=1.5)
    nx.draw_networkx(
        G, pos,
        node_size=600,
        node_color="#4a90d9",
        font_size=7,
        font_color="white",
        edge_color="#aaaaaa",
        width=0.8,
    )
    plt.title("RISC-V Extension Sharing Graph", fontsize=14)
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"  [graph] Saved to {out_path}")


def run_tier3(ext_map: dict[str, list[str]]) -> dict[str, set[str]]:
    graph = build_sharing_graph(ext_map)
    print_text_graph(graph)
    save_visual_graph(graph)
    return graph