"""
Main Entry Point for the Baseera Forecaster.

This module provides the Command Line Interface (CLI) to trigger 
either the training or inference pipelines for the hybrid financial 
forecasting model.
"""

import argparse
from .pipeline import train_pipeline, infer_pipeline
from .utils import set_seed

def main() -> None:
    """
    Parses CLI arguments and executes the requested Baseera pipeline.
    """
    parser = argparse.ArgumentParser(description="Baseera Hybrid Finance Forecaster")
    parser.add_argument(
        "--mode", 
        choices=["train", "infer"], 
        required=True,
        help="Whether to train the GRU or run inference."
    )
    parser.add_argument(
        "--user_file", 
        type=str, 
        required=True,
        help="Path to the JSON ledger of transactions."
    )
    parser.add_argument(
        "--epochs", 
        type=int, 
        default=500,
        help="Number of epochs to train the GRU."
    )
    parser.add_argument(
        "--batch_size", 
        type=int, 
        default=64,
        help="Batch size for training."
    )
    parser.add_argument(
        "--lr", 
        type=float, 
        default=1e-3,
        help="Learning rate for AdamW optimizer."
    )
    parser.add_argument(
        "--seed", 
        type=int, 
        default=42,
        help="Random seed for reproducibility."
    )
    
    args = parser.parse_args()
    set_seed(args.seed)

    if args.mode == "train":
        train_pipeline(args)
    else:
        infer_pipeline(args)


if __name__ == "__main__":
    main()
