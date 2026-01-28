from datasets import load_dataset
import os

# Configuration
DATASET_NAME = "dotan1111/MSA-amino-10-seq"
OUTPUT_DIR = "data-bin-amino-raw"
NUM_SEQS = 10

def prepare_data():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    
    print(f"Downloading dataset {DATASET_NAME}...")
    ds = load_dataset(DATASET_NAME)
    
    splits = ['train', 'test', 'validation']
    
    for split in splits:
        if split not in ds:
            continue
            
        print(f"Processing split: {split}")
        src_file = os.path.join(OUTPUT_DIR, f"{split}.source")
        tgt_file = os.path.join(OUTPUT_DIR, f"{split}.target")
        
        with open(src_file, 'w', encoding='utf-8') as f_src, \
             open(tgt_file, 'w', encoding='utf-8') as f_tgt:
            
            for item in ds[split]:
                # --- SOURCE ---
                # Unaligned sequences separated by ' | '
                source_dict = item['unaligned_seqs']
                source_list = []
                for k in range(NUM_SEQS):
                    key = f"seq{k}"
                    if key in source_dict:
                        source_list.append(source_dict[key])
                    else:
                        source_list.append("") 
                
                # Format: "A C ... | D E ..." (Space separated tokens)
                source_formatted = " | ".join([" ".join(list(seq)) for seq in source_list])
                
                # --- TARGET ---
                # Interleaved Column-Major Format
                target_raw = item['MSA']
                if isinstance(target_raw, str):
                    total_len = len(target_raw)
                    if total_len % NUM_SEQS == 0:
                        seq_len = total_len // NUM_SEQS
                        # Split the single string back into 10 aligned sequences
                        msa_rows = [target_raw[i*seq_len : (i+1)*seq_len] for i in range(NUM_SEQS)]
                        
                        # Create Column-Major Interleaved format
                        # Row 0 Col 0, Row 1 Col 0, ... Row 9 Col 0, Row 0 Col 1 ...
                        interleaved_tokens = []
                        for col_idx in range(seq_len):
                            for row_idx in range(NUM_SEQS):
                                interleaved_tokens.append(msa_rows[row_idx][col_idx])
                        
                        target_formatted = " ".join(interleaved_tokens)
                    else:
                        print(f"Warning: Target length {total_len} not divisible by {NUM_SEQS}. Skipping item.")
                        continue
                else:
                    print("Warning: Target format unknown. Skipping.")
                    continue

                f_src.write(source_formatted + "\n")
                f_tgt.write(target_formatted + "\n")
                
    print(f"Done! Files are in {OUTPUT_DIR}")

if __name__ == "__main__":
    prepare_data()
