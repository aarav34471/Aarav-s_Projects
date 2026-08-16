# BreastMNIST CNN Classification

This notebook develops and evaluates convolutional neural networks for binary breast-tumour image classification using BreastMNIST.

## Technical Approach

The workflow includes dataset inspection, train/validation/test transforms, hyperparameter tuning, augmentation, Adam-versus-SGD comparison, a custom CNN architecture, precision-recall and ROC analysis, confusion matrices, cross-validation, and adaptation of an ImageNet-pretrained ResNet18 to the two-class target.

## Preserved Results

The strongest complete recorded custom-CNN run reports:

- validation AUC: 0.853;
- validation accuracy: 0.846;
- test AUC: 0.868;
- test accuracy: 0.865;
- positive-class F1: 0.891.

The notebook also contains five fold-level test AUC values between 0.861 and 0.882. A later ResNet18 run was interrupted, so no transfer-learning result is claimed.

## Running the Notebook

```bash
pip install jupyter matplotlib medmnist numpy scikit-learn torch torchvision
jupyter lab breastmnist-cnn-analysis.ipynb
```

BreastMNIST is downloaded through the `medmnist` package. A CUDA-capable environment is recommended for repeated training and cross-validation.

## Limitations

- This is an experimental classifier, not a clinical diagnostic system.
- The notebook preserves existing outputs rather than rerunning costly training.
- The final transfer-learning cell did not complete and requires a fresh controlled run.
- Medical validation would require external datasets, calibration analysis, and domain-expert review.
