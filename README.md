# Polyp Segmentation with U-Net v2 and PolypPVT

This repository contains my experiments on **colon polyp segmentation**, using:

- **PolypPVT** – Transformer-based polyp segmentation model.
- **U-Net v2** – CNN-based segmentation model trained on the BKAI-IGH NeoPolyp split.
- A shared evaluation pipeline for computing **Dice Score (DSC)**, **IoU**, and other metrics on the BKAI dataset.

The project is organized so it can be run on:

- A normal **Linux** machine  
- **Windows**  
- The Concordia **Speed cluster**

---

## 1) Repository Structure

```text
Polysegmentation/
├── Bkai_Training/              # Training / testing / eval code for BKAI U-Net v2 experiments
├── PolypSeg/                   # PolypPVT training + test code
├── unet_v2/                    # (Optional) U-Net v2 base implementation
├── documentation/              # Notes, figures, etc.
├── evalmetrics.py              # Generic evaluation helper (if used)
├── PolypPVT.pth                # PolypPVT checkpoint (Transformer model)
├── requirements.txt            # Python dependencies
└── README.md
Note: In some of my older paths the folder was named Bkai_Training_Dataset.
In this repo it is named Bkai_Training. If your clone uses a different name, adjust paths accordingly.

```
---


## 2) Datasets & External Artifacts 
Raw datasets and large checkpoints are not committed to this repository.

Please download them from Google Drive and place them in your own directories:

Author Dataset (Train + Test): https://drive.google.com/file/d/1n6w8VK4wWrwkgRX7upKFugUp1uzUaZaE/view?usp=sharing

BKAI-IGH NeoPolyp dataset (Train, Val, Test)(images + masks): https://drive.google.com/file/d/1ubfqhMpELNJn2y-SgGAfd4JX93iIkqkP/view?usp=sharing

PolypPVT pretrained weights (PolypPVT.pth) if not already present: https://drive.google.com/drive/folders/1xC5Opwu5Afz4xiK5O9v4NnQOZY0A9-2j (Also present in repository)

My Best Model PolypPVT pretrained weights (best_epoch_71.pth) : https://drive.google.com/file/d/1fDiYRmg3MrzuS2ts57Yuc2Os5Krse1yJ/view?usp=sharing

