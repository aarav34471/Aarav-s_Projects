# CUDA Parallel Histogram

A CUDA implementation of minimum and maximum reduction followed by construction of a 512-bin histogram over binary floating-point samples.

## Overview

The program loads single-precision values from a binary input file, determines the data range on the GPU, and builds a histogram using CUDA kernels. It demonstrates parallel reduction, shared memory, synchronisation, atomic updates, explicit host/device memory management, and CUDA event timing.

## Implementation

- `maxReduceKernel` and `minReduceKernel` perform multi-pass, block-level reductions in shared memory.
- `histogramKernel512` accumulates a per-block histogram in shared memory before merging counts into global memory with atomic operations.
- `histogram512` manages device allocation, host/device transfers, kernel timing, and result retrieval.
- The command-line program verifies the histogram total after printing all 512 bins.

## Requirements

- NVIDIA GPU supporting CUDA and 1,024-thread blocks
- NVIDIA CUDA Toolkit with `nvcc`
- A binary input file containing contiguous 32-bit floating-point values

The original input dataset is not included. `data_points.pbin` is ignored so locally supplied data is not committed.

## Build and Run

From this directory:

```bash
nvcc -O2 -o cuda-histogram cuda_histogram.cu main.cpp
./cuda-histogram /path/to/data_points.pbin
```

## Project Structure

```text
cuda-parallel-histogram/
├── cuda_histogram.cu   # CUDA reductions, histogram kernel, and host wrappers
├── cuda_histogram.hpp  # Shared declarations and fixed kernel parameters
└── main.cpp            # Input loading, execution, and result reporting
```

## Limitations

- The block size and histogram size are fixed at 1,024 threads and 512 bins.
- Kernel timing covers histogram construction rather than the complete end-to-end program.
- The project does not include a CPU baseline, automated tests, or representative input data.
- Production use would require stronger input validation and broader GPU compatibility checks.

## Provenance

The implementation originated as COM2039 histogram coursework. The supplied archive did not include a licence file, dataset, or generated output; confirm reuse and distribution rights before republishing the source independently.
