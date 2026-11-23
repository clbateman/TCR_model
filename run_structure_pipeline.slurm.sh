#!/bin/bash

#SBATCH --job-name=pipeline_tcr_structure
#SBATCH --output=outs/%x_%j.out
#SBATCH --error=outs/%x_%j.err
#SBATCH --cpus-per-task=8
#SBATCH --mem=500G

# --------------------------------------------------------
# 1. Setup environment
# --------------------------------------------------------
source /shared/ifbstor1/software/miniconda/etc/profile.d/conda.sh
conda activate /shared/projects/fine_tuning_for_tcr_specificity_prediction/envs/tfold


set -euo pipefail


# ===========================================================
# TCR structural preprocessing pipeline on slurm cluster
#
# Pipeline:

#   input dataset: dataset containing CDR3 sequences and V/J gene information (alpha and beta chains)
#        ↓↓
# Stitchr preprocessing
#        ↓↓ 
#     Stitchr
#        ↓↓ 
# TFold preprocessing
#        ↓↓
#      TFold: predicted TCR structures in PDB format
#
# Usage:
#   sbatch run_structure_pipeline.slurm.sh <input_dataset> <dataset_name or identifier>
#   sbatch run_structure_pipeline.slurm.sh data/mouse_dataset.csv mouse_dataset
#
# ===========================================================


# Check arguments

if [ "$#" -ne 2 ]; then
    echo "Usage:"
    echo "  $0 <input_dataset> <dataset_name>"
    echo
    echo "Example:"
    echo "  $0 data/mouse_dataset.csv mouse_dataset"
    exit 1
fi


INPUT_DATASET="$1"
DATASET_NAME="$2"


# Repository location

# SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT_DIR="/shared/projects/fine_tuning_for_tcr_specificity_prediction/TCR_model"

cd "$SCRIPT_DIR"


# Define scripts
PROJECT_DIR="/shared/projects/fine_tuning_for_tcr_specificity_prediction/TCR_model"
STITCHR_PREPROCESS="${PROJECT_DIR}/scripts/stitchr_preprocess.py"
STITCHR_SCRIPT="${PROJECT_DIR}/scripts/run_stitchr.py"
TFOLD_PREPROCESS="${PROJECT_DIR}/scripts/preprocessing_to_tfold.py"
TFOLD_SCRIPT="${PROJECT_DIR}/scripts/run_tfold.py"


# Define output directories

STITCHR_PREPROCESS_DIR="${PROJECT_DIR}/outputs/stitchr_preprocessed"
STITCHR_DIR="${PROJECT_DIR}/outputs/stitchr"
TFOLD_PREPROCESS_DIR="${PROJECT_DIR}/outputs/tfold_preprocessed"
TFOLD_DIR="${PROJECT_DIR}/outputs/tfold/${DATASET_NAME}"


# Define output files

STITCHR_PREPROCESSED="${STITCHR_PREPROCESS_DIR}/${DATASET_NAME}.tsv"

STITCHR_OUTPUT="${STITCHR_DIR}/${DATASET_NAME}.tsv"

TFOLD_JSON="${TFOLD_PREPROCESS_DIR}/${DATASET_NAME}.json"

TFOLD_METADATA="${TFOLD_PREPROCESS_DIR}/${DATASET_NAME}_metadata.tsv"


# Check input

if [ ! -f "$INPUT_DATASET" ]; then
    echo "[ERROR] Input dataset not found:"
    echo "        $INPUT_DATASET"
    exit 1
fi


# Create output directories

mkdir -p "$STITCHR_PREPROCESS_DIR"
mkdir -p "$STITCHR_DIR"
mkdir -p "$TFOLD_PREPROCESS_DIR"
mkdir -p "$TFOLD_DIR"


echo
echo "========================================================"
echo " TCR structural preprocessing pipeline"
echo "========================================================"
echo
echo "Input dataset:"
echo "  $INPUT_DATASET"
echo
echo "Dataset name:"
echo "  $DATASET_NAME"
echo
echo "========================================================"
echo

# STEP 1 — Stitchr preprocessing

echo "--------------------------------------------------------"
echo "STEP 1/4: Stitchr preprocessing"
echo "--------------------------------------------------------"

python "$STITCHR_PREPROCESS" \
    -i "$INPUT_DATASET" \
    -o "$STITCHR_PREPROCESSED"


if [ ! -f "$STITCHR_PREPROCESSED" ]; then
    echo
    echo "[ERROR] Stitchr preprocessing did not produce:"
    echo "        $STITCHR_PREPROCESSED"
    exit 1
fi


echo
echo "[OK] Stitchr preprocessing complete."
echo "     Output: $STITCHR_PREPROCESSED"
echo



# STEP 2 — Stitchr

echo "----------------------------------------------------"
echo "STEP 2/4: Stitchr"
echo "----------------------------------------------------"

python "$STITCHR_SCRIPT" \
    -i "$STITCHR_PREPROCESSED" \
    -o "$STITCHR_OUTPUT"


if [ ! -f "$STITCHR_OUTPUT" ]; then
    echo
    echo "[ERROR] Stitchr did not produce:"
    echo "        $STITCHR_OUTPUT"
    exit 1
fi


echo
echo "[OK] Stitchr complete."
echo "     Output: $STITCHR_OUTPUT"
echo


# STEP 3 — TFold preprocessing

echo "------------------------------------------------"
echo "STEP 3/4: TFold preprocessing"
echo "------------------------------------------------"

python "$TFOLD_PREPROCESS" \
    -i "$STITCHR_OUTPUT" \
    -o "$TFOLD_JSON" \
    -m "$TFOLD_METADATA"


if [ ! -f "$TFOLD_JSON" ]; then
    echo
    echo "[ERROR] TFold preprocessing did not produce:"
    echo "        $TFOLD_JSON"
    exit 1
fi

if [ ! -f "$TFOLD_METADATA" ]; then
    echo
    echo "[ERROR] TFold preprocessing did not produce:"
    echo "        $TFOLD_METADATA"
    exit 1
fi


echo
echo "[OK] TFold preprocessing complete."
echo "     JSON:     $TFOLD_JSON"
echo "     Metadata: $TFOLD_METADATA"
echo


# STEP 4 — TFold

echo "-------------------------------------------"
echo "STEP 4/4: TFold"
echo "-------------------------------------------"

python "$TFOLD_SCRIPT" \
    -i "$TFOLD_JSON" \
    -o "$TFOLD_DIR"


if [ ! -d "$TFOLD_DIR" ]; then
    echo
    echo "[ERROR] TFold output directory was not created:"
    echo "        $TFOLD_DIR"
    exit 1
fi


echo
echo "[OK] TFold complete."
echo "     PDBs: $TFOLD_DIR"
echo


# Finished

echo "======================================================="
echo " Pipeline completed successfully!"
echo "======================================================="
echo
echo "Input:"
echo "  $INPUT_DATASET"
echo
echo "Outputs:"
echo "  Stitchr preprocessing:"
echo "    $STITCHR_PREPROCESSED"
echo
echo "  Stitchr:"
echo "    $STITCHR_OUTPUT"
echo
echo "  TFold preprocessing:"
echo "    $TFOLD_JSON"
echo "    $TFOLD_METADATA"
echo
echo "  TFold PDBs:"
echo "    $TFOLD_DIR"
echo