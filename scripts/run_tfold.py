"""
Run TFold on a JSON file containing alpha and beta TCR chains.
This script is a part of the TCR sequence to structure pipeline.

Input and output are specified as command line arguments:
    Input JSON should be generated using the preprocessing_to_tfold.py script.
    Output PDB files will be saved in the specified output directory.

usage:
    python run_tfold.py -i input.json -o output_dir

"""

import argparse
import json
import os
import ssl
import torch
import tfold
from tqdm import tqdm


# Arguments
parser = argparse.ArgumentParser(
    description="Run TFold on a JSON file containing paired TCR alpha and beta chains."
)

parser.add_argument(
    "-i", "--input",
    required=True,
    help="Input JSON file containing TCR chain sequences"
)

parser.add_argument(
    "-o", "--output-dir",
    required=True,
    help="Directory where TFold PDB files will be saved"
)

args = parser.parse_args()

input_json = args.input
output_dir = args.output_dir


# SSL
ssl._create_default_https_context = ssl._create_unverified_context


# Output directory
os.makedirs(output_dir, exist_ok=True)


# Device
device = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

print("Using device:", device)


# Load pretrained models

print("Loading TFold models...")

ppi_model_path = tfold.model.esm_ppi_650m_tcr()
tfold_model_path = tfold.model.tfold_tcr_trunk()

model = tfold.deploy.TCRPredictor.restore_from_module(
    ppi_model_path,
    tfold_model_path
)

model = model.to(device)
model.eval()


# Load input JSON

with open(input_json, "r") as f:
    tcr_entries = json.load(f)

print(f"Loaded {len(tcr_entries)} TCRs")


# Run prediction
successful = 0
failed = 0
skipped = 0

with torch.no_grad():

    for entry in tqdm(tcr_entries, desc="Running TFold"):

        name = entry.get("name", "unnamed")

        output_pdb = os.path.join(
            output_dir,
            f"tcr_{name}.pdb"
        )

        # Skip if already exists
        if os.path.exists(output_pdb):
            print(f"[SKIP] {name} already exists")
            skipped += 1
            continue

        chains = [
            {
                "id": c["id"],
                "sequence": c["sequence"]
            }
            for c in entry["chains"]
        ]

        try:
            model.infer_pdb(
                chains,
                output_pdb
            )

            print(f"[OK] {name}")
            successful += 1

        except Exception as e:
            print(f"[ERROR] Failed for TCR {name}: {e}")
            failed += 1


# Summary
print("\nTFold finished.")
print(f"Successful: {successful}")
print(f"Skipped:    {skipped}")
print(f"Failed:     {failed}")
print(f"Output directory: {output_dir}")