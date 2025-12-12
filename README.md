# TruthCheck: AI-Powered Fact Verification System

![Status](https://img.shields.io/badge/Status-Active-success)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)

A state-of-the-art **Automated Fact-Checking System** that uses a multi-stage neural pipeline to verify text claims in real-time. It combines **Web Scraping**, **Semantic Search**, and **Natural Language Inference (NLI)** to determine the truthfulness of statements with high precision.
## Application link :" https://huggingface.co/spaces/Danielchris145/TruthCheck-AI "
---

## 🌟 Key Features

### 🧠 Advanced AI Core
-   **Multi-Model Consensus**: Aggregates judgments from `RoBERTa-large-MNLI` and `DeBERTa-v3-large` for robust accuracy.
-   **Semantic Filtering**: Uses `Sentence-Transformers` to ensure only relevant evidence is analyzed.
-   **Credibility Weighting**: Automatically assigns higher trust scores to `.gov`, `.edu`, and scientific domains.

### 💻 Modern "Cyber-Noir" Interface
-   **Futuristic UI**: deep space blue theme with neon cyan/purple accents using **Tailwind CSS**.
-   **Real-Time Dashboard**: Track system stats, truth rates, and scan history in the Command Center.
-   **Interactive Visuals**: Animated confidence gauges, evidence streams, and live "scanning" effects.

### ⚙️ Enterprise-Ready
-   **REST API**: Fully documented endpoint (`/api/verify`) for external integration.
-   **Persistence**: Built-in SQLite database stores all verification history.
-   **Scalable Architecture**: Modular design separating Extraction, Retrieval, and Classification layers.

---

## 🏛️ System Architecture (Top-to-Bottom)

The application follows a strictly layered pipeline architecture:

1.  **Input Layer**:
    -   User submits a claim via the **Web UI** or **API**.
    -   The `ClaimExtractor` identifies factual statements using **spaCy**.

2.  **Retrieval Layer**:
    -   `KeywordExtractor` pulls search terms (Entities/Nouns).
    -   `EvidenceRetriever` scrapes trusted sources (Wikipedia, Google, DuckDuckGo).
    -   Evidence is filtered by domain credibility and semantic similarity.

3.  **Inference Layer (The "Brain")**:
    -   Filtered evidence is paired with the claim (Premise + Hypothesis).
    -   **NLI Models** classify each pair as `Entailment`, `Contradiction`, or `Neutral`.
    -   A weighted voting algorithm calculates the final **Verdict** and **Confidence Score**.

4.  **Presentation Layer**:
    -   Results are returned to the user with a color-coded verdict (Green/Red/Amber).
    -   Data is archived in the `history.db` SQLite database.

---

## 🚀 Installation & Setup Guide

Follow these steps to deploy the system locally.

### Prerequisites
-   **Python 3.10+** installed.
-   **Git** installed.
-   Internet connection (for downloading models).

### Step 1: Clone the Repository
```bash
git clone https://github.com/CHRISDANIEL145/truth-check.git
cd truth-check
```

### Step 2: Create Virtual Environment
Isolate dependencies to avoid conflicts.
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
This will install PyTorch, Transformers, spaCy, and Flask.
```bash
pip install -r requirements.txt
```

### Step 4: Download Language Models
Pre-download the necessary NLI and spaCy models.
```bash
python -m spacy download en_core_web_sm
```
*Note: The Transformer models (RoBERTa/DeBERTa) will automatically download on the first run (approx. 3GB).*

### Step 5: Run the Application
Start the Flask server.
```bash
python run.py
```
You should see output indicating the server is running on `http://127.0.0.1:5000`.

---

## 📖 Usage Guide

### 1. Using the Analyzer
-   Navigate to `http://127.0.0.1:5000`.
-   Type a factual claim (e.g., *"The Great Wall of China is visible from space"*).
-   Click **INIT_SCAN**.
-   View the Verdict, Confidence Score, and supporting/contradicting Evidence.

### 2. The Dashboard
-   Click **Dashboard** in the top navigation.
-   View global statistics (Truth Rate, Total Scans).
-   Review your complete verification history.

### 3. API Integration
Invoke the verification engine programmatically:

**Endpoint:** `POST /api/verify`

**Request:**
```json
{
  "claim": "Water boils at 100 degrees Celsius."
}
```

**Response:**
```json
{
  "label": "True",
  "confidence": 0.99,
  "evidence": "..."
}
```

---

## 📂 Project Structure

```
TruthCheck/
├── app.py                 # Main Flask application & routes
├── run.py                 # Entry point
├── history.db             # SQLite database (auto-created)
├── models/                # AI Core
│   ├── claim_extractor.py # Identifies claims
│   ├── evidence_retriever.py # Web scraping logic
│   ├── keyword_extractor.py  # NLP keyword extraction
│   └── nli_classifier.py     # RoBERTa/DeBERTa inference pipeline
├── static/                # Frontend Assets
│   ├── css/style.css      # Custom animations & styles
│   └── js/main.js         # Frontend logic
├── templates/             # HTML Views
│   ├── index.html         # Analyzer UI
│   ├── dashboard.html     # Stats & History
│   ├── how_it_works.html  # Architecture Docs
│   └── api.html           # API Docs
└── utils/                 # Helpers
    └── config.py          # App configuration
```

---

## 🤝 Contributing
Contributions are welcome! Please fork the repository and submit a Pull Request.

## 📄 License
This project is licensed under the MIT License.
