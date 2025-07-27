import csv
from collections import defaultdict

INPUT_FILE = "input_files/0.4-ppi_edges.tsv"
OUTPUT_FILE = "info_files/gene_database.txt"
THRESHOLD = 0.4

interactions = defaultdict(dict)

with open(INPUT_FILE, "r") as f:
    reader = csv.reader(f, delimiter="\t")
    for row in reader:
        if row[0].startswith("#"):
            header = [col.lstrip("#") for col in row]  # extract actual column names
            idx_node1 = header.index("node1")
            idx_node2 = header.index("node2")
            idx_score = header.index("combined_score")
            continue  # skip header
        try:
            g1 = row[idx_node1].strip().upper()
            g2 = row[idx_node2].strip().upper()
            score = float(row[idx_score])
            if score >= THRESHOLD:
                interactions[g1][g2] = score
                interactions[g2][g1] = score
        except Exception as e:
            print(f"[WARN] Skipping row due to error: {e}")

# Write gene_database.txt
with open(OUTPUT_FILE, "w") as f:
    for gene, partners in sorted(interactions.items()):
        if partners:
            line = gene + "-" + ",".join(f"{p}({s:.3f})" for p, s in sorted(partners.items()))
            f.write(line + "\n")

print(f"[INFO] Wrote {len(interactions)} genes to: {OUTPUT_FILE}")