import pandas as pd
import numpy as np
import argparse

class StitchrPreprocess:
    def __init__(self, input_file, output_file):
        try:
            # if extension txt or tsv open with sep \t
            if input_file.endswith('.txt') or input_file.endswith('.tsv'):
                self.data = pd.read_csv(input_file, sep="\t", encoding="unicode_escape")
            elif input_file.endswith('.xlsx') or input_file.endswith('.xls'):
                self.data = pd.read_excel(input_file)
            elif input_file.endswith('.csv'):
                # allow auto-detection of delimiter (handles ; , \t etc.)
                self.data = pd.read_csv(input_file, sep=None, engine="python", encoding='cp1252')
            else:
                raise ValueError(f"File format {input_file} not supported")
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {input_file}")
        
        self.output_file = output_file
        
    def preprocess(self):
        # if "CDR3_alpha" not in self.data.columns or "V_alpha" not in self.data.columns or "J_alpha" not in self.data.columns:
        #     self.data["CDR3_alpha"] = np.nan
        #     self.data["V_alpha"] = np.nan
        #     self.data["J_alpha"] = np.nan

        # # Rename columns to TRA_CDR3, TRB_CDR3, TRAV, TRAJ, TRBV, TRBJ
        # self.data = self.data.rename(columns={"CDR3_alpha": "TRA_CDR3", "CDR3_beta": "TRB_CDR3",
        #                  "V_beta": "TRBV", "J_beta":"TRBJ",
        #                  "V_alpha": "TRAV", "J_alpha": "TRAJ"})

        # # ---------------------------------------------------------
        # # FIX: Only add missing columns to avoid duplicates
        # # ---------------------------------------------------------
        # required_cols = [
        #     "TRAC", "TRBC", "TRA_leader", "TRB_leader",
        #     "Linker", "Link_order",
        #     "TRA_5_prime_seq", "TRA_3_prime_seq",
        #     "TRB_5_prime_seq", "TRB_3_prime_seq"
        # ]
        # Map alternative column names to the standard names Stitchr expects.
        column_mapping = {
            "CDR3_alpha": "TRA_CDR3",
            "CDR3_beta": "TRB_CDR3",
            "V_alpha": "TRAV",
            "J_alpha": "TRAJ",
            "V_beta": "TRBV",
            "J_beta": "TRBJ",
        }

        for source, target in column_mapping.items():
            if source in self.data.columns and target not in self.data.columns:
                self.data = self.data.rename(columns={source: target})

         # Add missing columns only when neither naming convention supplied them.
        required_tcr_columns = [
            "TRA_CDR3", "TRB_CDR3",
            "TRAV", "TRAJ", "TRBV", "TRBJ",]



        for col in required_tcr_columns:
            if col not in self.data.columns:
                self.data[col] = np.nan
        # ---------------------------------------------------------

        # If TCR_name not present increment a number 
        if 'TCR_name' not in self.data.columns:
            self.data['TCR_name'] = self.data.index
        
        if self.data['TCR_name'].isnull().all():
             self.data['TCR_name'] = self.data.index

        columns_order = ["TCR_name", "TRAV", "TRAJ", "TRA_CDR3",
                         "TRBV", "TRBJ", "TRB_CDR3", "TRAC", "TRBC",
                         "TRA_leader", "TRB_leader", "Linker",
                         "Link_order", "TRA_5_prime_seq",
                         "TRA_3_prime_seq", "TRB_5_prime_seq", "TRB_3_prime_seq"]
        
        self.data = self.data.loc[:, ~self.data.columns.duplicated()]

        self.data = self.data.reindex(columns=columns_order)

        self.data.to_csv(self.output_file, index=False, sep="\t")

        print(f"Stitchr pre-processing done!")
        print(f"Saved dataset for stitchr: {self.output_file}")
        print(f"Number of TCRs: {len(self.data)}")

        return self.data

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", help="Input file (should contain at least CDR3_beta, V_beta, J_beta alpha optional)", required=True)
    parser.add_argument("-o", "--output", help="Output file", required=True)
    args = parser.parse_args()
    
    stitchr_compatible = StitchrPreprocess(args.input, args.output)
    stitchr_compatible.preprocess()
