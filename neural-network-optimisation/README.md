# Neural Network Optimisation Benchmark

This experiment compares gradient descent with evolutionary approaches for training a ResNet18 classifier on CIFAR-10.

## Overview

The notebook establishes a conventional stochastic-gradient-descent baseline, then treats the final classification layer as a search vector for several derivative-free optimisers. The objective is to examine the accuracy/compute trade-off rather than claim that evolutionary search is a drop-in replacement for backpropagation.

## Methods

- Full-network SGD training.
- Genetic Algorithm optimisation of the final layer.
- A memetic Genetic Algorithm with short Adam local-search steps.
- Differential Evolution over the final-layer parameters.
- NSGA-II using accuracy and parameter magnitude as competing objectives.

All evolutionary methods use DEAP and freeze the pretrained feature extractor. Saved `.pth` checkpoints and generated figures are local experiment outputs.

## Preserved Results

| Method | Recorded CIFAR-10 test accuracy |
| --- | ---: |
| Full-network SGD | 77.76% |
| Genetic Algorithm, final layer | 46.47% |
| Memetic GA/Adam, final layer | 27.42% |
| Differential Evolution, final layer | 47.91% |
| NSGA-II selected solution | 41.00% |

These results are exploratory rather than a controlled leaderboard: SGD trains the full network, while the evolutionary runs optimise only the last layer and use sampled minibatches during fitness evaluation. The principal finding is that standard gradient training delivered much better accuracy under the implemented setup.

## Running the Notebook

Open [`optimisation-benchmark.ipynb`](optimisation-benchmark.ipynb) in Jupyter or Google Colab. A CUDA runtime is recommended.

```bash
pip install torch torchvision deap numpy matplotlib
```

The complete experiment is compute-intensive: the recorded SGD run used 10 epochs, while evolutionary runs use repeated population-level model evaluations.

## Limitations

- Compute budgets are not normalised across methods.
- Several fitness functions use a single minibatch, increasing variance.
- Only the classifier head is evolved, whereas the SGD baseline updates the full network.
- Results come from one architecture and dataset.
