import sys
import os
from align_with_betaalign import align_tfa

# --- DEFAULT CONFIGURATION ---
# Paths relative to the project root
DEFAULT_MODEL_DIR = "checkpoints_amino"
DEFAULT_DATA_BIN = "data-bin-amino-processed"

def run_simple(input_tfa_path):
    if not os.path.exists(input_tfa_path):
        print(f"Error: File {input_tfa_path} does not exist.")
        return

    # Automatic output name definition
    # Example: "test.tfa" -> "test_aligned.fasta"
    base_name = os.path.splitext(input_tfa_path)[0]
    output_fasta_path = f"{base_name}_aligned.fasta"

    print("=== BetaAlign Wrapper ===")
    print(f"Input: {input_tfa_path}")
    print(f"Expected Output: {output_fasta_path}")
    print(f"Model: {DEFAULT_MODEL_DIR}")
    print("=========================\n")

    # Run alignment
    align_tfa(
        input_path=input_tfa_path,
        model_dir=DEFAULT_MODEL_DIR,
        data_bin=DEFAULT_DATA_BIN,
        output_path=output_fasta_path,
        num_seqs=10
    )

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run_betaalign_simple.py <path_to_file.fasta_or_tfa>")
    else:
        run_simple(sys.argv[1])
