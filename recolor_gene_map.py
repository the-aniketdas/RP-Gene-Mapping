from bs4 import BeautifulSoup
import os

INPUT_SVG = "input_files/0.4-string_map.svg"
COORDS_FILE = "output_files/layout_coordinates.txt"
OUTPUT_SVG = "output_files/restructured_gene_map.svg"

# Group color mapping
GROUP_COLORS = {
    "A": "#7575ef",  # blue
    "B": "#FFFF00",  # yellow
    "D": "#66ff00",  # green
}

# === Step 1: Load valid gene layout & groups ===
valid_genes = {}
with open(COORDS_FILE, "r") as f:
    next(f)  # skip header
    for line in f:
        parts = line.strip().split("\t")
        if len(parts) >= 4:
            gene = parts[0].strip().upper()
            group = parts[3].strip().upper()
            valid_genes[gene] = group

print(f"[INFO] Parsed {len(valid_genes)} valid gene group entries.")

# === Step 2: Parse SVG ===
with open(INPUT_SVG, "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f, "xml")

# Step 2a: Remove or recolor gene nodes
kept_node_ids = set()
recolored_count = 0
removed_nodes = set()
group_color_counts = {"A": 0, "B": 0, "D": 0}

for g in soup.find_all("g", class_="nwnodecontainer"):
    gene = g.get("data-safe_div_label", "").strip().upper()
    group = valid_genes.get(gene)

    if group and group in GROUP_COLORS:
        bubble = g.find("circle", class_="nwbubblecoloredcircle")
        if bubble:
            bubble["fill"] = GROUP_COLORS[group]
            recolored_count += 1
            group_color_counts[group] += 1
        # Keep this node ID for edge pruning
        node_id = g.get("id", "")
        if node_id.startswith("node."):
            kept_node_ids.add(node_id.split(".")[1])
    else:
        g.decompose()
        removed_nodes.add(gene)

# === Step 3: Remove edges linked to removed nodes ===
removed_edges = 0
for edge in soup.find_all("g", class_="nwlinkwrapper"):
    edge_id = edge.get("id", "")
    parts = edge_id.split(".")
    if len(parts) == 3:
        source_id, target_id = parts[1], parts[2]
        if source_id not in kept_node_ids or target_id not in kept_node_ids:
            edge.decompose()
            removed_edges += 1

# === Final summary ===
print(f"[INFO] Recolored {recolored_count} A/B/D nodes.")
for grp in sorted(group_color_counts):
    print(f"  → Group {grp}: {group_color_counts[grp]} nodes recolored")
print(f"[INFO] Removed {len(removed_nodes)} Group C or unknown nodes.")
print(f"[INFO] Removed {removed_edges} edges linked to missing nodes.")

# === Save updated SVG ===
with open(OUTPUT_SVG, "w", encoding="utf-8") as f:
    f.write(str(soup))

print(f"✅ Final cleaned + recolored SVG saved as {OUTPUT_SVG}")