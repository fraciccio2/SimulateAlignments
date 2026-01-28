import sys
import torch
import argparse
from fairseq_cli.train import cli_main

# FIX for PyTorch 2.6+: Allow loading argparse.Namespace which Fairseq uses in checkpoints
if hasattr(torch.serialization, 'add_safe_globals'):
    torch.serialization.add_safe_globals([argparse.Namespace])

if __name__ == "__main__":
    sys.exit(cli_main())
