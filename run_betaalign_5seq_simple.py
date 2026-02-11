import sys
import os
from align_with_betaalign import align_tfa

# --- CONFIGURATION FOR 5 SEQUENCES ---
# Update these paths if your folders are named differently
DEFAULT_MODEL_DIR = "checkpoints_amino_5seq"
DEFAULT_DATA_BIN = "data-bin-amino-5seq-processed"

def run_simple_5seq(input_tfa_path):
    if not os.path.exists(input_tfa_path):
        print(f"Error: File {input_tfa_path} does not exist.")
        return

    # Automatic output name definition
    base_name = os.path.splitext(input_tfa_path)[0]
    output_fasta_path = f"{base_name}_aligned_5seq.fasta"

    print("=== BetaAlign Wrapper (5 Sequences) ===")
    print(f"Input: {input_tfa_path}")
    print(f"Expected Output: {output_fasta_path}")
    print(f"Model Dir: {DEFAULT_MODEL_DIR}")
    print(f"Data Bin: {DEFAULT_DATA_BIN}")
    print("=======================================\n")
    
    # Check if model paths exist before running
    if not os.path.exists(DEFAULT_MODEL_DIR):
        print(f"[WARNING] Model directory '{DEFAULT_MODEL_DIR}' not found.")
        print("Please copy your trained model folder from Linux to this directory.")
        return
    if not os.path.exists(DEFAULT_DATA_BIN):
        print(f"[WARNING] Data-bin directory '{DEFAULT_DATA_BIN}' not found.")
        print("Please copy your 'data-bin' folder from Linux to this directory.")
        return

    # Run alignment
    align_tfa(
        input_path=input_tfa_path,
        model_dir=DEFAULT_MODEL_DIR,
        data_bin=DEFAULT_DATA_BIN,
        output_path=output_fasta_path,
        num_seqs=5
    )

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run_betaalign_5seq_simple.py <path_to_file.fasta_or_tfa>")
    else:
        run_simple_5seq(sys.argv[1])
