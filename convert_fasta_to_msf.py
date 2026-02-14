import sys
import os
from Bio import AlignIO

def convert_fasta_to_msf(input_fasta, output_msf):
    """
    Converts an aligned FASTA file to MSF format.
    """
    if not os.path.exists(input_fasta):
        print(f"Error: Input file not found: {input_fasta}")
        sys.exit(1)

    try:
        # AlignIO.convert returns the number of alignments converted (should be 1 for a single file)
        count = AlignIO.convert(input_fasta, "fasta", output_msf, "msf")
        print(f"Successfully converted {count} alignment(s).")
        print(f"Output saved to: {output_msf}")
    except Exception as e:
        print(f"Error during conversion: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python convert_fasta_to_msf.py <input_aligned.fasta> <output.msf>")
        sys.exit(1)
    
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    
    convert_fasta_to_msf(input_path, output_path)
