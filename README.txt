# ☁️ CipherCloud: AI-Powered IAM Policy Risk Analyzer

**CipherCloud** is a modular, ML-powered cloud IAM policy analyzer that detects risky permissions, classifies threats by attack family, and rewrites unsafe IAM policies using a fine-tuned LLM. It was inspired by tools like PMapper, CloudSplaining, and IAM Access Analyzer, but rebuilt from scratch to deeply understand the attack surface of IAM roles and policies through machine learning and AI-driven remediation.

This tool is not just a static scanner — it's an AI-backed defense and educational engine that teaches you *why* policies are risky, what attack they enable (e.g., Privilege Escalation or KMS Abuse), and how to **fix them automatically**.

---

## 📸 Demo

▶️ **Video Demo** – See CipherCloud scanning and remediating real IAM policies

![Attack Flow](https://github.com/user-attachments/assets/12b47f8a-riskmap.png)

---

## 🚀 Features

* 🔍 **Binary Risk Scanner** – Detects whether a policy is *Safe* or *Risky*
* 🧠 **Attack Family Classifier** – Multi-class ML model to categorize attack type
* ✍️ **LLM Policy Rewriter** – Fine-tuned model to generate safer policy versions
* 📊 **Explainability Layer** – Outputs exact reasons for risky verdicts
* 🧪 **CLI Scanner** – Scan and classify IAM policies in bulk
* 🧱 **Realistic Dataset Generator** – Create synthetic risky policies for training

---

## 🧠 Tech Stack

* Python 3.11
* `scikit-learn`, `joblib` – ML classifiers
* `transformers`, `peft` – LLM fine-tuning (LoRA)
* `argparse`, `json`, `pandas` – CLI scanner, data processing

---

## 📦 Directory Structure

```
CipherCloud/
├── Binary Dataset/           → Safe vs Risky policies (labeled)
├── Classifier Dataset/       → Multi-class attack-labeled policies
├── Generators/               → Synthetic policy generators (by attack family)
├── Models/                   → Binary & family classifiers, LLM finetuning scripts
├── Scanners/                 → CLI tools to scan, classify, rewrite policies
├── policies/                 → Input IAM policies for testing
├── rewrites/                 → Output from LLM rewriter
├── utils/                    → Feature extraction, JSON parsing, shared functions
├── README.md
└── requirements.txt
```

---

## ⚙️ Setup Instructions

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/CipherCloud.git
cd CipherCloud

# 2. Create virtual env
python3 -m venv env
source env/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run a binary scan
python Scanners/Binary_Scanner.py policies/example.json

# 5. Run full scan with attack classification and rewrite
python Scanners/Complete_Scanner.py policies/example.json
```

---

## 🧪 How It Works

1. Input IAM policy is passed through the **feature extractor**
2. **Binary Classifier** predicts if it's *Safe* or *Risky*
3. If *Risky*, **Attack Family Classifier** predicts the threat category:

   * Privilege Escalation
   * Shadow Admin
   * Persistence
   * Data Exfiltration
   * Lateral Movement
   * Service Abuse
   * KMS Abuse
   * Secrets Theft
   * DoS / Destructive Actions
   * Policy Backdooring
4. **LLM Policy Rewriter** suggests a safer version (optional)
5. Logs are written and outputs saved in `rewrites/`

---

## 📈 Training & Data Engineering

CipherCloud includes a full synthetic data generator:

* 10 attack families + Safe class
* Family-specific templates to generate 1000s of realistic samples
* `TF-IDF + ML` feature extraction
* LoRA fine-tuning on policy rewrites using `falcon` or `mistral`
* Multi-class classifier trained with 10-fold validation

---

## 📊 Example Output

```
Policy: policies/example.json

✅ Verdict: RISKY
📂 Family: Privilege Escalation
⚠️ Reason: Allows iam:PassRole + ec2:RunInstances

💡 Suggested Rewrite:
"Effect": "Allow",
"Action": "ec2:DescribeInstances",
"Resource": "arn:aws:ec2:region:account:instance/i-*"
```

---

## 🔐 Limitations

* LLM rewrites may occasionally produce invalid JSON
* Rewrites aren't guaranteed to be least-privilege unless refined
* No live AWS role pull (for now)
* No policy diff visualizer (WIP)

---

## 👨‍💻 Author

**Mohamed Gamal** (JimmyDevvvvv)

A cybersecurity builder passionate about real-time defense, policy hardening, and the future of AI in cloud security.

---

## 📄 License

**MIT License** – See [`LICENSE`](./LICENSE)
