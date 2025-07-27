from bs4 import BeautifulSoup

SEARCH_GENES = {"PRPF4", "CNGA3", "PDE6C"}  # Add any others you're seeing
SVG_FILE = "restructured_gene_map.svg"

with open(SVG_FILE, "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f, "xml")

matches = []
for tag in soup.find_all(["g", "text", "circle"]):
    content = tag.text.strip().upper() if tag.name == "text" else ""
    if any(gene in content for gene in SEARCH_GENES):
        matches.append(str(tag))

print(f"[INFO] Found {len(matches)} possible references to searched genes.")
if matches:
    print("\nFirst match:\n", matches[0])