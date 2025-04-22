# -*- coding: utf-8 -*-
import csv
import os

# File paths
ANNOTATIONS_FILE = "input_files/string_annotations.tsv"
COORDS_FILE = "input_files/string_coords.tsv"
CHANGED_NAME_GENES = "info_files/changed_name_genes.txt"
GENE_GROUP_FILE = "info_files/gene_group.txt"
INTERMEDIATE_GENES_FILE = "info_files/intermediate_genes.txt"
OUTPUT_FILE = "output_files/layout_coordinates.txt"

GENE_TO_STRING = {}
STRING_COORDS = {}
GENE_GROUP = {}
INTERMEDIATES = set()

def loadGeneMappings():
    with open(CHANGED_NAME_GENES, 'r') as file:
        for line in file:
            gene, sid = line.strip().split('\t')
            GENE_TO_STRING[gene] = sid
    print(f"[DEBUG] Loaded {len(GENE_TO_STRING)} gene → STRING ID mappings")

def loadGeneGroups():
    with open(GENE_GROUP_FILE, 'r') as file:
        for line in file:
            gene, group = line.strip().split('\t')
            GENE_GROUP[gene] = group
    print(f"[DEBUG] Loaded {len(GENE_GROUP)} gene group labels")

def loadIntermediateGenes():
    with open(INTERMEDIATE_GENES_FILE, 'r') as file:
        for line in file:
            INTERMEDIATES.add(line.strip())
    print(f"[DEBUG] Loaded {len(INTERMEDIATES)} intermediate nodes")

def loadCoordinates():
    with open(COORDS_FILE, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter='\t')
        for row in reader:
            sid = row['identifier']
            STRING_COORDS[sid] = {
                'x': float(row['x_position']),
                'y': float(row['y_position']),
                'color': row['color'],
                'annotation': row['annotation'],
                'name': row['#node']
            }
    print(f"[DEBUG] Parsed {len(STRING_COORDS)} node coordinates")

def restructure():
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter='\t')
        writer.writerow(['#node', 'identifier', 'x_position', 'y_position', 'color', 'annotation'])

        count = 0
        for gene, group in GENE_GROUP.items():
            sid = GENE_TO_STRING.get(gene)
            if sid and sid in STRING_COORDS:
                coord = STRING_COORDS[sid]
                writer.writerow([
                    gene, sid, coord['x'], coord['y'],
                    coord['color'], coord['annotation']
                ])
                count += 1
            else:
                print(f"[WARN] Missing mapping or coords for gene {gene}")

        for sid in INTERMEDIATES:
            if sid in STRING_COORDS:
                coord = STRING_COORDS[sid]
                writer.writerow([
                    coord['name'], sid, coord['x'], coord['y'],
                    coord['color'], coord['annotation']
                ])
                count += 1
            else:
                print(f"[WARN] Intermediate STRING ID {sid} missing from coordinates")

    print(f"[INFO] Wrote {count} entries to {OUTPUT_FILE}")

if __name__ == "__main__":
    print("📥 Loading input files...")
    loadGeneMappings()
    loadGeneGroups()
    loadIntermediateGenes()
    loadCoordinates()
    restructure()
    print("✅ Done.")
