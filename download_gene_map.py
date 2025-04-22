import os
import csv
from collections import defaultdict

INPUT_FOLDER = "input_files"
OUTPUT_FOLDER = "info_files"

EDGE_FILE = os.path.join(INPUT_FOLDER, "string_edges.tsv")
ANNOTATION_FILE = os.path.join(INPUT_FOLDER, "string_annotations.tsv")
GENE_LIST_FILE = os.path.join(INPUT_FOLDER, "original_gene_list.txt")

def debug_print_columns(path):
    with open(path, newline='') as f:
        header = f.readline().strip().split('\t')
        print(f"[DEBUG] Columns in {path} → {header}")
    return header

def load_gene_list():
    with open(GENE_LIST_FILE) as f:
        return [line.strip() for line in f if line.strip()]

def load_annotations():
    annotations = {}
    with open(ANNOTATION_FILE, newline='') as f:
        next(f)  # skip header
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 2:
                gene_symbol = parts[0].strip().upper()
                protein_id = parts[1].strip()
                if gene_symbol and protein_id:
                    annotations[gene_symbol] = protein_id
    return annotations

def load_edges():
    edges = {}
    with open(EDGE_FILE, newline='') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            a = row["node1_string_id"]
            b = row["node2_string_id"]
            try:
                score = float(row["combined_score"])
            except ValueError:
                score = 0.0
            edges.setdefault(a, []).append((b, score))
            edges.setdefault(b, []).append((a, score))  # ensure undirected
    return edges

def normalize_gene_names(gene_list, annotations):
    normalized = {}
    unidentifiable = []

    print("\n🔍 Matching gene names...")
    for gene in gene_list:
        key = gene.strip().upper()
        if key in annotations:
            normalized[gene] = annotations[key]
        else:
            print(f"[UNMATCHED] '{gene}' not found in annotations.")
            unidentifiable.append(gene)

    print(f"\n✅ Matched: {len(normalized)} genes")
    print(f"❌ Unmatched: {len(unidentifiable)} genes\n")

    print("🧾 Sample from annotation gene names:")
    for idx, g in enumerate(sorted(annotations.keys())):
        print(f"  {g}")
        if idx > 10: break

    return normalized, unidentifiable

def classify_genes(normalized_genes, edges, annotations):
    groups = {}
    intermediates = set()
    gene_ids = set(normalized_genes.values())

    print("\n🔍 Classifying genes based on connectivity...")
    for gene_name, gene_id in normalized_genes.items():
        if gene_id not in edges:
            groups[gene_name] = "C"
            print(f"[C] {gene_name} → no entry in edges")
            continue

        neighbors = edges[gene_id]
        direct = [n for n, _ in neighbors if n in gene_ids]
        if direct:
            groups[gene_name] = "A"
            print(f"[A] {gene_name} → directly connected to {len(direct)} other gene(s)")
        else:
            found = False
            for n, _ in neighbors:
                second_neighbors = edges.get(n, [])
                for nn, _ in second_neighbors:
                    if nn in gene_ids:
                        found = True
                        groups[gene_name] = "B"
                        print(f"[B] {gene_name} → indirectly connected via {n}")
                        intermediates.add(n)
                        break
                if found:
                    break
            if not found:
                groups[gene_name] = "C"
                print(f"[C] {gene_name} → no direct or indirect links")

        # Always record potential intermediates
        for n, _ in neighbors:
            second_neighbors = edges.get(n, [])
            for nn, _ in second_neighbors:
                if nn in gene_ids and n not in gene_ids:
                    intermediates.add(n)

    print(f"\n✅ Classification complete: {len(groups)} genes")
    print(f"🌐 Intermediates identified: {len(intermediates)} nodes")

    return groups, intermediates

def verify_all_intermediates(normalized, edges, annotations):
    gene_ids = set(normalized.values())
    intermediate_candidates = defaultdict(set)
    id_to_name = {v: k for k, v in annotations.items()}

    print("\n🔎 Verifying all intermediate nodes...")

    for gene_id in gene_ids:
        neighbors = edges.get(gene_id, [])
        for neighbor, _ in neighbors:
            if neighbor not in gene_ids:
                intermediate_candidates[neighbor].add(gene_id)

    true_intermediates = {k: v for k, v in intermediate_candidates.items() if len(v) >= 2}

    print(f"✅ Found {len(true_intermediates)} intermediates connecting ≥2 genes\n")

    for i, (inter_id, connected_genes) in enumerate(true_intermediates.items()):
        gene_names = [id_to_name.get(gid, gid) for gid in connected_genes]
        print(f"[INT] {inter_id} connects genes: {gene_names}")
        if i >= 10:
            print("... (truncated)")
            break

def save_output(groups, intermediates, normalized_genes, unidentifiable, annotations):
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    with open(os.path.join(OUTPUT_FOLDER, "gene_group.txt"), "w") as f:
        for g, c in sorted(groups.items()):
            f.write(f"{g}\t{c}\n")

    with open(os.path.join(OUTPUT_FOLDER, "intermediate_genes.txt"), "w") as f:
        for inter in sorted(intermediates):
            name = [k for k, v in annotations.items() if v == inter]
            label = name[0] if name else inter
            f.write(f"{label}\n")

    with open(os.path.join(OUTPUT_FOLDER, "changed_name_genes.txt"), "w") as f:
        for gene, gid in normalized_genes.items():
            f.write(f"{gene}\t{gid}\n")

    with open(os.path.join(OUTPUT_FOLDER, "unidentifiable_genes.txt"), "w") as f:
        for gene in unidentifiable:
            f.write(gene + "\n")

    with open(os.path.join(OUTPUT_FOLDER, "gene_database.txt"), "w") as f:
        f.write("Name\tSTRING_ID\n")
        for gene, gid in normalized_genes.items():
            f.write(f"{gene}\t{gid}\n")

if __name__ == "__main__":
    print("📥 Loading input files...")
    debug_print_columns(ANNOTATION_FILE)
    debug_print_columns(EDGE_FILE)

    genes = load_gene_list()
    annotations = load_annotations()
    edges = load_edges()

    print("🔎 Normalizing gene names...")
    normalized, unidentifiable = normalize_gene_names(genes, annotations)

    print("🔗 Classifying gene relationships...")
    groups, intermediates = classify_genes(normalized, edges, annotations)

    print("🧪 Running full intermediate check...")
    verify_all_intermediates(normalized, edges, annotations)

    print("💾 Saving output...")
    save_output(groups, intermediates, normalized, unidentifiable, annotations)

    print("✅ Done.")
