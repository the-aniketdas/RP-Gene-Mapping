import os
from bs4 import BeautifulSoup

SVG_FILE = "svg_files/restructured_gene_map.svg"
OUTPUT_FILE = "output_files/gene_coords.txt"

def extract_coords_from_svg(svg_path, output_path):
    if not os.path.exists(svg_path):
        print(f"[ERROR] SVG file not found: {svg_path}")
        return

    with open(svg_path, "r") as f:
        soup = BeautifulSoup(f, "xml")

    # Map of gene name to coordinates
    coords = {}

    # Extract <text> elements that contain the gene names and positions
    for text_tag in soup.find_all("text"):
        if text_tag.string and text_tag.has_attr("x") and text_tag.has_attr("y"):
            gene = text_tag.string.strip().upper()
            try:
                x = int(float(text_tag["x"]))
                y = int(float(text_tag["y"]))
                coords[gene] = [x, y]
            except ValueError:
                continue  # Skip malformed coordinate entries

    # Write to file
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        f.write("The following pairings (Gene : Coords) indicate the coordinates of the gene in the restructured SVG file.\n\n")
        for gene in sorted(coords.keys()):
            f.write(f"{gene} : [{coords[gene][0]}, {coords[gene][1]}]\n")

    print(f"[INFO] Extracted {len(coords)} gene coordinates.")
    print(f"✅ Output saved to {output_path}")

# Run the extraction
if __name__ == "__main__":
    extract_coords_from_svg(SVG_FILE, OUTPUT_FILE)