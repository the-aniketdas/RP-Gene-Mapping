import os
from bs4 import BeautifulSoup

SVG_INPUT = os.path.join("input_files", "string_map.svg")
COORDS_FILE = os.path.join("output_files", "layout_coordinates.txt")
SVG_OUTPUT = os.path.join("restructured_gene_map.svg")

color_map = {
    "A": "#808080",
    "B": "#FFFF00",
    "C": "#a0a0a0",  # Not used, C will be removed
    "D": "#5fd35f",
}

# Load valid genes
print("[INFO] Loading layout_coordinates.txt...")
valid_genes = {}
with open(COORDS_FILE, "r", encoding="utf-8") as f:
    next(f)
    for line in f:
        parts = line.strip().split("\t")
        if len(parts) >= 4:
            gene = parts[0].strip().upper()
            group = parts[3].strip().upper()
            valid_genes[gene] = group
print(f"[INFO] Parsed {len(valid_genes)} valid gene group entries.")

# Parse SVG
print("[INFO] Parsing SVG...")
with open(SVG_INPUT, "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f, "xml")

edited = 0
removed = 0
valid_node_ids = set()

# Keep only A/B/D and recolor them
for g in soup.find_all("g", {"class": "nwnodecontainer"}):
    gene = g.get("data-safe_div_label", "").strip().upper()

    if not gene:
        for t in g.find_all("text"):
            if t and t.text:
                possible = t.text.strip().upper()
                if possible in valid_genes:
                    gene = possible
                    break

    group = valid_genes.get(gene)

    if not gene or group not in ("A", "B", "D"):
        g.decompose()
        removed += 1
        continue

    # Recolor
    bubble = g.find("circle", {"class": "nwbubblecoloredcircle"})
    if bubble and group in color_map:
        bubble["fill"] = color_map[group]
        edited += 1

    # Save valid node ID
    node_id = g.get("id", "")
    if node_id.startswith("node."):
        numeric_id = node_id.replace("node.", "").strip()
        valid_node_ids.add(numeric_id)

print(f"[INFO] Recolored {edited} A/B/D nodes.")
print(f"[INFO] Removed {removed} Group C or unknown nodes.")

# Remove edges that point to removed nodes
edge_removed = 0
for g in soup.find_all("g", {"class": "nwlinkwrapper"}):
    edge_id = g.get("id", "")
    if edge_id.startswith("edge."):
        parts = edge_id.replace("edge.", "").split(".")
        if len(parts) >= 2:
            src_id, tgt_id = parts[0], parts[1]
            if src_id not in valid_node_ids or tgt_id not in valid_node_ids:
                g.decompose()
                edge_removed += 1

print(f"[INFO] Removed {edge_removed} edges linked to missing nodes.")

with open(SVG_OUTPUT, "w", encoding="utf-8") as f:
    f.write(str(soup))
print(f"✅ Final cleaned + recolored SVG saved as {SVG_OUTPUT}")