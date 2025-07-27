import csv
import os

INPUT_GENES_FILE = "input_files/original_gene_list.txt"
INTERACTIONS_FILE = "input_files/0.4-ppi_edges.tsv"
THRESHOLD = 0.4
OUTPUT_DIR = "output_files"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Load RP gene list
with open(INPUT_GENES_FILE, "r") as f:
    rp_genes = set(g.strip().upper() for g in f if g.strip())
print(f"[INFO] Loaded {len(rp_genes)} unique genes from {INPUT_GENES_FILE}")

# Load STRING interactions
edges = []
with open(INTERACTIONS_FILE, "r") as f:
    header_line = f.readline()
    if header_line.startswith("#"):
        header_line = header_line.lstrip("#")
    header = header_line.strip().split("\t")

    reader = csv.DictReader(f, fieldnames=header, delimiter="\t")
    for row in reader:
        try:
            g1 = row["node1"].strip().upper()
            g2 = row["node2"].strip().upper()
            score = float(row["combined_score"])
        except (KeyError, ValueError):
            continue
        edges.append((g1, g2, score))
print(f"[INFO] Parsed {len(edges)} edges from STRING")

# Identify Group A
group_a = set()
for g1, g2, score in edges:
    if g1 in rp_genes and g2 in rp_genes and score >= THRESHOLD:
        group_a.update([g1, g2])
print(f"[INFO] Group A (directly connected): {len(group_a)}")

# Identify Groups B and D
group_b = set()
group_d = set()
intermediate_map = {}

for gene in rp_genes - group_a:
    for g1, g2, score in edges:
        if score < THRESHOLD:
            continue
        if gene == g1 and g2 not in rp_genes:
            intermediate = g2
        elif gene == g2 and g1 not in rp_genes:
            intermediate = g1
        else:
            continue

        # Now see if the intermediate connects to any Group A gene
        for x1, x2, s2 in edges:
            if s2 < THRESHOLD:
                continue
            if (x1 == intermediate and x2 in group_a) or (x2 == intermediate and x1 in group_a):
                group_b.add(gene)
                group_d.add(intermediate)
                intermediate_map[gene] = intermediate
                break
        if gene in group_b:
            break

group_c = rp_genes - group_a - group_b

# === Save Outputs ===
with open(os.path.join(OUTPUT_DIR, "gene_group.txt"), "w") as f:
    f.write("Group A: Input gene that has direct connection with another input gene\n---\n")
    for g in sorted(group_a):
        f.write(f"{g}\n")
    f.write("\n\nGroup B: Input gene that is indirectly connected to another input gene, via an intermediate gene\n---\n")
    for g in sorted(group_b):
        f.write(f"{g}\n")
    f.write("\n\nGroup C: Input gene that is not directly or indirectly connected to another input gene\n---\n")
    for g in sorted(group_c):
        f.write(f"{g}\n")
    f.write("\n\nGroup D: Intermediate gene that connects Group B genes with Group A or other Group B genes\n---\n")
    for g in sorted(group_d):
        f.write(f"{g}\n")

with open(os.path.join(OUTPUT_DIR, "intermediate_genes.txt"), "w") as f:
    for g in sorted(group_d):
        f.write(f"{g}\n")

with open(os.path.join(OUTPUT_DIR, "intermediate_mapping.txt"), "w") as f:
    for g, inter in intermediate_map.items():
        f.write(f"{g}\t{inter}\n")

print(f"[INFO] Group B (need intermediates): {len(group_b)}")
print(f"[INFO] Group D (Group B resolved with intermediates): {len(group_d)}")
print(f"[INFO] Group C (unconnected after search): {len(group_c)}")
print("✅ Outputs saved: gene_group.txt, intermediate_genes.txt, intermediate_mapping.txt")