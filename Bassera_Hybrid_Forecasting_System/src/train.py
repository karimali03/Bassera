from pathlib import Path
from typing import List, Tuple

import numpy as np
import torch
from torch.utils.data import DataLoader

from .model import CashflowLoss


def train_model(
    model: torch.nn.Module,
    train_loader: DataLoader,
    val_loader: DataLoader,
    device: torch.device,
    epochs: int = 50,
    lr: float = 1e-3,
    checkpoint_path: Path | None = None,
) -> Tuple[torch.nn.Module, List[float], List[float]]:
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
        optimizer, T_max=epochs, eta_min=lr * 0.01
    )
    criterion = CashflowLoss(alpha=0.6, income_weight=2.0, huber_delta=500.0)

    best_val_loss = float("inf")
    patience = 25
    patience_counter = 0

    train_losses: List[float] = []
    val_losses: List[float] = []

    for epoch in range(epochs):
        model.train()
        epoch_train_loss = 0.0
        for x_seq, x_future, y in train_loader:
            x_seq = x_seq.to(device)
            x_future = x_future.to(device)
            y = y.to(device)

            optimizer.zero_grad()
            pred = model(x_seq, x_future)
            loss = criterion(pred, y)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()
            epoch_train_loss += loss.item()

        model.eval()
        epoch_val_loss = 0.0
        with torch.no_grad():
            for x_seq, x_future, y in val_loader:
                x_seq = x_seq.to(device)
                x_future = x_future.to(device)
                y = y.to(device)
                pred = model(x_seq, x_future)
                epoch_val_loss += criterion(pred, y).item()

        train_loss = epoch_train_loss / max(len(train_loader), 1)
        val_loss = epoch_val_loss / max(len(val_loader), 1)
        train_losses.append(train_loss)
        val_losses.append(val_loss)

        scheduler.step()

        print(f"Epoch {epoch + 1:02d} | train={train_loss:.4f} | val={val_loss:.4f}")

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            if checkpoint_path is not None:
                torch.save(model.state_dict(), checkpoint_path)
            patience_counter = 0
        else:
            patience_counter += 1
            if patience_counter >= patience:
                print("Early stopping triggered.")
                break

    if checkpoint_path is not None:
        model.load_state_dict(torch.load(checkpoint_path, map_location=device))
    return model, train_losses, val_losses


def predict_on_loader(
    model: torch.nn.Module, loader: DataLoader, device: torch.device
) -> Tuple[np.ndarray, np.ndarray]:
    model.eval()
    preds: List[np.ndarray] = []
    targets: List[np.ndarray] = []

    with torch.no_grad():
        for x_seq, x_future, y in loader:
            x_seq = x_seq.to(device)
            x_future = x_future.to(device)
            pred = model(x_seq, x_future).cpu().numpy()
            preds.append(pred)
            targets.append(y.numpy())

    return np.concatenate(preds, axis=0), np.concatenate(targets, axis=0)
