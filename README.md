### Network Security Project with Phishing Data 

A Machine Learning project to detect network intrusions using a modular pipeline. The system includes data ingestion, preprocessing, model training, evaluation, experiment tracking via MLflow, storage on AWS S3, and deployment using FastAPI.

---

## 🚀 Tech Stack
- **Python**, **Scikit-Learn**, **Pandas**
- **MLflow** (tracking)
- **DagsHub** (remote MLflow storage)
- **AWS S3** (artifact storage)
- **FastAPI + Uvicorn** (deployment)

---

## 📁 Project Structure

```bash
Network-Security-ML-Pipeline/
│
├── src/
│   ├── components/
│   │   ├── data_ingestion.py
│   │   ├── data_transformation.py
│   │   └── model_trainer.py
│   │
│   ├── pipeline/
│   │   ├── training_pipeline.py
│   │   └── prediction_pipeline.py
│   │
│   ├── utils/
│   │   └── common.py
│   │
│   ├── constant/
│   └── entity/
│
├── artifacts/                 # Generated automatically
├── app/
│   └── main.py                # FastAPI app
│
├── requirements.txt
└── README.md

```

## 🧩 Create & Activate Virtual Environment
```bash
conda create -n networkml python=3.10 -y
conda activate networkml
pip install -r requirements.txt
```


## 🧪 Setup MLflow Tracking (DagsHub)
```bash
export MLFLOW_TRACKING_URI=https://dagshub.com/<your-username>/<your-repo>.mlflow
export MLFLOW_TRACKING_USERNAME=<your-username>
export MLFLOW_TRACKING_PASSWORD=<your-token>
```

## ☁️ Configure AWS S3 Bucket
```bash
aws configure
# Enter AWS Access Key, Secret Key and Region (ap-south-1 recommended)
```

## 📦 Train the Model
```bash
python main.py
```
or if using FastAPI endpoint:
```bash
uvicorn app.main:app --reload
```
Visit:
```arduino
http://127.0.0.1:8000/train
```

## 🔍 Run Prediction API
```bash
http://127.0.0.1:8000/predict
```

## 📊 View MLflow Dashboard
```bash
mlflow ui
```
or DagsHub automatically stores runs at:
```bash
https://dagshub.com/<your-username>/<your-repo>/experiments
```
