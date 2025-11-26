# Polyp Segmentation with U-Net v2 and PolypPVT

This repository contains my experiments on **colon polyp segmentation**, using:

- **PolypPVT** – Transformer-based polyp segmentation model.
- **U-Net v2** – CNN-based segmentation model trained on the BKAI-IGH NeoPolyp split.
- A shared evaluation pipeline for computing **Dice Score (DSC)**, **IoU**, and **other metrics** on the BKAI dataset.

The project is organized so it can be run on:
- A normal **Linux** machine
- **Windows**
- The Concordia **Speed cluster**

---

## 1. Repository Structure

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

2. Datasets & External Artifacts
Raw datasets and large checkpoints are not committed to this repository.

Please download them from Google Drive and place them in your own directories:

🔗 To fill in with your own links

BKAI-IGH NeoPolyp dataset (images + masks): [Google Drive link]

Train/test split folders used in Bkai_Training/: [Google Drive link]

PolypPVT pretrained weights (PolypPVT.pth) if not already present: [Google Drive link]

Saved result maps / predictions (optional): [Google Drive link]

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

3. Installation (Common Idea)
All three environments follow the same basic idea:

Create a virtual environment

Activate it

Install dependencies from requirements.txt

Run training / test commands with the right paths.

The exact commands differ slightly between Linux, Windows, and Speed, so each setup is described separately below.

4. Linux Setup
4.1. Clone and environment
bash
Copy code
git clone https://github.com/VighneshK12/Polyp-Segmentation.git
cd Polyp-Segmentation

python3 -m venv .venv
source .venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt
If you want Jupyter:

bash
Copy code
pip install jupyterlab ipykernel
python -m ipykernel install --user --name polypseg --display-name "polypseg"
4.2. Train PolypPVT (Transformer model)
Assume:

Project root: /path/to/Polyp-Segmentation

Train set: /path/to/datasets/TrainDataset

Test set: /path/to/datasets/TestDataset

Run:

bash
Copy code
cd /path/to/Polyp-Segmentation

export MPLBACKEND=Agg   # avoid GUI backend issues

python PolypSeg/Train.py \
  --epoch 100 \
  --batchsize 32 \
  --trainsize 352 \
  --train_path "/path/to/datasets/TrainDataset" \
  --test_path  "/path/to/datasets/TestDataset" \
  --train_save "/path/to/datasets/checkpoints_polyp_pvt"
You can pipe the logs to a file if you want:

bash
Copy code
python PolypSeg/Train.py ... \
  > polyp_pvt_train.log 2>&1
4.3. Test PolypPVT
bash
Copy code
export MPLBACKEND=Agg

python PolypSeg/Test.py \
  --testsize 352 \
  --pth_path "/path/to/PolypPVT.pth" \
  --data_root "/path/to/datasets/TestDataset" \
  --save_root "/path/to/datasets/result_map/PolypPVT"
4.4. Train U-Net v2 on BKAI split
Assume the BKAI split is under Bkai_Training/TrainDataset etc:

bash
Copy code
export MPLBACKEND=Agg

python Bkai_Training/Bkai_Train.py \
  --epoch 80 \
  --batchsize 32 \
  --trainsize 352 \
  --train_path "/path/to/Polyp-Segmentation/Bkai_Training/TrainDataset" \
  --test_path  "/path/to/Polyp-Segmentation/Bkai_Training" \
  --train_save "/path/to/Polyp-Segmentation/checkpoints_bkai_split"
Logs:

bash
Copy code
python Bkai_Training/Bkai_Train.py ... \
  > checkpoints_bkai_split/train_bkai_split.log 2>&1
4.5. Test U-Net v2 on BKAI split
bash
Copy code
export MPLBACKEND=Agg

python Bkai_Training/BkaiTest.py \
  --testsize 352 \
  --pth_path "/path/to/Polyp-Segmentation/checkpoints_bkai_split/UNetV2/best/best_epoch_71.pth" \
  --data_root "/path/to/Polyp-Segmentation/Bkai_Training" \
  --save_root "/path/to/Polyp-Segmentation/result_map_bkai/UNetV2"
4.6. Evaluate BKAI results
bash
Copy code
export MPLBACKEND=Agg

python Bkai_Training/Bkai_eval.py \
  > Bkai_Training/eval_bkai.log 2>&1
This script reads your saved predictions + ground truth for BKAI and logs the metrics.

5. Windows Setup
Commands are similar but with Windows-style virtualenv activation and environment variables.

5.1. Clone and environment (PowerShell)
powershell
Copy code
git clone https://github.com/VighneshK12/Polyp-Segmentation.git
cd Polyp-Segmentation

python -m venv .venv
.\.venv\Scripts\Activate.ps1

pip install --upgrade pip
pip install -r requirements.txt
5.2. Train PolypPVT
In PowerShell you can set MPLBACKEND like this:

powershell
Copy code
$env:MPLBACKEND = "Agg"