BKAI-GH  results: (https://drive.google.com/file/d/1gWqP6gF013l0Fo7Ya-eY7lRN_y6h9XzJ/view?usp=sharing)

Author Dataseets Results (Our runs): https://drive.google.com/file/d/1arPMpPTKcqDxj5w1f6mFXZ1YMGC1tHUN/view?usp=drive_link

A typical layout for BKAI on your machine:

text
Copy code
datasets/
└── BKAI_IGH_NeoPolyp/
    ├── TrainDataset/
    │   ├── images/
    │   └── masks/
    └── TestDataset/
        ├── images/
        └── masks/
You can then point the training scripts to these folders via --train_path, --test_path, and --data_root.

## 3) Installation (Common Idea)
All three environments follow the same basic idea:

Create a virtual environment
Activate it
Install dependencies from requirements.txt
Run training / test commands with the right paths.

The exact commands differ for Linux, Windows, and Speed, so each setup is described separately below.

## 4) Linux Setup
## 4.1) Clone and create environment

```bash

git clone https://github.com/VighneshK12/Polyp-Segmentation.git
cd Polyp-Segmentation

python3 -m venv .venv
source .venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt

```
## 4.2) Train PolypPVT (Transformer model)

Assume:
Project root: /path/to/Polyp-Segmentation
Train set: /path/to/datasets/TrainDataset
Test set: /path/to/datasets/TestDataset

```bash

cd /path/to/Polyp-Segmentation

export MPLBACKEND=Agg   # avoid GUI backend issues

python PolypSeg/Train.py \
  --epoch 100 \
  --batchsize 32 \
  --trainsize 352 \
  --train_path "/path/to/datasets/TrainDataset" \
  --test_path  "/path/to/datasets/TestDataset" \
  --train_save "/path/to/datasets/checkpoints_polyp_pvt"


```

You can pipe the logs to a file if you want:

```bash
python PolypSeg/Train.py ... > polyp_pvt_train.log 2>&1
```


## 4.3) Test PolypPVT

```bash
export MPLBACKEND=Agg

python PolypSeg/Test.py \
  --testsize 352 \
  --pth_path "/path/to/PolypPVT.pth" \
  --data_root "/path/to/datasets/TestDataset" \
  --save_root "/path/to/datasets/result_map/PolypPVT"
```

## 4.4) Train U-Net v2 on BKAI split
Assume the BKAI split is under Bkai_Training/TrainDataset etc:

```bash

export MPLBACKEND=Agg

python Bkai_Training/Bkai_Train.py \
  --epoch 80 \
  --batchsize 32 \
  --trainsize 352 \
  --train_path "/path/to/Polyp-Segmentation/Bkai_Training/TrainDataset" \
  --test_path  "/path/to/Polyp-Segmentation/Bkai_Training" \
  --train_save "/path/to/Polyp-Segmentation/checkpoints_bkai_split"

```
Logs:
```bash

python Bkai_Training/Bkai_Train.py ... \
  > checkpoints_bkai_split/train_bkai_split.log 2>&1
```


## 4.5) Test U-Net v2 on BKAI split
```bash

export MPLBACKEND=Agg

python Bkai_Training/BkaiTest.py \
  --testsize 352 \
  --pth_path "/path/to/Polyp-Segmentation/checkpoints_bkai_split/UNetV2/best/best_epoch_71.pth" \
  --data_root "/path/to/Polyp-Segmentation/Bkai_Training" \
  --save_root "/path/to/Polyp-Segmentation/result_map_bkai/UNetV2"

```
## 4.6) Evaluate BKAI results
```bash

export MPLBACKEND=Agg

python Bkai_Training/Bkai_eval.py \
  > Bkai_Training/eval_bkai.log 2>&1
This script reads your saved predictions + ground truth for BKAI and logs the metrics.
```

## 5) Windows Setup
Commands are similar but with Windows-style virtualenv activation and environment variables.

## 5.1) Clone and create environment (PowerShell)
```bash

git clone https://github.com/VighneshK12/Polyp-Segmentation.git
cd Polyp-Segmentation

python -m venv .venv
.\.venv\Scripts\Activate.ps1

pip install --upgrade pip
pip install -r requirements.txt

```

## 5.2) Train 

In PowerShell you can set MPLBACKEND like this:

```bash
powershell

$env:MPLBACKEND = "Agg"

python PolypSeg/Train.py `
  --epoch 100 `
  --batchsize 32 `
  --trainsize 352 `
  --train_path "D:/Datasets/Polyp/TrainDataset" `
  --test_path  "D:/Datasets/Polyp/TestDataset" `
  --train_save "D:/Datasets/Polyp/checkpoints_polyp_pvt"

```

## 5.3) Test PolypPVT
```bash
powershell


$env:MPLBACKEND = "Agg"

python PolypSeg/Test.py `
  --testsize 352 `
  --pth_path "D:/Models/PolypPVT.pth" `
  --data_root "D:/Datasets/Polyp/TestDataset" `
  --save_root "D:/Datasets/Polyp/result_map/PolypPVT"

```
## 5.4) Train & Test on BKAI

```bash

powershell

$env:MPLBACKEND = "Agg"

python Bkai_Training/Bkai_Train.py `
  --epoch 80 `
  --batchsize 32 `
  --trainsize 352 `
  --train_path "D:/Projects/Polyp-Segmentation/Bkai_Training/TrainDataset" `
  --test_path  "D:/Projects/Polyp-Segmentation/Bkai_Training" `
  --train_save "D:/Projects/Polyp-Segmentation/checkpoints_bkai_split"

python Bkai_Training/BkaiTest.py `
  --testsize 352 `
  --pth_path "D:/Projects/Polyp-Segmentation/checkpoints_bkai_split/UNetV2/best/best_epoch_71.pth" `
  --data_root "D:/Projects/Polyp-Segmentation/Bkai_Training" `
  --save_root "D:/Projects/Polyp-Segmentation/result_map_bkai/UNetV2"

python Bkai_Training/Bkai_eval.py `
  > Bkai_Training/eval_bkai.log 2>&1

```


## 6) Speed Cluster Setup (Concordia)
This section mirrors how I run the experiments on Speed.

## 6.1) Create and activate the environment
From any shell on Speed:
```bash

# Create a venv in scratch (only once)
python3 -m venv /nfs/speed-scratch/$USER/.polypseg-env

# Activate it (bash)
source /nfs/speed-scratch/$USER/.polypseg-env/bin/activate
If you are using tcsh/csh (common in ENCS), activation looks like:

csh

source /nfs/speed-scratch/$USER/.polypseg-env/bin/activate.csh

```
Then install dependencies:

```bash

pip install --upgrade pip
pip install jupyterlab ipykernel
pip install -r /nfs/speed-scratch/$USER/medical-segmentation-projects/Polysegmentation/requirements.txt
(Adjust the repo path if yours is different.)
```

## 6.2) Define paths for a run (tcsh example)

# Root of the project

```bash
set ROOT = "/nfs/speed-scratch/$USER/medical-segmentation-projects/Polysegmentation"

```

# Unique directory for this run (timestamped)

```bash

set RUN  = "$ROOT/PolySegTestFileRun_`date +%Y%m%d_%H%M%S`"


```

# Create log / result / weight directories

```bash
mkdir -p "$RUN/logs" "$RUN/results/PolypPVT" "$RUN/weights"
set LOG = "$RUN/logs/train_polyp_pvt.log"

```

## 6.3) Train PolypPVT on Speed

```bash
csh

env MPLBACKEND=Agg \
  python $ROOT/PolypSeg/Train.py \
    --epoch 100 \
    --batchsize 32 \
    --trainsize 352 \
    --train_path "$ROOT/TrainDataset" \
    --test_path  "$ROOT/TestDataset" \
    --train_save "$ROOT/checkpoints" \
  |& tee $LOG


```
## 6.4) Test PolypPVT on Speed

```bash
csh

python $ROOT/PolypSeg/Test.py \
  --testsize 352 \
  --pth_path "$ROOT/PolypSeg/pvt_pth/PolypPVT.pth" \
  --data_root "$ROOT/TestDataset" \
  --save_root "$ROOT/result_map/PolypPVT"


```

## 6.5) Train U-Net v2 on BKAI split (Speed)

```bash
csh

env MPLBACKEND=Agg \
  python $ROOT/Bkai_Training/Bkai_Train.py \
    --epoch 80 \
    --batchsize 32 \
    --trainsize 352 \
    --train_path "$ROOT/Bkai_Training/TrainDataset" \
    --test_path  "$ROOT/Bkai_Training" \
    --train_save "$ROOT/checkpoints_bkai_split" \
  |& tee "$ROOT/checkpoints_bkai_split/train_bkai_split.log"


```

## 6.6) Test U-Net v2 on BKAI split (Speed)

```bash
csh
Copy code
env MPLBACKEND=Agg \
  python $ROOT/Bkai_Training/BkaiTest.py \
    --testsize 352 \
    --pth_path "$ROOT/checkpoints_bkai_split/UNetV2/best/best_epoch_71.pth" \
    --data_root "$ROOT/Bkai_Training" \
    --save_root "$ROOT/result_map_bkai/UNetV2"


```

## 6.7) Evaluate BKAI results (Speed)

```bash
csh
env MPLBACKEND=Agg \
  python $ROOT/Bkai_Training/Bkai_eval.py \
  |& tee "$ROOT/Bkai_Training/eval_bkai.log"


```

## 8) Citation
All Credits go to:
```bash

@article{peng2023u,
  title   = {U-Net v2: Rethinking the Skip Connections of U-Net for Medical Image Segmentation},
  author  = {Peng, Yaopeng and Sonka, Milan and Chen, Danny Z},
  journal = {arXiv preprint arXiv:2311.17791},
  year    = {2023}
}


```
