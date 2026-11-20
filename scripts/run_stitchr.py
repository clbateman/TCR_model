import pandas as pd
import subprocess
import argparse
import re

# input_file = "data/mouse_for_stitchr.tsv"
# output_file = "data/mouse_stitchred.tsv"

parser = argparse.ArgumentParser(
    description="Generate full TCR alpha and beta sequences using Stitchr."
)

parser.add_argument(
    "-i", "--input",
    required=True,
    help="Input TSV file containing TCR sequences and V/J genes"
)

parser.add_argument(
    "-o", "--output",
    required=True,
    help="Output TSV file with stitched TRA and TRB sequences"
)

args = parser.parse_args()

input_file = args.input
output_file = args.output

df = pd.read_csv(input_file, sep="\t", dtype=str, engine="python").fillna("")


def stitch_sequence(v_gene, j_gene, cdr3, chain_type="aa"):
    """
    Try stitchr with given V/J allele.
    If missing, fallback to *01 allele.
    """
    def run_stitch(v, j):
        # Construct command
        cmd = ["stitchr", "-s", "human", "-v", v, "-j", j, "-cdr3", cdr3]



        # if chain_type == "aa":
        #     cmd += ["--aa", "1"]  # specify AA output
        cmd += ["-m", "AA"]    










        result = subprocess.run(cmd, capture_output=True, text=True)
        stdout = result.stdout.strip()
        stderr = result.stderr.strip()
        seq = result.stdout.strip()

        # Stitchr may write allele warnings to either stdout or stderr.
        messages = stdout + "\n" + stderr

        allele_missing = (
            "Defaulting to *01" in messages or
            "No valid variable region allele determined" in messages or
            "No valid leader region allele determined" in messages or
            "No valid joining region allele determined" in messages
        )

        # Remove warning messages from stdout before extracting the sequence.
        stdout = re.split(
            r"No valid (?:leader|variable|joining) region allele determined yet",
            stdout,
            maxsplit=1
        )[0]

        # Keep FASTA sequence lines only, excluding headers and blank lines.
        seq_lines = [
            line.strip()
            for line in stdout.splitlines()
            if line.strip() and not line.strip().startswith(">")
        ]
        seq = "".join(seq_lines)

        # Keep only standard amino-acid letters.
        seq = re.sub(r"[^A-Za-z]", "", seq)

        if result.returncode != 0 or not seq:
            return None, allele_missing, result.returncode

        










        # # Extract sequence (skip header lines starting with '>')
        # seq_lines = [l for l in stdout.splitlines() if not l.startswith(">")]
        # seq = "".join(seq_lines) if seq_lines else None

        return seq, allele_missing, result.returncode





    # Try original allele
    seq, allele_missing, rc = run_stitch(v_gene, j_gene)
    if seq and rc == 0:
        return seq

    # If missing, fallback to *01
    v_base = v_gene.split("*")[0] + "*01"
    j_base = j_gene.split("*")[0] + "*01"
    seq, _, rc = run_stitch(v_base, j_base)
    if seq and rc == 0:
        print(f"Used fallback *01 for {v_gene}/{j_gene}")
        return seq

    # return empty string 
    print(f"Failed to stitch sequence for {v_gene}/{j_gene}/{cdr3}")
    print(f"\nFailed for:")
    print("Return code:", rc)
    return ""

# Iterate rows and generate sequences
TRA_aa_list = []
TRB_aa_list = []

for idx, row in df.iterrows():
    print(f"Processing row {idx}: {row['TRAV']}/{row['TRAJ']} - {row['TRA_CDR3']} | {row['TRBV']}/{row['TRBJ']} - {row['TRB_CDR3']}")
    
    # Alpha chain
    if pd.notna(row["TRA_CDR3"]) and pd.notna(row["TRAV"]) and pd.notna(row["TRAJ"]):
        alpha_seq = stitch_sequence(row["TRAV"], row["TRAJ"], row["TRA_CDR3"])
    else:
        alpha_seq = ""
    TRA_aa_list.append(alpha_seq)

    # Beta chain
    if pd.notna(row["TRB_CDR3"]) and pd.notna(row["TRBV"]) and pd.notna(row["TRBJ"]):
        beta_seq = stitch_sequence(row["TRBV"], row["TRBJ"], row["TRB_CDR3"])
    else:
        beta_seq = ""
    TRB_aa_list.append(beta_seq)

# Add sequences to dataframe
df["TRA_aa"] = TRA_aa_list
df["TRB_aa"] = TRB_aa_list

# Save updated TSV
df.to_csv(output_file, sep="\t", index=False)
print(f"Stitchr done! Updated TSV written to {output_file}")
