import csv
import os
from collections import defaultdict

# Set paths
INPUT_DIR = "input_files"
GENE_LIST_FILE = os.path.join(INPUT_DIR, "original_gene_list.txt")
PPI_FILE = os.path.join(INPUT_DIR, "ppi_edges.tsv")

def load_gene_list(path):
    genes = set()
    with open(path, 'r') as f:
        for line in f:
            g = line.strip().upper()
            if g:
                genes.add(g)
    print(f"[INFO] Loaded {len(genes)} unique genes from {path}")
    return genes

def load_ppi_edges(path, score_threshold=0.4):
    ppi = defaultdict(list)
    edge_count = 0

    with open(path, 'r', encoding='utf-8') as f:
        # Handle STRING header with leading #
        first_line = f.readline()
        if first_line.startswith("#"):
            first_line = first_line[1:]  # remove hash

        headers = first_line.strip().split("\t")
        reader = csv.DictReader(f, delimiter="\t", fieldnames=headers)

        required_fields = {'node1', 'node2', 'combined_score'}
        if not required_fields.issubset(set(headers)):
            raise ValueError(f"[ERROR] Missing expected columns in TSV: {required_fields - set(headers)}")

        for row in reader:
            try:
                a = row["node1"].strip().upper()
                b = row["node2"].strip().upper()
                score = float(row["combined_score"])

                if score >= score_threshold:
                    ppi[a].append((b, score))
                    ppi[b].append((a, score))
                    edge_count += 1
            except Exception as e:
                print(f"[WARN] Skipped line due to parse error: {e}")

    print(f"[INFO] Parsed {edge_count} high-confidence edges from STRING")
    return ppi

def classify_genes(input_genes, ppi_graph):
    group_A, group_B = set(), set()
    for gene in input_genes:
        partners = [g for g, _ in ppi_graph.get(gene, []) if g in input_genes and g != gene]
        if partners:
            group_A.add(gene)
        else:
            group_B.add(gene)
    print(f"[INFO] Group A (directly connected): {len(group_A)}")
    print(f"[INFO] Group B (need intermediates): {len(group_B)}")
    return group_A, group_B

def find_intermediates(group_B, group_A, input_genes, ppi_graph):
    group_D = set()
    mapping = {}
    unresolved = set()

    for b in group_B:
        found = False
        for partner, score in sorted(ppi_graph.get(b, []), key=lambda x: -x[1]):
            if partner in input_genes:
                continue
            second_degree = [g for g, _ in ppi_graph.get(partner, []) if g in group_A]
            if second_degree:
                mapping[b] = (partner, second_degree)
                group_D.add(partner)
                found = True
                break
        if not found:
            unresolved.add(b)

    print(f"[INFO] Group B resolved with intermediates (Group D): {len(mapping)}")
    print(f"[INFO] Group C (unconnected after search): {len(unresolved)}")
    return mapping, group_D, unresolved

def save_outputs(input_genes, group_A, mapping, unresolved, group_D):
    with open("gene_group.txt", "w") as f:
        for g in input_genes:
            if g in group_A:
                f.write(f"{g}\tA\n")
            elif g in mapping:
                f.write(f"{g}\tB\n")
            else:
                f.write(f"{g}\tC\n")

    with open("intermediate_genes.txt", "w") as f:
        for d in sorted(group_D):
            f.write(f"{d}\n")

    with open("intermediate_mapping.txt", "w") as f:
        for b, (d, connects_to) in mapping.items():
            f.write(f"{b} → {d} → {', '.join(connects_to)}\n")

    print("✅ Outputs saved: gene_group.txt, intermediate_genes.txt, intermediate_mapping.txt")

# ============ Pipeline Execution ============

try:
    genes = load_gene_list(GENE_LIST_FILE)
    ppi_graph = load_ppi_edges(PPI_FILE)
    group_A, group_B = classify_genes(genes, ppi_graph)
    mapping, group_D, unresolved = find_intermediates(group_B, group_A, genes, ppi_graph)
    save_outputs(genes, group_A, mapping, unresolved, group_D)
except Exception as e:
    print(f"[FATAL] An error occurred: {e}")
