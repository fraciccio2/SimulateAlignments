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

                    # 1. We first need to decode the original 10-sequence structure
                    if total_len % ORIGINAL_NUM_SEQS == 0:
                        real_seq_len = total_len // ORIGINAL_NUM_SEQS

                        # Recover all 10 original rows
                        all_10_rows = [target_raw[i*real_seq_len : (i+1)*real_seq_len] for i in range(ORIGINAL_NUM_SEQS)]

                        # 2. SELECTION: Take only the first 5 rows
                        selected_rows = all_10_rows[:TARGET_NUM_SEQS]

                        # 3. INTERLEAVING: Process as if we only have 5 sequences
                        interleaved_tokens = []
                        for col_idx in range(real_seq_len):
                            for row_idx in range(TARGET_NUM_SEQS):
                                interleaved_tokens.append(selected_rows[row_idx][col_idx])

                        target_formatted = " ".join(interleaved_tokens)
                    else:
                        print(f"Warning: Original target length {total_len} not divisible by {ORIGINAL_NUM_SEQS}. Skipping.")
                        continue
                else:
                    print("Warning: Target format unknown. Skipping.")
                    continue

                f_src.write(source_formatted + "\n")
                f_tgt.write(target_formatted + "\n")

    print(f"Done! Files (sliced to {TARGET_NUM_SEQS} sequences) are in {OUTPUT_DIR}")

if __name__ == "__main__":
    prepare_data()