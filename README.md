# smartcontainer-risk-dashboard
# 🚢 SmartContainer Risk Intelligence System
https://smartcontainer-risk-dashboard-4rkyt4xmcbxj3h39zfsudq.streamlit.app/
> **AI-Powered Risk Detection for Global Port Security**  
> Using machine learning and anomaly detection to prioritize container inspections.

*Kavya Mehta – 24BEI034 | Shreyan Mehta – 24BEI023*

---

## 📌 Table of Contents

- [Problem Statement](#-problem-statement)
- [Solution Overview](#-solution-overview)
- [System Architecture](#-system-architecture)
- [Features Used](#-features-used)
- [ML Models & Techniques](#-ml-models--techniques)
- [Feature Engineering](#-feature-engineering)
- [Risk Scoring Logic](#-risk-scoring-logic)
- [Explainability (XAI)](#-explainability-xai)
- [LLM-Based Natural Language Explanations](#-llm-based-natural-language-explanations)
- [Model Evaluation](#-model-evaluation)
- [Dashboard](#-dashboard)
- [Installation & Usage](#-installation--usage)
- [Project Structure](#-project-structure)
- [Dependencies](#-dependencies)

---

## 🚨 Problem Statement

Ports worldwide process extremely large volumes of containers every single day. Due to limited manpower and time, authorities cannot physically inspect every container. Current inspection processes rely on **manual rules or random sampling**, which leads to:

- ❌ Unnecessary inspections of low-risk containers
- ❌ Delays in cargo clearance
- ❌ High operational costs
- ❌ Risk of dangerous or fraudulent shipments passing unnoticed

**Ports need a system that intelligently identifies which containers actually require inspection.**

---

## ✅ Solution Overview

The **SmartContainer Risk Intelligence System** analyzes container shipment data and automatically identifies high-risk containers using machine learning. The system:

1. **Detects anomalies** in shipment data using Isolation Forest
2. **Calculates a risk score** for every container using XGBoost
3. **Provides human-readable explanations** for flagged containers using SHAP, LIME, and an LLM
4. **Displays results** through an interactive Streamlit dashboard

The goal is to transform container inspection from *random checking* to **intelligent, risk-based inspection** — helping port authorities prioritize their work and avoid wasting time on low-risk shipments.

---

## 🏗️ System Architecture

```
Raw Shipment Data
        │
        ▼
┌─────────────────────┐
│   Data Processing   │  ← Cleaning, encoding, datetime parsing
└─────────────────────┘
        │
        ▼
┌─────────────────────┐
│  Feature Engineering│  ← Weight discrepancy, value density,
│                     │    route rarity, importer behaviour, etc.
└─────────────────────┘
        │
        ├─────────────────────────────┐
        ▼                             ▼
┌──────────────────┐        ┌──────────────────────┐
│  Anomaly Detection│       │   Risk Prediction     │
│  (Isolation Forest)│      │   (XGBoost Regressor) │
└──────────────────┘        └──────────────────────┘
        │                             │
        └──────────┬──────────────────┘
                   ▼
        ┌─────────────────────┐
        │  Final Risk Score   │  ← 0.55 × ML Score + 0.45 × Trade Intelligence Score
        └─────────────────────┘
                   │
                   ▼
        ┌─────────────────────┐
        │  Explainability     │  ← SHAP + LIME + LLM (OpenRouter)
        └─────────────────────┘
                   │
                   ▼
        ┌─────────────────────┐
        │  Streamlit Dashboard│  ← Visualization & Search
        └─────────────────────┘
```

---

## 📊 Features Used

| Category | Features |
|---|---|
| **Weight** | `Measured_Weight`, `Declared_Weight` |
| **Value** | `Declared_Value` |
| **Identity** | `Importer_ID`, `Exporter_ID` |
| **Trade** | `Trade_Regime`, `Origin_Country`, `Destination_Country`, `Destination_Port` |
| **Logistics** | `Shipping_Line`, `HS_Code`, `Dwell_Time_Hours` |
| **Time** | `Declaration_Date`, `Declaration_Time` |

---

## 🤖 ML Models & Techniques

### 1. XGBoost Regressor (Risk Scoring)
```python
model = XGBRegressor(
    n_estimators=120,
    max_depth=6,
    learning_rate=0.08,
    random_state=42
)
```
Generates a continuous risk score (0–1) for each container based on shipment attributes.

### 2. Isolation Forest (Anomaly Detection)
```python
iso = IsolationForest(
    contamination=0.05,
    random_state=42
)
```
Identifies containers that behave **abnormally** compared to typical shipment patterns. Outputs `Anomaly_Flag = 1` for outliers.

### 3. SMOTETomek (Class Imbalance Handling)
```python
smt = SMOTETomek(random_state=42)
X_res, y_res = smt.fit_resample(X, y_bin)
```
Combines oversampling of the minority class (Critical shipments) with cleaning of borderline examples to improve model performance on imbalanced data.

---

## 🔧 Feature Engineering

The `feature_engineering()` function enriches raw shipment data with the following derived features:

| Feature | Description |
|---|---|
| `Weight_Diff` | Difference between measured and declared weight |
| `Weight_Ratio` | Ratio of measured to declared weight |
| `Weight_Percent_Diff` | Percentage discrepancy in weight |
| `Value_per_Weight` | Declared value per unit of weight (value density) |
| `Declaration_Hour` | Hour of the day the shipment was declared |
| `Day_of_Week` | Day of the week (0=Monday, 6=Sunday) |
| `Month` | Month of the year |
| `Is_Night_Shipment` | 1 if declared between 8 PM and 5 AM, else 0 |
| `Route` | Concatenation of origin country and destination port |
| `Route_Frequency` | How often this particular route appears in the dataset |
| `Route_Rarity` | Inverse of route frequency — rare routes are higher risk |
| `Importer_Shipment_Count` | Total historical shipments by this importer |
| `Importer_Avg_Value` | Average declared value for this importer |
| `Importer_Value_Deviation` | How much this shipment deviates from the importer's average |
| `Exporter_Shipment_Count` | Total historical shipments by this exporter |
| `Exporter_Avg_Value` | Average declared value for this exporter |
| `Dwell_Risk` | Z-score of dwell time — unusually long dwell is a red flag |

---

## 🧮 Risk Scoring Logic

### Trade Intelligence Score

A rule-based composite score combining four normalized risk signals:

```python
weight_risk     = normalize(df['Weight_Percent_Diff'].clip(0, 100))
value_risk      = normalize(HS_Code-grouped value-per-weight deviation from median)
route_risk      = normalize(df['Route_Rarity'])
behaviour_risk  = normalize(df['Importer_Value_Deviation'])

Trade_Intelligence_Score = (
    weight_risk    * 0.30 +
    value_risk     * 0.30 +
    route_risk     * 0.20 +
    behaviour_risk * 0.20
)
```

### Final Risk Score

```python
Final_Risk_Score = 0.55 × ML_Risk_Score + 0.45 × Trade_Intelligence_Score
```

### Risk Classification

```python
def classify_risk(row):
    if row['Final_Risk_Score'] > 0.60 or (
        row['Anomaly_Flag'] == 1 and row['Final_Risk_Score'] > 0.45
    ):
        return "Critical Risk"
    elif row['Final_Risk_Score'] > 0.25 or row['Anomaly_Flag'] == 1:
        return "Low Risk"
    else:
        return "Minimal Risk"
```

| Risk Level | Condition |
|---|---|
| 🔴 **Critical Risk** | Score > 0.60, or anomaly detected AND score > 0.45 |
| 🟡 **Low Risk** | Score > 0.25, or anomaly detected |
| 🟢 **Minimal Risk** | Score ≤ 0.25 and no anomaly |

---

## 🔍 Explainability (XAI)

The system uses two complementary explainability frameworks so that every flagged shipment can be justified to a human investigator.

### SHAP (SHapley Additive exPlanations)
```python
explainer = shap.Explainer(model)
shap_values = explainer(X)
shap.summary_plot(shap_values, X, plot_type="bar")
```
SHAP values show the **global importance** of each feature across all predictions, as well as the **per-shipment contribution** of each feature to the final risk score.

### LIME (Local Interpretable Model-agnostic Explanations)
```python
lime_exp = explainer_lime.explain_instance(
    row.values, model.predict, num_features=5
)
```
LIME generates a local linear approximation of the model's decision for each individual shipment, highlighting the specific rules that triggered the flag.

### Quick XAI Summary Function
```python
def generate_xai_explanation(index):
    # Returns top 3 features and whether they increased or lowered risk
    # Example: "Weight_Diff increased risk, Route_Rarity increased risk, Dwell_Time_Hours lowered risk"
```

---

## 💬 LLM-Based Natural Language Explanations

For containers flagged as **RISKY**, the system calls a Large Language Model via the [OpenRouter API](https://openrouter.ai/) to generate a plain-English, 2–3 sentence explanation readable by non-technical port authorities.

### How It Works

```python
prompt = f"""You are a customs risk analyst. A machine learning model flagged a shipment.
Write exactly 2-3 sentences explaining WHY, in plain English. No jargon.

Shipment details: {shipment_text}
Model verdict: {prediction} (confidence: {confidence:.0%})
Key risk drivers (SHAP): {shap_text}
Key rules triggered (LIME): {lime_text}
"""
```

### Model Fallback Strategy
The system automatically tries all available **free models** on OpenRouter in sequence. If a model returns an empty response or hits a rate limit (HTTP 429), it moves to the next one — ensuring maximum availability without any paid API cost.

```python
for model in free_models:
    try:
        response = client.chat.completions.create(...)
        if content:
            return content.strip()
    except:
        continue  # try next model
```

### Batch Processing
When running across an entire test set, LLM calls are made **only for RISKY containers**. Safe containers receive a fixed message: *"Shipment parameters align with standard trade profiles."* A 60-second pause is inserted every 100 LLM calls to avoid rate limiting.

---

## 📈 Model Evaluation

The model is evaluated using the following metrics on both a held-out test set and real-time data:

| Metric | Description |
|---|---|
| **Precision** | Of all containers flagged as risky, how many actually were? |
| **Recall** | Of all truly risky containers, how many did the system catch? |
| **F1 Score** | Harmonic mean of precision and recall |
| **AUPRC** | Area Under the Precision-Recall Curve — key metric for imbalanced datasets |
| **Confusion Matrix** | Breakdown of TP, TN, FP, FN |

```python
# Evaluation on test set
precision = precision_score(y_test, y_pred)
recall    = recall_score(y_test, y_pred)
f1        = f1_score(y_test, y_pred)
auprc     = auc(recall_curve, precision_curve)
```

The system is evaluated twice — once on the **training/test split** and again on a separate **real-time dataset** (`Real-Time Data.csv`) to validate generalization.

---

## 🖥️ Dashboard
https://smartcontainer-risk-dashboard-4rkyt4xmcbxj3h39zfsudq.streamlit.app/
The Streamlit dashboard provides port authorities with a real-time operational interface including:

- 📊 **Overview metrics** — total containers processed, risk distribution counts
- 🗺️ **Risk by origin country** — geographic heatmap of risk concentration
- 🚢 **Risk by shipping line** — carrier-level risk profiling
- 🏢 **Risk by destination port** — port-level risk analysis
- ⚠️ **Anomaly detection table** — list of flagged outlier containers
- 🔝 **Top risky containers** — ranked by Final Risk Score
- 🔍 **Container search** — look up any shipment by ID

---

## 🚀 Installation & Usage

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/smartcontainer-risk-intelligence.git
cd smartcontainer-risk-intelligence
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Prepare Your Data
Place your shipment CSV file in the project root. The file must include columns for:
`Declaration_Date`, `Declaration_Time`, `Declared_Weight`, `Measured_Weight`, `Declared_Value`, `Origin_Country`, `Destination_Port`, `Destination_Country`, `Shipping_Line`, `Trade_Regime`, `Importer_ID`, `Exporter_ID`, `HS_Code`, `Dwell_Time_Hours`, `Clearance_Status`

### 4. Run the Notebook
Open and run `SmartContainer_Risk_Intelligence.ipynb` sequentially. The notebook will:
- Engineer features
- Train the XGBoost model
- Generate risk scores
- Produce SHAP/LIME explanations
- Call the LLM for natural language explanations

### 5. Launch the Dashboard
```bash
streamlit run dashboard.py
```

---

## 📁 Project Structure

```
smartcontainer-risk-intelligence/
│
├── SmartContainer_Risk_Intelligence.ipynb   # Main notebook
├── dashboard.py                             # Streamlit dashboard
├── Real-Time Data.csv                       # Real-time evaluation dataset
├── requirements.txt
└── README.md
```

---

## 📦 Dependencies

```
pandas
numpy
scikit-learn
xgboost
imbalanced-learn          # SMOTETomek
shap
lime
openai                    # OpenRouter-compatible client
requests
streamlit
matplotlib
```

Install all at once:
```bash
pip install pandas numpy scikit-learn xgboost imbalanced-learn shap lime openai requests streamlit matplotlib
```

---

## ⚠️ Notes

- The OpenRouter API key in the source code is for demonstration purposes. Replace it with your own key from [openrouter.ai](https://openrouter.ai/) before deploying.
- The LLM explanation step requires an active internet connection and a valid OpenRouter API key.
- `XGBRegressor` is used (not `XGBClassifier`) — risk scores are continuous values in [0, 1], thresholded at 0.5 for binary classification.

---

*Built for smarter, faster, and fairer global trade security.*
