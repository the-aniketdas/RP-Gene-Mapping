import os
from bs4 import BeautifulSoup

INPUT_SVG = "input_files/0.4-string_map.svg"
GENE_GROUP_FILE = "output_files/gene_group.txt"
OUTPUT_COORDS = "output_files/layout_coordinates.txt"

# === Step 1: Parse gene groups A, B, D from gene_group.txt ===
included_genes = {}
current_group = None
valid_groups = {"A", "B", "D"}

with open(GENE_GROUP_FILE, "r") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        if line.startswith("Group "):
            current_group = line.split(":")[0].split()[-1]
        elif current_group in valid_groups and not line.startswith("---"):
            included_genes[line.upper()] = current_group

print(f"[INFO] Loaded {len(included_genes)} genes from groups A/B/D.")

# === Step 2: Parse SVG and extract coordinates ===
with open(INPUT_SVG, "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f, "xml")

nodes = []
matched = 0
unmatched = 0

for g in soup.find_all("g", class_="nwnodecontainer"):
    gene = g.get("data-safe_div_label", "").strip().upper()
    if gene not in included_genes:
        unmatched += 1
        continue

    x = float(g.get("data-x_pos", 0))
    y = float(g.get("data-y_pos", 0))
    text = g.find_all("text")
    annotation = text[-1].text.strip() if text else ""
    group = included_genes[gene]
    nodes.append((gene, x, y, group, annotation))
    matched += 1

print(f"[INFO] Matched {matched} gene nodes with coordinates.")
print(f"[WARN] {unmatched} genes in SVG not in groups A/B/D")

# === Step 3: Write to layout_coordinates.txt ===
with open(OUTPUT_COORDS, "w") as f:
    f.write("name\tx\ty\tgroup\tannotation\n")
    for gene, x, y, group, annotation in nodes:
        f.write(f"{gene}\t{x}\t{y}\t{group}\t{annotation}\n")

print(f"✅ Wrote {len(nodes)} nodes to {OUTPUT_COORDS}")