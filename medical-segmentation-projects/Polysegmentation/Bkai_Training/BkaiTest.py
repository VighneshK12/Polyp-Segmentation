import os
import argparse
import numpy as np
import torch
import torch.nn.functional as F
import cv2

from unet_v2.UNet_v2 import UNetV2
from utils.dataloader import test_dataset


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--testsize', type=int, default=352, help='testing size')
    parser.add_argument('--pth_path', type=str,
                        required=True,
                        help='path to your trained UNetV2 checkpoint (.pth)')
    parser.add_argument('--data_root', type=str,
                        required=True,
                        help='root containing TestDataset (with images/ and masks/)')
    parser.add_argument('--save_root', type=str,
                        required=True,
                        help='folder to save predictions')
    args = parser.parse_args()

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print('Device:', device)

    # --- build model (same as in training) ---
    # We still pass the PVT backbone path; it will be overridden by your checkpoint.
    model = UNetV2(
        pretrained_path=f"{os.getcwd()}/PolypSeg/pvt_pth/pvt_v2_b2.pth",
        deep_supervision=False
    ).to(device)

    # --- load YOUR trained weights ---
    print(f"Loading checkpoint from: {args.pth_path}")
    ckpt = torch.load(args.pth_path, map_location=device)
    # If the checkpoint was saved with DataParallel, strip 'module.' prefix
    if any(k.startswith('module.') for k in ckpt.keys()):
        ckpt = {k.replace('module.', '', 1): v for k, v in ckpt.items()}
    model.load_state_dict(ckpt, strict=True)
    model.eval()

    # For BKAI we just have one dataset: 'TestDataset'
    datasets = ['TestDataset']

    with torch.no_grad():
        for ds in datasets:
            data_path = os.path.join(args.data_root, ds)
            image_root = os.path.join(data_path, 'images')
            gt_root    = os.path.join(data_path, 'masks')
            save_path  = os.path.join(args.save_root, ds)
            os.makedirs(save_path, exist_ok=True)

            if not os.path.isdir(image_root) or not os.path.isdir(gt_root):
                raise FileNotFoundError(f"Missing {image_root} or {gt_root}")

            num_imgs = len(os.listdir(gt_root))
            print(f"[{ds}] Found {num_imgs} GT masks")

            loader = test_dataset(image_root, gt_root, args.testsize)

            for _ in range(num_imgs):
                image, gt, name = loader.load_data()   # image: tensor; gt: np array
                gt = np.asarray(gt, np.float32)
                gt /= (gt.max() + 1e-8)

                image = image.to(device)

                # UNetV2 returns a single prediction tensor
                res = model(image)

                res = F.interpolate(res, size=gt.shape, mode='bilinear', align_corners=False)
                res = torch.sigmoid(res).cpu().numpy().squeeze()
                res = (res - res.min()) / (res.max() - res.min() + 1e-8)  # normalize to [0,1]
                out = (res * 255).astype(np.uint8)

                cv2.imwrite(os.path.join(save_path, name), out)

            print(ds, 'Finish! Saved to:', save_path)

if __name__ == '__main__':
    main()
