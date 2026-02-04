from datasets import load_dataset
import os

# Configuration
DATASET_NAME = "dotan1111/MSA-amino-10-seq"
OUTPUT_DIR = "data-bin-amino-5seq-raw"
ORIGINAL_NUM_SEQS = 10
TARGET_NUM_SEQS = 5

def prepare_data():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    
    print(f"Downloading dataset {DATASET_NAME}...")
    ds = load_dataset(DATASET_NAME)
    
    splits = ['train', 'test', 'validation']
    
    for split in splits:
        if split not in ds:
            continue
            
        print(f"Processing split: {split} for {TARGET_NUM_SEQS} sequences...")
        src_file = os.path.join(OUTPUT_DIR, f"{split}.source")
        tgt_file = os.path.join(OUTPUT_DIR, f"{split}.target")
        
        with open(src_file, 'w', encoding='utf-8') as f_src, \
             open(tgt_file, 'w', encoding='utf-8') as f_tgt:
            
            for item in ds[split]:
                # --- SOURCE ---
                source_dict = item['unaligned_seqs']
                source_list = []
                
                # Take only the first 5 sequences
                for k in range(TARGET_NUM_SEQS):
                    key = f"seq{k}"
                    if key in source_dict:
                        source_list.append(source_dict[key])
                    else:
                        source_list.append("") 
                
                # Format: "A C ... | D E ..."
                source_formatted = " | ".join([" ".join(list(seq)) for seq in source_list])
                
                # --- TARGET ---
                target_raw = item['MSA']
                if isinstance(target_raw, str):
                    total_len = len(target_raw)
                    if total_len % ORIGINAL_NUM_SEQS == 0:
                        seq_len = total_len // ORIGINAL_NUM_SEQS
                        
                        # Extract the 10 rows
                        msa_rows = [target_raw[i*seq_len : (i+1)*seq_len] for i in range(ORIGINAL_NUM_SEQS)]
                        
                        # Keep only first 5 rows
                        msa_rows_subset = msa_rows[:TARGET_NUM_SEQS]
                        
                        # Filter out all-gap columns
                        # We need to transpose to check columns
                        cols_to_keep = []
                        for col_idx in range(seq_len):
                            col_chars = [row[col_idx] for row in msa_rows_subset]
                            # If not all chars are gaps ('-'), keep this column
                            if not all(c == '-' for c in col_chars):
                                cols_to_keep.append(col_chars)
                        
                        # Now we have the valid columns, let's reconstruct the target
                        # Format: Column-Major Interleaved
                        # Row 0 Col 0, Row 1 Col 0... Row 4 Col 0, Row 0 Col 1...
                        
                        interleaved_tokens = []
                        if cols_to_keep:
                            num_valid_cols = len(cols_to_keep)
                            for col_chars in cols_to_keep:
                                for row_idx in range(TARGET_NUM_SEQS):
                                    interleaved_tokens.append(col_chars[row_idx])
                        else:
                            # Edge case: empty alignment
                            print("Warning: Alignment became empty after subsetting. Skipping.")
                            continue
                        
                        target_formatted = " ".join(interleaved_tokens)
                    else:
                        continue
                else:
                    continue

                f_src.write(source_formatted + "\n")
                f_tgt.write(target_formatted + "\n")
                
    print(f"Done! Files are in {OUTPUT_DIR}")

if __name__ == "__main__":
    prepare_data()
