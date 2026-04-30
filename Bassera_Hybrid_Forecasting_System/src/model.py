import torch
import torch.nn as nn


class FinanceForecaster(nn.Module):
    """
    Upgraded Sequence-to-Sequence GRU for joint expense + income forecasting.

    Architecture:
        1. GRU Encoder       : Processes the 35-day historical transaction window.
                              Hidden size doubled to 128 for greater capacity.
        2. Attention Layer   : Soft attention weighs the most relevant days in the
                              window before compressing to a single context vector.
        3. Shared Trunk      : A deep feedforward that fuses context + future anchors.
        4. Expense Head      : Softplus output — expense is always non-negative.
        5. Income Head       : Separate Softplus output — modelled independently so
                              its learning signal does not interfere with expenses.

    Outputs: Tensor of shape [batch, 2] where col-0 = expense, col-1 = income.
    """
    def __init__(
        self,
        input_size: int,
        future_size: int,
        hidden_size: int = 128,
        num_layers: int = 2,
        dropout: float = 0.2,
    ) -> None:
        super().__init__()

        self.gru = nn.GRU(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0.0,
            bidirectional=False,
        )

        # Soft attention: compress the time dimension into one context vector
        self.attn = nn.Linear(hidden_size, 1, bias=False)

        # Shared trunk that fuses historical context + temporal future anchors
        trunk_input = hidden_size + future_size
        self.trunk = nn.Sequential(
            nn.Linear(trunk_input, 256),
            nn.LayerNorm(256),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(256, 128),
            nn.LayerNorm(128),
            nn.GELU(),
            nn.Dropout(dropout * 0.5),
        )

        # Separate output heads so each signal gets its own gradient path
        self.expense_head = nn.Sequential(nn.Linear(128, 32), nn.GELU(), nn.Linear(32, 1), nn.Softplus())
        self.income_head  = nn.Sequential(nn.Linear(128, 32), nn.GELU(), nn.Linear(32, 1), nn.Softplus())

    def encode(self, x_seq: torch.Tensor) -> torch.Tensor:
        """
        Compress the historical 35-day sequence into an attention-weighted context.

        Args:
            x_seq: Shape [batch, seq_len, input_size]
        Returns:
            Shape [batch, hidden_size]
        """
        out, _ = self.gru(x_seq)               # [batch, seq_len, hidden]
        scores = torch.softmax(self.attn(out), dim=1)  # [batch, seq_len, 1]
        h = torch.sum(scores * out, dim=1)     # [batch, hidden]
        return h

    def forward(self, x_seq: torch.Tensor, x_future: torch.Tensor) -> torch.Tensor:
        """
        Full forward pass.

        Args:
            x_seq:   Historical data [batch, seq_len, input_size]
            x_future: Future temporal anchors [batch, future_size]
        Returns:
            Tensor [batch, 2] — (expense, income)
        """
        h       = self.encode(x_seq)
        combined = torch.cat([h, x_future], dim=-1)
        shared  = self.trunk(combined)
        expense = self.expense_head(shared)
        income  = self.income_head(shared)
        return torch.cat([expense, income], dim=-1)   # [batch, 2]

    # Keep `.decoder` as a property pointing at the trunk so inference.py still works
    @property
    def decoder(self):
        """Compatibility shim — inference calls model.decoder(combined)."""
        class _Decoder(nn.Module):
            def __init__(self_, trunk, expense_head, income_head):
                super().__init__()
                self_.trunk = trunk
                self_.expense_head = expense_head
                self_.income_head  = income_head
            def forward(self_, x):
                shared  = self_.trunk(x)
                expense = self_.expense_head(shared)
                income  = self_.income_head(shared)
                return torch.cat([expense, income], dim=-1)
        return _Decoder(self.trunk, self.expense_head, self.income_head)


class CashflowLoss(nn.Module):
    """
    Composite loss for joint expense + income regression.

    Strategy
    --------
    - **Expense** (col 0): Huber loss (robust to rare spending spikes) + MAE for
      median grounding.  Weighted 60 / 40 (Huber / MAE).
    - **Income** (col 1): Higher weight because the income signal is sparser and
      the model needs a stronger gradient to avoid always predicting 0.
      Same Huber + MAE blend but the overall income term is multiplied by
      `income_weight` (default 2.0) to balance the learning.
    """
    def __init__(self, alpha: float = 0.6, income_weight: float = 2.0, huber_delta: float = 1.0) -> None:
        super().__init__()
        self.alpha         = alpha
        self.income_weight = income_weight
        self.huber         = nn.HuberLoss(delta=huber_delta)

    def forward(self, pred: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
        # pred / target both shape [batch, 2]
        p_exp, t_exp = pred[:, 0:1], target[:, 0:1]
        p_inc, t_inc = pred[:, 1:2], target[:, 1:2]

        loss_exp = self.alpha * self.huber(p_exp, t_exp) + (1 - self.alpha) * nn.functional.l1_loss(p_exp, t_exp)
        loss_inc = self.alpha * self.huber(p_inc, t_inc) + (1 - self.alpha) * nn.functional.l1_loss(p_inc, t_inc)

        return loss_exp + self.income_weight * loss_inc


# Backwards-compat alias so train.py can keep importing ExpenseLoss
ExpenseLoss = CashflowLoss
