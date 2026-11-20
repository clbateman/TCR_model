"""
Prepare stitched TCR sequences for TFold.
This script is a part of the TCR sequence to structure pipeline.
This script reads a TSV/CSV/XLSX file containing paired TCR alpha and beta chain sequences, filters valid pairs, and generates a JSON file suitable for TFold input.
It also saves a metadata TSV file containing relevant information for the valid paired TCRs.

Input and output are specified as command line arguments.
Input file should contain columns for TRA_aa and TRB_aa sequences, as well as other metadata columns from stitchr.
Output JSON will be used as input for TFold.

Usage:
    python preprocessing_to_tfold.py -i input_file -o output_json -m output_metadata
"""

import pandas as pd
import json
import os
import argparse

# input_file = "data/database_pooled_mouse_ann.csv"   # csv / tsv / xlsx
# output_json = "data/mouse_for_to_tfold.json"
# output_metadata = "data/mouse_metadata.tsv"

# input_file = "../tfold/data/gr/human_stitchred.tsv"
# output_json = "../tfold/data/gr/human_for_tfold.json"
# output_metadata = "../tfold/data/gr/human_metadata.tsv"

parser = argparse.ArgumentParser(
    description="Prepare stitched TCR sequences for TFold."
)

parser.add_argument(
    "-i", "--input",
    required=True,
    help="Input TSV/CSV/XLSX file containing stitched TRA_aa and TRB_aa sequences"
)

parser.add_argument(
    "-o", "--output",
    required=True,
    help="Output JSON file for TFold"
)

parser.add_argument(
    "-m", "--metadata",
    required=True,
    help="Output TSV file containing metadata for the valid paired TCRs"
)

args = parser.parse_args()

input_file = args.input
output_json = args.output
output_metadata = args.metadata

# Load dataset
ext = os.path.splitext(input_file)[1].lower()

if ext == ".xlsx":
    df = pd.read_excel(input_file, dtype=str)

elif ext == ".csv":
    df = pd.read_csv(input_file, dtype=str, sep=";")

elif ext == ".tsv":
    df = pd.read_csv(input_file, sep="\t", dtype=str)

else:
    raise ValueError(f"Unsupported file type: {ext}")

df = df.fillna("")

# Filter valid paired TCRs
df_valid = df[
    (df["TRA_aa"].str.strip() != "") &
    (df["TRB_aa"].str.strip() != "")
].copy()

print(f"Total rows: {len(df)}")
print(f"Valid paired TCRs: {len(df_valid)}")


# Build TFold JSON
tfold_data = []

for _, row in df_valid.iterrows():

    alpha_seq = row["TRA_aa"].strip()
    beta_seq = row["TRB_aa"].strip()

    entry = {
        "name": str(row["TCR_name"]),
        "chains": [
            {
                "id": "A",
                "sequence": alpha_seq
            },
            {
                "id": "B",
                "sequence": beta_seq
            }
        ]
    }

    tfold_data.append(entry)


# Save TFold JSON

# Create output directory if necessary
os.makedirs(os.path.dirname(output_json) or ".", exist_ok=True)

with open(output_json, "w") as f:
    json.dump(tfold_data, f, indent=2)

print(f"Saved TFold JSON: {output_json}")


# Save metadata table

metadata_columns = [
    "TCR_name",
    "TRA_CDR3",
    "TRB_CDR3",
    "TRAV",
    "TRAJ",
    "TRBV",
    "TRBJ"
]

# Keep only columns that exist
metadata_columns = [
    c for c in metadata_columns
    if c in df_valid.columns
]

os.makedirs(os.path.dirname(output_metadata) or ".", exist_ok=True)
df_valid[metadata_columns].to_csv(
    output_metadata,
    sep="\t",
    index=False
)

print(f"Tfold pre-processing done!Saved metadata TSV: {output_metadata}")