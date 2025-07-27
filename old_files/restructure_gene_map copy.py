import csv
import os

# File paths
INPUT_COORDS = os.path.join("input_files", "network_coordinates.tsv")
GENE_GROUP_FILE = os.path.join("info_files", "gene_group.txt")
INTERMEDIATES_FILE = os.path.join("info_files", "intermediate_genes.txt")
OUTPUT_FILE = os.path.join("output_files", "layout_coordinates.txt")

# Load group A/B/C classifications
gene_groups = {}
with open(GENE_GROUP_FILE, "r") as f:
    for line in f:
        parts = line.strip().split("\t")
        if len(parts) == 2:
            gene, group = parts
            gene_groups[gene.upper()] = group.upper()

# Load intermediates (Group D)
group_d = set()
with open(INTERMEDIATES_FILE, "r") as f:
    for line in f:
        gene = line.strip().upper()
        if gene:
            group_d.add(gene)

print(f"[INFO] Loaded {len(gene_groups)} genes from gene_group.txt")
print(f"[INFO] Loaded {len(group_d)} intermediate genes (Group D)")

# Read STRING network coordinates
nodes_written = 0
with open(INPUT_COORDS, "r", encoding="utf-8") as infile, \
     open(OUTPUT_FILE, "w", encoding="utf-8") as outfile:

    header = infile.readline().strip()
    if header.startswith("#"):
        header = header[1:]  # remove leading #
    reader = csv.DictReader(infile, delimiter="\t", fieldnames=header.split("\t"))

    outfile.write("name\tx\ty\tgroup\tannotation\n")

    for row in reader:
        name = row["node"].strip().upper()
        x = float(row["x_position"])
        y = float(row["y_position"])
        annotation = row["annotation"].strip()

        # Assign group: A/B/C/D or skip
        if name in gene_groups:
            group = gene_groups[name]
        elif name in group_d:
            group = "D"
        else:
            continue  # not in any group → skip

        outfile.write(f"{name}\t{x:.3f}\t{y:.3f}\t{group}\t{annotation}\n")
        nodes_written += 1

print(f"✅ Wrote {nodes_written} nodes to layout_coordinates.txt")
