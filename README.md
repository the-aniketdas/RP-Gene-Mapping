# RP (Retinitis Pigmentosa) Gene Mapping
Work is supplemental to the paper "Applying Gene Discovery and Gene Mapping to Identifying the Underlying Causes of Retinitis Pigmentosa", by Yu chien (Calvin) Ma, Akaash Venkat, Chun-Yu (Audi) Liu, Su Bin Yoon, and Dr. Jie Zheng.

- - - -

Note: The pipeline is written for **Python 3**. The earlier mention of Python 2.7 is outdated.
- - - -

If you only need the final visualizations, check the `svg_files/` folder included in the repository.


## How to Run the Pipeline

1. Download or clone this repository.
2. Open Terminal (Mac/Linux) or PowerShell (Windows).
3. Navigate into the `RP-Gene-Mapping` folder.
4. Run the following scripts in order:
* python3 generate_gene_database.py
* python3 identify_intermediate_genes.py
* python3 restructure_gene_map.py
* python3 recolor_gene_map.py

The final output will be saved at:  
`output_files/restructured_gene_map.svg`

---

## Required Input Files

Before running, ensure these are present in the `input_files/` folder:

- `original_gene_list.txt` — One RP gene per line (symbols, not STRING IDs)
- `0.4-ppi_edges.tsv` — Protein-protein interaction data (reciprocal tabular text output) from STRING  
  Must include at least:  
  `node1`, `node2`, and `combined_score` as tab-separated columns with a header row.
- `0.4-string_map.svg` - SVG map download from STRING
---

## Reset Instructions (When Changing Gene List)

If you modify `original_gene_list.txt`, you must rerun the full pipeline.
This ensures all groupings, mappings, and visualizations are regenerated from scratch.
Fresh exports of the ppi_edges.tsv and string_map.svg are needed every time anything changes.

---

## Output Files

### Intermediate Outputs

- `info_files/gene_database.txt` — All STRING symbols used for mapping  
- `output_files/gene_group.txt` — Categorization of RP genes into:
  - Group A: directly connected
  - Group B: indirectly connected via an intermediate
  - Group C: unconnected
  - Group D: intermediate connector genes
- `output_files/intermediate_genes.txt` — List of Group D genes
- `output_files/intermediate_mapping.txt` — Mapping of Group B genes to intermediates
- `output_files/layout_coordinates.txt` — SVG coordinate layout

### Final Output

- `output_files/restructured_gene_map.svg` — Cleaned, recolored, and trimmed network SVG

---

## Notes

- The threshold for STRING edges is set to `0.4` by default (see `identify_intermediate_genes.py`).
- No third-party libraries are required beyond standard Python 3.