#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import xml.etree.ElementTree as ET
from collections import defaultdict

GENE_GROUP = defaultdict(list)
GROUP_COLOR = {
    'A': 'rgb(117,239,168)',
    'B': 'rgb(239,117,117)',
    'C': 'rgb(117,117,239)'
}

GENE_TO_STRING = {}
LAYOUT_COORDS = {}
ANNOTATIONS = {}
INTERMEDIATE_GENES = set()

def readGeneGroups():
    with open("info_files/gene_group.txt", "r") as file:
        for line in file:
            gene, group_id = line.strip().split("\t")
            if group_id not in GROUP_COLOR:
                print(f"[WARN] Unknown group '{group_id}' for gene {gene}")
                GROUP_COLOR[group_id] = 'rgb(180,180,180)'  # fallback color
            GENE_GROUP[group_id].append(gene)

def readGeneToString():
    with open("info_files/changed_name_genes.txt", "r") as file:
        for line in file:
            gene, string_id = line.strip().split("\t")
            GENE_TO_STRING[gene] = string_id

def readLayoutCoords():
    with open("output_files/layout_coordinates.txt", "r") as file:
        header = next(file)
        for line in file:
            parts = line.strip().split("\t")
            if len(parts) < 6:
                continue
            gene, string_id, x, y, color, annotation = parts
            LAYOUT_COORDS[string_id] = {
                "gene": gene,
                "x": float(x),
                "y": float(y),
                "color": color,
                "annotation": annotation
            }

def readIntermediates():
    if not os.path.exists("info_files/intermediate_genes.txt"):
        return
    with open("info_files/intermediate_genes.txt", "r") as file:
        for line in file:
            INTERMEDIATE_GENES.add(line.strip())

def recolorSVG():
    tree = ET.parse("input_files/string_map.svg")
    root = tree.getroot()
    namespace = {"svg": "http://www.w3.org/2000/svg"}
    for node in root.findall(".//svg:g", namespace):
        title = node.find("svg:title", namespace)
        if title is None:
            continue
        string_id = title.text.strip()
        if string_id not in LAYOUT_COORDS:
            continue

        coord = LAYOUT_COORDS[string_id]
        color = None

        if string_id in INTERMEDIATE_GENES:
            color = 'rgb(255,179,0)'  # orange for intermediates
        else:
            gene = coord["gene"]
            for group_id, genes in GENE_GROUP.items():
                if gene in genes:
                    color = GROUP_COLOR.get(group_id)
                    break

        if color:
            for shape in node.findall(".//*", namespace):
                if 'fill' in shape.attrib:
                    shape.set('fill', color)

    tree.write("output_files/restructured_gene_map.svg")
    print("✅ SVG recoloring complete: output_files/restructured_gene_map.svg")

def parseInput():
    print("📥 Loading input files...")
    readGeneGroups()
    readGeneToString()
    readLayoutCoords()
    readIntermediates()

def main():
    parseInput()
    recolorSVG()

if __name__ == "__main__":
    main()
