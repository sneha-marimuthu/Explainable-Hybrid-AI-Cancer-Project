"""
Uncertainty-Weighted Multi-Task Loss Formulation
Based on Kendall, Gal & Cipolla (CVPR 2018):
"Multi-task learning using uncertainty to weigh losses for scene geometry and semantics"
Balances task loss magnitudes dynamically via learnable homoscedastic variance parameters.
"""

import torch
import torch.nn as nn

class HomoscedasticUncertaintyLoss(nn.Module):
    def __init__(self, num_tasks=4):
        super(HomoscedasticUncertaintyLoss, self).__init__()
        # Learnable log-variance parameters: s_k = log(sigma_k^2)
        # Prevents negative variance and stabilizes optimization
        self.log_vars = nn.Parameter(torch.zeros(num_tasks, dtype=torch.float32))
        
        self.ce_diag = nn.CrossEntropyLoss()
        self.ce_stage = nn.CrossEntropyLoss()
        self.bce_tx = nn.BCEWithLogitsLoss()

    def cox_partial_loss(self, log_hazard, durations, events):
        """
        Negative partial log-likelihood of Cox proportional hazards model.
        """
        # Sort descending by event time
        order = torch.argsort(durations, descending=True)
        log_h = log_hazard[order].squeeze(-1)
        e = events[order].float()

        hazard_ratio = torch.exp(log_h)
        log_cumsum = torch.log(torch.cumsum(hazard_ratio, dim=0) + 1e-7)
        loss = -torch.sum((log_h - log_cumsum) * e) / (torch.sum(e) + 1e-7)
        return loss

    def forward(self, preds, targets):
        # Unpack targets
        target_diag = targets["diagnosis"]
        target_stage = targets["stage"]
        target_tx = targets["treatment"]
        durations = targets["durations"]
        events = targets["events"]

        # Compute individual task losses
        l_diag = self.ce_diag(preds["logits_diagnosis"], target_diag)
        l_stage = self.ce_stage(preds["logits_stage"], target_stage)
        l_tx = self.bce_tx(preds["logits_treatment"], target_tx)
        l_surv = self.cox_partial_loss(preds["log_hazard_survival"], durations, events)

        task_losses = [l_diag, l_stage, l_tx, l_surv]
        total_loss = 0.0
        weighted_breakdown = {}

        for k, (loss, name) in enumerate(zip(task_losses, ["diagnosis", "stage", "treatment", "survival"])):
            precision = torch.exp(-self.log_vars[k])
            # Kendall & Gal formula: 0.5 * exp(-s_k) * L_k + 0.5 * s_k
            task_weighted = 0.5 * precision * loss + 0.5 * self.log_vars[k]
            total_loss += task_weighted
            weighted_breakdown[name] = loss.item()
            weighted_breakdown[f"{name}_sigma"] = torch.exp(0.5 * self.log_vars[k]).item()

        return total_loss, weighted_breakdown
