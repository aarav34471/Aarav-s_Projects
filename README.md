# Software Engineering and Applied AI Portfolio

I build machine-learning systems and full-stack applications, with a particular interest in financial ML, natural-language processing, computer vision, and reliable backend engineering. This repository is a curated collection of end-to-end projects: each directory documents the problem, implementation, evaluation, and practical limitations.

## Featured Projects

### [Macroeconomic Event Impact Modelling](macroeconomic-event-impact-modelling/)

A financial-ML study of short-horizon S&P 500 futures reactions to CPI, GDP, non-farm payrolls, PCE, and retail-sales releases. The pipeline combines structured release surprises, volatility and market context, and FinBERT-derived text features, then compares logistic regression, XGBoost, and neural models using chronological walk-forward validation and a held-out 2025 test period. The final held-out results were deliberately modest (0.54 binary accuracy and 0.50 three-class accuracy across 46 events), illustrating the difficulty of extracting stable signal from a small, non-stationary event dataset.

`Python` `FinBERT` `PyTorch` `XGBoost` `Optuna` `scikit-learn` `time-series validation`

### [Sudra Backend](sudra-backend/)

A production-style ML inference service that exposes a TorchScript trading-behaviour model through FastAPI. Pydantic request models validate raw trade records before a deterministic preprocessing pipeline builds 55 ordered features, groups chronological sequences by trader, constructs causal and padding masks, and returns ten per-trade bias probabilities with label-specific thresholds. The containerised CPU service is built for ARM64 and deployed through GitHub Actions, Amazon ECR, ECS Fargate, Application Load Balancer health checks, and CloudWatch logging.

`Python` `FastAPI` `Pydantic` `PyTorch` `TorchScript` `Docker` `AWS ECS` `Amazon ECR` `GitHub Actions`

**Standalone repository:** [github.com/aarav34471/sudra-backend](https://github.com/aarav34471/sudra-backend)

### [Assistive Visual AI](assistive-visual-ai/)

An image-to-speech prototype that turns visual scenes into short spoken descriptions. It integrates YOLO26 object detection, SAM 3 segmentation, BLIP visual understanding, deterministic spatial language generation, and offline text-to-speech, with separate rich-image and low-latency video paths. Evaluation on a 100-image COCO subset measured a mean mask IoU of 0.576 and identified segmentation as the dominant latency cost in the full pipeline.

`Python` `PyTorch` `Ultralytics YOLO` `SAM 3` `BLIP` `OpenCV` `pyttsx3`

### [Ready Jobs](ready-jobs/)

A containerised job platform with role-specific experiences for graduates and employers. The Django REST backend exposes jobs, applications, profiles, bookmarks, and authentication APIs; the React client implements job discovery, application management, recommendations, and protected workflows. PostgreSQL, Docker Compose, and Nginx provide the supporting application stack.

`Django` `Django REST Framework` `React` `PostgreSQL` `JWT` `Docker` `Nginx`

### [PaySim Fraud Detection](paysim-fraud-detection/)

An imbalance-aware fraud-classification workflow built on synthetic mobile-money transactions. The notebooks cover exploratory analysis, leakage-conscious preprocessing, feature engineering, logistic baselines, five model families, thresholded evaluation, and business interpretation using fraud-class precision, recall, F1, ROC-AUC, and PR-AUC. The reported Random Forest result is the strongest candidate, while the current threshold-selection limitation is documented explicitly.

`Python` `pandas` `scikit-learn` `imbalanced-learn` `model evaluation`

## Additional Projects

| Project | Focus | Technologies |
| --- | --- | --- |
| [English Variants Sentiment and Sarcasm](english-variants-sentiment-sarcasm/) | An NLP investigation of sentiment and sarcasm across British, Australian, and Indian English. It compares TF-IDF baselines with fine-tuned RoBERTa and XLM-RoBERTa models, evaluates cross-variety generalisation, and analyses how dialect and code-mixing affect model behaviour. | Python, Hugging Face Transformers, RoBERTa, XLM-RoBERTa, scikit-learn, Gradio |
| [Neural Network Optimisation](neural-network-optimisation/) | Gradient-based and evolutionary optimisation of a ResNet classifier | PyTorch, DEAP, SGD, GA, differential evolution, NSGA-II |
| [BreastMNIST CNN](breastmnist-cnn/) | CNN training, evaluation, cross-validation, and ResNet18 transfer learning | PyTorch, MedMNIST, scikit-learn |
| [FlickFinder REST API](flickfinder-rest-api/) | Layered REST API over a SQLite movie database | Java, Javalin, JDBC, Maven, JUnit, Mockito |
| [Unix and Memory Management](unix-and-memory-management/) | Command execution and contiguous-memory allocation simulation | Java, Unix processes, linked data structures |
| [Pico Morse Code Decoder](pico-morse-code-decoder/) | Button-timed Morse input rendered on a seven-segment display | C, Raspberry Pi Pico SDK, GPIO, CMake |

## Repository Notes

- Raw licensed financial market data is not redistributed; the macroeconomic notebooks retain the outputs needed to review the analysis.
- Large model and dataset dependencies are documented within their projects, together with their upstream licensing requirements.
- Existing third-party and collaborator licence notices are preserved; copyright provenance should be confirmed before any future relicensing.
- Reported metrics are preserved from the existing project outputs. Expensive training workloads are not required merely to browse the portfolio.
