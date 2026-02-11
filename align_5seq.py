import sys
import os
# Import the alignment logic from the existing script
from align_with_betaalign import align_tfa

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("BetaAlign Inference Tool (5 Sequences)")
        print("Usage: python align_5seq.py <input.fasta/tfa> <model_dir> <data_bin> <output.fasta>")
        print("\nExample:")
        print("  python align_5seq.py test.fasta checkpoints_amino_5seq data-bin-amino-5seq-processed msa_output.fasta")
    else:
        # Parameters passed from command line
        input_file = sys.argv[1]
        model_directory = sys.argv[2]
        data_bin_directory = sys.argv[3]
        output_file = sys.argv[4]
        
        # Call the existing function forcing num_seqs=5
        print(f"Starting alignment for 5 sequences on file: {input_file}")
        align_tfa(input_file, model_directory, data_bin_directory, output_file, num_seqs=5)

