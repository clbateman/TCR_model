# TCR_model
Creates models of TCRs in PDB format from CDR3 sequences and V/J names or sequences using stitchr and tfold.


### **PIPELINE**

For the whole pipeline, run script `run_structure_pipeline.sh` or `run_structure_pipeline.slurm.sh`

The script will run stitchr preprocessing, stitchr, tfold preprocessing and tfold. 

Input is the dataset containing CDR3 and V/J names or sequences (alpha and beta chains).
Output is the PDB files of the TCRs. 

Usage:
    `bash run_structure_pipeline.sh <input_dataset> <dataset_name or identifier>`
    or on slurm:
    `sbatch run_structure_pipeline.slurm.sh <input_dataset> <dataset_name or identifier>`

#### Steps:

### Stitchr

run scripts:
1. `stitchr_preprocess.py`
2. `run_stitchr.py`

Input is a dataset containing 
* CDR3 alpha and beta sequences
* V and J alpha and beta gene names or sequences

Output is a JSON file containing full sequences for alpha and beta chains

### tfold

run scripts:
1. `preprocessing_to_tfold.py`
2. `run_tfold.slurm.sh or run_tfold.py` 

optional: run pdbfixer on pdbs if missing hydrogens or interactions <-- Still does not always work for screening

Input is the JSON list of TCR chain sequences

### Outputs

The pipeline creates PDB format structures of TCRs that can be used for virtual screening with different peptides. 