python PolypSeg/Train.py `
  --epoch 100 `
  --batchsize 32 `
  --trainsize 352 `
  --train_path "D:/Datasets/Polyp/TrainDataset" `
  --test_path  "D:/Datasets/Polyp/TestDataset" `
  --train_save "D:/Datasets/Polyp/checkpoints_polyp_pvt"
5.3. Test PolypPVT
powershell
Copy code
$env:MPLBACKEND = "Agg"

python PolypSeg/Test.py `
  --testsize 352 `
  --pth_path "D:/Models/PolypPVT.pth" `
  --data_root "D:/Datasets/Polyp/TestDataset" `
  --save_root "D:/Datasets/Polyp/result_map/PolypPVT"
5.4. Train & Test on BKAI
powershell
Copy code
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
6. Speed Cluster Setup (Concordia)
This section mirrors exactly how I run the experiments on Speed.

6.1. Create and activate the environment
From any shell on Speed:

bash
Copy code
# Create a venv in scratch (only once)
python3 -m venv /nfs/speed-scratch/$USER/.polypseg-env

# Activate it (bash)
source /nfs/speed-scratch/$USER/.polypseg-env/bin/activate
If you are using tcsh/csh (which is common in ENCS), activation looks like:

csh
Copy code
source /nfs/speed-scratch/$USER/.polypseg-env/bin/activate.csh
Then install dependencies:

bash
Copy code
pip install --upgrade pip
pip install jupyterlab ipykernel
pip install -r /nfs/speed-scratch/$USER/medical-segmentation-projects/Polysegmentation/requirements.txt
(Adjust the repo path if yours is different.)

6.2. Define paths for a run
Example using tcsh syntax (what I actually used):

c
Copy code
# Root of the project
set ROOT = "/nfs/speed-scratch/$USER/medical-segmentation-projects/Polysegmentation"

# Unique directory for this run (timestamped)
set RUN  = "$ROOT/PolySegTestFileRun_`date +%Y%m%d_%H%M%S`"

# Create log / result / weight directories
mkdir -p "$RUN/logs" "$RUN/results/PolypPVT" "$RUN/weights"
set LOG = "$RUN/logs/train_polyp_pvt.log"
6.3. Train PolypPVT on Speed
c
Copy code
env MPLBACKEND=Agg \
  python $ROOT/PolypSeg/Train.py \
    --epoch 100 \
    --batchsize 32 \
    --trainsize 352 \
    --train_path "$ROOT/TrainDataset" \
    --test_path  "$ROOT/TestDataset" \
    --train_save "$ROOT/checkpoints" \
  |& tee $LOG
6.4. Test PolypPVT on Speed
cs
Copy code
python $ROOT/PolypSeg/Test.py \
  --testsize 352 \
  --pth_path "$ROOT/PolypSeg/pvt_pth/PolypPVT.pth" \
  --data_root "$ROOT/TestDataset" \
  --save_root "$ROOT/result_map/PolypPVT"
6.5. Train U-Net v2 on BKAI split (Speed)
csh
Copy code
env MPLBACKEND=Agg \
  python $ROOT/Bkai_Training/Bkai_Train.py \
    --epoch 80 \
    --batchsize 32 \
    --trainsize 352 \
    --train_path "$ROOT/Bkai_Training/TrainDataset" \
    --test_path  "$ROOT/Bkai_Training" \
    --train_save "$ROOT/checkpoints_bkai_split" \
  |& tee "$ROOT/checkpoints_bkai_split/train_bkai_split.log"
6.6. Test U-Net v2 on BKAI split (Speed)
c
Copy code
env MPLBACKEND=Agg \
  python $ROOT/Bkai_Training/BkaiTest.py \
    --testsize 352 \
    --pth_path "$ROOT/checkpoints_bkai_split/UNetV2/best/best_epoch_71.pth" \
    --data_root "$ROOT/Bkai_Training" \
    --save_root "$ROOT/result_map_bkai/UNetV2"
6.7. Evaluate BKAI results (Speed)
csh
Copy code
env MPLBACKEND=Agg \
  python $ROOT/Bkai_Training/Bkai_eval.py \
  |& tee "$ROOT/Bkai_Training/eval_bkai.log"
7. Results (to fill in)
Summarize your final performance here once you’re done:

Model	Dataset	Mean Dice	Mean IoU	Notes
PolypPVT	BKAI-IGH NeoPolyp	XX.XX	XX.XX	Trainsize=352, batch=32
U-Net v2	BKAI-IGH NeoPolyp	XX.XX	XX.XX	Custom BKAI split (600/200/200 or similar)


9. Citation
@article{peng2023u,
  title={U-Net v2: Rethinking the Skip Connections of U-Net for Medical Image Segmentation},
  author={Peng, Yaopeng and Sonka, Milan and Chen, Danny Z},
  journal={arXiv preprint arXiv:2311.17791},
  year={2023}
}


=

