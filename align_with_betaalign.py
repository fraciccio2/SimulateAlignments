import sys
import os
import torch
import argparse
from Bio import SeqIO
from fairseq.models.transformer import TransformerModel
import summarize_results

# Required for recent PyTorch versions (2.6+) to load Fairseq checkpoints safely
if hasattr(torch.serialization, 'add_safe_globals'):
    torch.serialization.add_safe_globals([argparse.Namespace])

def align_tfa(input_path, model_dir, data_bin, output_path, num_seqs=10):
    """
    Aligns a file (FASTA or TFA) using a BetaAlign model (Fairseq Transformer).
    If the file is .tfa, it is converted to .fasta before processing.
    """
    if not os.path.exists(input_path):
        print(f"Error: File not found {input_path}")
        return

    # Handle .tfa -> .fasta conversion and supported extensions
    file_name, file_ext = os.path.splitext(input_path)
    ext = file_ext.lower()
    
    if ext == '.tfa':
        fasta_path = file_name + ".fasta"
        print(f"[INFO] Detected .tfa file. Converting: {input_path} -> {fasta_path}")
        try:
            records = list(SeqIO.parse(input_path, "fasta"))
            SeqIO.write(records, fasta_path, "fasta")
            input_path = fasta_path 
        except Exception as e:
            print(f"Error converting .tfa to .fasta: {e}")
            return
    elif ext not in ['.fasta', '.fa', '.faa']:
        print(f"\n[ERROR] Extension '{file_ext}' not supported.")
        print("Input file must be in .fasta or .tfa format\n")
        sys.exit(1)
    
    # 1. Load sequences from the file (now certainly .fasta or compatible)
    records = list(SeqIO.parse(input_path, "fasta"))
    
    # Logic for sequence count handling
    if len(records) < num_seqs:
        print(f"\n[CRITICAL ERROR] The file '{input_path}' contains only {len(records)} sequences.")
        print(f"The BetaAlign model requires EXACTLY {num_seqs} sequences to function.")
        print("Please add sequences or use a model trained differently.\n")
        sys.exit(1)
    
    elif len(records) > num_seqs:
        print(f"\n[INFO] The file contains {len(records)} sequences. Only the first {num_seqs} will be used.")
        records = records[:num_seqs]
        
        # Optional: Save a temporary file of the used sequences for traceability
        temp_fasta = input_path + ".10seq.temp.fasta"
        with open(temp_fasta, "w") as f:
            SeqIO.write(records, f, "fasta")
        print(f"[INFO] Created temporary copy of the 10 used sequences in: {temp_fasta}")

    # Prepare input in source format: "S E Q | S - Q | ..."
    # BetaAlign expects space-separated characters and " | " separated sequences
    source_seqs = [" ".join(list(str(record.seq))) for record in records]
    transformer_input = " | ".join(source_seqs)

    # 2. Load Fairseq Model
    print(f"Loading model from {model_dir}...")
    try:
        model = TransformerModel.from_pretrained(
            model_dir,
            checkpoint_file='checkpoint_best.pt',
            data_name_or_path=data_bin,
            source_lang='source',
            target_lang='target'
        )
    except Exception as e:
        print(f"Error loading model: {e}")
        print("Ensure model_dir contains 'checkpoint_best.pt' and data_bin contains the dictionaries.")
        return

    model.eval()
    if torch.cuda.is_available():
        model.cuda()
        print("Using GPU for inference.")
    else:
        print("Using CPU for inference.")

    # Input Length Check (Preventive)
    input_tokens = transformer_input.split()
    num_tokens = len(input_tokens)
    
    # Calculate minimum expected length (sum of all residues in input sequences)
    # The output MUST contain at least all input residues (plus gaps).
    total_residues = sum(len(str(r.seq)) for r in records)
    
    # DEBUG: Print joined input
    print("\n--- DEBUG: Transformer Input (Full) ---")
    print(transformer_input)
    print(f"Total Residues to Align: {total_residues}")
    print("--------------------------------------------------\n")

    # Fairseq models usually expose max_positions (tuple for source, target)
    # If not available, use the default 512 seen in the error
    max_pos = model.max_positions[0] if hasattr(model, 'max_positions') else 512
    
    if num_tokens > max_pos:
        print(f"\n[CRITICAL ERROR] Input too long for this model!")
        print(f"  - Current input length: {num_tokens} tokens")
        print(f"  - Model max limit:      {max_pos} tokens")
        print(f"  - Estimate per sequence: ~{int(max_pos/num_seqs)} amino acids")
        print("\nThe model was trained with a very short context (max 512 tokens total).")
        print("It is not possible to align full proteins with this configuration, only short fragments.")
        print("Suggestion: Try trimming the sequences or use a model trained with higher --max-source-positions.\n")
        return

    # 3. Inference (Translation)
    print("Aligning (this may take some time)...")
    with torch.no_grad():
        # Use beam search to improve alignment quality
        # min_len: Force output to be at least as long as the input residues (prevents truncation)
        # max_len_b: Allow enough space for output (residues + gaps)
        translated = model.translate(
            transformer_input, 
            beam=10, 
            min_len=total_residues,
            max_len_b=total_residues + 500
        )
    
    # 4. Output Post-processing "interleaved"
    # Output is a string of space-separated tokens: C1_S1 C1_S2 ... C1_S10 C2_S1 ...
    tokens = translated.split()
    
    # Consistency Check
    if len(tokens) % num_seqs != 0:
        print(f"Warning: Number of produced tokens ({len(tokens)}) is not a multiple of {num_seqs}.")
        print("The alignment might be incomplete or incorrect.")
    
    msa_rows = [[] for _ in range(num_seqs)]
    for i, token in enumerate(tokens):
        msa_rows[i % num_seqs].append(token)

    summarize_results.process_sequence_data(input_path, output_path)
    
    print(f"\nAlignment completed!")
    print(f"Result saved in: {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("BetaAlign Inference Tool")
        print("Usage: python align_with_betaalign.py <input.fasta/tfa> <model_dir> <data_bin> <output.fasta>")
        print("\nExample:")
        print("  python align_with_betaalign.py test.fasta checkpoints_amino data-bin-amino-processed msa_output.fasta")
    else:
        # Parameters passed from command line
        input_file = sys.argv[1]
        model_directory = sys.argv[2]
        data_bin_directory = sys.argv[3]
        output_file = sys.argv[4]
        
        align_tfa(input_file, model_directory, data_bin_directory, output_file)
