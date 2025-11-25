import os
import numpy as np
import cv2
from datetime import datetime

def dice_iou(pred, gt):
    pred = (pred > 128).astype(np.uint8)  # threshold at 0.5
    gt   = (gt > 128).astype(np.uint8)

    inter = np.logical_and(pred, gt).sum()
    union = np.logical_or(pred, gt).sum()
    dice = 2 * inter / (pred.sum() + gt.sum() + 1e-8)
    iou  = inter / (union + 1e-8)
    return dice, iou

def eval_dataset(pred_root, gt_root):
    dices, ious = [], []
    for name in os.listdir(pred_root):
        if not name.endswith('.png'):
            continue

        pred_path = os.path.join(pred_root, name)
        gt_path   = os.path.join(gt_root, name)

        if not os.path.exists(gt_path):
            # skip if no matching GT file
            print(f"[WARN] No GT for {name}, skipping")
            continue

        pred = cv2.imread(pred_path, cv2.IMREAD_GRAYSCALE)
        gt   = cv2.imread(gt_path, cv2.IMREAD_GRAYSCALE)

        d, i = dice_iou(pred, gt)
        dices.append(d)
        ious.append(i)

    if len(dices) == 0:
        print("  No valid image pairs found!")
        return None, None, 0

    mean_dice = float(np.mean(dices))
    mean_iou  = float(np.mean(ious))
    n_images  = len(dices)

    print(f"  Mean Dice: {mean_dice:.4f}")
    print(f"  Mean IoU : {mean_iou:.4f}")
    print(f"  #Images  : {n_images}")

    return mean_dice, mean_iou, n_images

if __name__ == "__main__":
    base = "/nfs/speed-scratch/k_vighne/Polysegtr/U-Net_v2"
    pred_base = f"{base}/result_map/PolypPVT"
    gt_base   = f"{base}/TestDataset"

    # where to save logs
    log_dir = os.path.join(base, "eval_logs")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "eval_PolypPVT.log")

    datasets = ["CVC-300", "CVC-ClinicDB", "Kvasir", "CVC-ColonDB", "ETIS-LaribPolypDB"]

    results = []
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print(f"=== Evaluation run @ {timestamp} ===")

    for ds in datasets:
        pred_root = os.path.join(pred_base, ds)
        gt_root   = os.path.join(gt_base, ds, "masks")

        print(f"\nDataset: {ds}")
        print(f"  Pred: {pred_root}")
        print(f"  GT  : {gt_root}")

        if not (os.path.isdir(pred_root) and os.path.isdir(gt_root)):
            print("  [SKIP] Missing pred_root or gt_root")
            results.append((ds, None, None, 0, "MISSING_PATH"))
            continue

        mean_dice, mean_iou, n_images = eval_dataset(pred_root, gt_root)
        status = "OK" if n_images > 0 else "NO_VALID_PAIRS"
        results.append((ds, mean_dice, mean_iou, n_images, status))

    # ---- write log file ----
    with open(log_file, "a") as f:
        f.write(f"=== Evaluation run @ {timestamp} ===\n")
        for ds, md, mi, n, status in results:
            if status != "OK":
                f.write(f"{ds}: status={status}, n={n}\n")
            else:
                f.write(
                    f"{ds}: status={status}, "
                    f"mean_dice={md:.4f}, mean_iou={mi:.4f}, n={n}\n"
                )
        f.write("\n")

    print(f"\nSaved log to: {log_file}")
