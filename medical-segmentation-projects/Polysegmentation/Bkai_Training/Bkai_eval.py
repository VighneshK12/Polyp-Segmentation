import os
import numpy as np
import cv2
from pathlib import Path
from datetime import datetime

def binarize(x, thr=0.5):
    """
    Convert mask image to binary.
    - Handles both [0, 255] uint8 and [0, 1] float images.
    - thr is in [0,1].
    """
    x = x.astype(np.float32)
    if x.max() > 1.5:      # image is in [0, 255]
        x = x / 255.0      # normalize to [0, 1]
    return (x >= thr).astype(np.uint8)

def dice_iou(gt, pred):
    gt   = gt.astype(bool)
    pred = pred.astype(bool)

    inter = np.logical_and(gt, pred).sum()
    union = np.logical_or(gt, pred).sum()
    gt_sum   = gt.sum() + 1e-8
    pred_sum = pred.sum() + 1e-8

    dice = (2 * inter + 1e-8) / (gt_sum + pred_sum)
    iou  = (inter + 1e-8) / (union + 1e-8)
    return float(dice), float(iou)

if __name__ == "__main__":
    # ---- paths ----
    pred_root = Path("/nfs/speed-scratch/k_vighne/Polysegtr/U-Net_v2/result_map_bkai/UNetV2/TestDataset")
    gt_root   = Path("/nfs/speed-scratch/k_vighne/Polysegtr/U-Net_v2/Bkai_Training_Dataset/TestDataset/masks")

    assert pred_root.is_dir(), f"Missing pred folder: {pred_root}"
    assert gt_root.is_dir(),   f"Missing GT folder:   {gt_root}"

    pred_files = sorted([
        f for f in pred_root.iterdir()
        if f.suffix.lower() in [".png", ".jpg", ".jpeg"]
    ])

    dices, ious = [], []

    print(f"== BKAI evaluation @ {datetime.now()} ==")
    print("Pred:", pred_root)
    print("GT  :", gt_root)
    print("#Images:", len(pred_files))

    for pf in pred_files:
        gf = gt_root / pf.name
        if not gf.exists():
            print(f"[WARN] No GT for {pf.name}, skipping.")
            continue

        # read as grayscale (0–255)
        pred = cv2.imread(str(pf), cv2.IMREAD_GRAYSCALE)
        gt   = cv2.imread(str(gf), cv2.IMREAD_GRAYSCALE)

        if pred is None or gt is None:
            print(f"[WARN] Failed to read {pf.name}, skipping.")
            continue

        # if shapes differ, resize GT to prediction size (nearest-neighbor)
        if pred.shape != gt.shape:
            gt = cv2.resize(gt, (pred.shape[1], pred.shape[0]),
                            interpolation=cv2.INTER_NEAREST)

        # predictions are white blobs -> use higher threshold
        pred_bin = binarize(pred, thr=0.5)
        # GT masks are red in RGB -> ~0.2 in gray -> lower threshold
        gt_bin   = binarize(gt,   thr=0.1)

        d, i = dice_iou(gt_bin, pred_bin)
        dices.append(d)
        ious.append(i)

    if dices:
        print(f"\nMean Dice: {np.mean(dices):.4f}")
        print(f"Mean IoU : {np.mean(ious):.4f}")
    else:
        print("No overlapping predictions/GT to evaluate.")
