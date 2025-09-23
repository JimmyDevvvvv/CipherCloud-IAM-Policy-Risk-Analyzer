# CipherCloud: IAM Policy Risk Analyzer

A machine learning system for analyzing AWS IAM policies to identify risky permissions and generate safer alternatives.

## Overview

CipherCloud analyzes IAM policies using machine learning classifiers to detect dangerous permission combinations and automatically suggests policy improvements. The system uses both binary classification (safe/risky) and multi-class classification to categorize specific attack vectors.

## Core Components

- **Binary Classifier**: Determines if a policy contains risky permissions
- **Attack Family Classifier**: Categorizes threats into specific attack types
- **Policy Rewriter**: Generates safer policy alternatives using fine-tuned language models
- **CLI Scanner**: Command-line interface for batch analysis
- **Dataset Generators**: Creates synthetic training data

## Installation

```bash
git clone https://github.com/JimmyDevvvvv/CipherCloud-IAM-Policy-Risk-Analyzer.git
cd CipherCloud-IAM-Policy-Risk-Analyzer

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
```

## Usage

Basic policy analysis:
```bash
python Scanners/Binary_Scanner.py policies/example.json
```

Complete analysis with rewrite suggestions:
```bash
python Scanners/Complete_Scanner.py policies/example.json
```

Batch processing:
```bash
python Scanners/Batch_Scanner.py policies/
```

## Directory Structure

```
CipherCloud/
├── Binary Dataset/      # Binary classification training data
├── Classifier Dataset/  # Multi-class training data
├── Generators/         # Synthetic data generation
├── Models/            # ML model training scripts
├── Scanners/          # Analysis tools
├── policies/          # Sample policies
├── rewrites/          # Generated policy fixes
└── utils/             # Shared utilities
```

## Attack Categories

The system identifies these attack patterns:

- **Privilege Escalation**: Gaining higher privileges through permission combinations
- **Shadow Admin**: Near-administrative access without obvious indicators
- **Persistence**: Mechanisms for maintaining long-term access
- **Data Exfiltration**: Unauthorized access to sensitive data
- **Lateral Movement**: Cross-service or cross-account access
- **Service Abuse**: Misuse of AWS services for malicious purposes
- **KMS Abuse**: Unauthorized encryption/decryption operations
- **Secrets Theft**: Access to credentials and sensitive parameters
- **Destructive Actions**: Permissions that can cause service disruption
- **Policy Backdooring**: Subtle modifications to existing policies

## Technical Implementation

**Machine Learning Pipeline:**
1. Feature extraction using TF-IDF and custom policy features
2. Binary classification for initial risk assessment
3. Multi-class classification for attack categorization
4. Language model fine-tuning for policy rewriting

**Technology Stack:**
- scikit-learn and joblib for ML models
- transformers library for language model fine-tuning
- pandas and numpy for data processing
- argparse and rich for CLI interface

## Training Custom Models

Generate training data:
```bash
python Generators/PolicyGenerator.py --samples 5000 --output datasets/
```

Train classifiers:
```bash
python Models/train_binary_classifier.py --data datasets/binary/
python Models/train_family_classifier.py --data datasets/classifier/
```

Fine-tune language model:
```bash
python Models/finetune_llm.py --model falcon-7b --data datasets/rewrites/
```

## Performance

Current model performance on test datasets:

| Metric | Binary Classifier | Family Classifier |
|--------|------------------|-------------------|
| Accuracy | 94.2% | 89.7% |
| Precision | 93.8% | 88.4% |
| Recall | 94.6% | 90.1% |
| F1-Score | 94.2% | 89.2% |

## Configuration

Create `config.yaml` to customize behavior:

```yaml
models:
  binary_classifier: "models/binary_clf.joblib"
  family_classifier: "models/family_clf.joblib"
  llm_model: "microsoft/DialoGPT-medium"

thresholds:
  risk_threshold: 0.7
  confidence_threshold: 0.8

output:
  save_rewrites: true
  verbose: true
  format: "json"
```

## Known Limitations

- Language model outputs may contain JSON syntax errors
- Policy rewrites require manual review before production use
- No direct AWS API integration
- Limited to AWS IAM policies (no Azure/GCP support)

## Development

Install development dependencies:
```bash
pip install -r requirements-dev.txt
```

Run tests:
```bash
pytest tests/
```

Code formatting:
```bash
black .
flake8 .
```

## Contributors

- Mohamed Gamal (@JimmyDevvvvv)
- Ahmed Hegab (@AHegab)
- AhmedishimAplus (@AhmedishimAplus)
- Ammar Hassona (@AmmarHassona)
- Abdullah Mohamed (@Sicariusa)
- Abdulrahman Alawbathani (@VizardeX)
- Yehia Fadly (@Yehia3A)

## License

MIT License - see LICENSE file for details.
