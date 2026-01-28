#!/bin/bash
set -e

# ==========================================
# CONFIGURATION
# ==========================================
RAW_DATA_DIR="data-bin-amino-raw"
PROCESSED_DATA_DIR="data-bin-amino-processed"
SAVE_DIR="checkpoints_amino"

# ==========================================
# 1. PREPROCESSING
# ==========================================
if [ -d "$PROCESSED_DATA_DIR" ]; then
    echo ">>> Found processed data in $PROCESSED_DATA_DIR. Skipping preprocessing..."
else
    echo ">>> Starting Preprocessing..."
    # We create a joined dictionary for source and target since they share the same alphabet (Amino Acids)
    fairseq-preprocess \
        --source-lang source --target-lang target \
        --trainpref "$RAW_DATA_DIR/train" \
        --validpref "$RAW_DATA_DIR/validation" \
        --testpref "$RAW_DATA_DIR/test" \
        --destdir "$PROCESSED_DATA_DIR" \
        --workers 8 \
        --joined-dictionary
fi

# ==========================================
# 2. TRAINING
# ==========================================
echo ">>> Starting Training..."

# Architecture: transformer_vaswani_wmt_en_de_big
# Adjusted for memory: update-freq might need to be higher on smaller GPUs
python run_fairseq_train_safe.py "$PROCESSED_DATA_DIR" \
    --save-dir "$SAVE_DIR" \
    --source-lang source --target-lang target \
    --arch transformer_vaswani_wmt_en_de_big \
    --share-all-embeddings \
    --optimizer adam --adam-betas '(0.9, 0.98)' --clip-norm 0.0 \
    --lr 5e-5 --lr-scheduler inverse_sqrt --warmup-updates 4000 \
    --dropout 0.3 --weight-decay 0.0001 \
    --criterion label_smoothed_cross_entropy --label-smoothing 0.1 \
    --max-tokens 4096 \
    --update-freq 4 \
    --max-source-positions 512 --max-target-positions 512 \
    --skip-invalid-size-inputs-valid-test \
    --validate-interval-updates 5000 \
    --save-interval-updates 5000 \
    --keep-interval-updates 5 \
    --no-epoch-checkpoints \
    --patience 10 \
    --fp16
