import numpy as np
from sklearn.metrics import average_precision_score, precision_score
import torch

# torch.manual_seed(0)


n_frames = 5
n_classes = 2


def cal_map(gt, pred):
    ap = torch.zeros(pred.size(1))
    rg = torch.arange(1, pred.size(0) + 1).float()
    p = torch.zeros(pred.size(1))
    # compute average precision for each class
    for k in range(pred.size(1)):
        # sort scores
        scores = pred[:, k]
        targets = gt[:, k]
        _, sortind = torch.sort(scores, 0, True)
        truth = targets[sortind]

        tp = truth.float().cumsum(0)

        # compute precision curve
        precision = tp.div(rg)
        p[k] = precision
        # compute average precision
        ap[k] = precision[truth.bool()].sum() / max(truth.sum(), 1)
    return p


def cal_map_sklearn(gt, pred):
    threshold = 1.
    idx = 0
    p = torch.zeros(pred.size(1))
    while threshold > 0:
        y_pred = (pred > threshold).byte()
        y_true = gt.max(1)

        p[idx] = precision_score(y_true, y_pred)
    return p


pred = torch.rand(n_frames, n_classes)
gt = torch.zeros(n_frames, n_classes)

for i in range(n_frames):
    j = torch.randint(0, n_classes, (1,))
    gt[i, j] = 1

p1 = cal_map(gt, pred)
p2 = cal_map_sklearn(gt, pred)

print(p1)
print(p2)
