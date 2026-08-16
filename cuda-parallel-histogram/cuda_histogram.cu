//============================================================================
// Name        : cuda_histogram.cu
// Version     :
// Copyright   :
// Description : CUDA parallel reduction and histogram implementation
//============================================================================

#include "cuda_histogram.hpp"

/// Error Checking
#define gpuErrchk(ans) { gpuAssert((ans), __FILE__, __LINE__); }
inline void gpuAssert(cudaError_t code, const char *file, int line, bool abort=true)
{
	if (code != cudaSuccess)
	{
		fprintf(stderr,"GPUassert: %s %s %d\n", cudaGetErrorString(code), file, line);
		if (abort) exit(code);
	}
}

/// Loading file
size_t loadSamples(const char* path_to_data_points_file, float** ptr ){
    std::ifstream file (path_to_data_points_file, std::ios::in|std::ios::binary|std::ios::ate);
    std::streampos size_read = file.tellg();
    if (size_read < 0){
        std::cout << "Error reading file " << path_to_data_points_file << std::endl;
        exit(1);
    }
    size_t len_array = size_read/sizeof(float);
    std::cout << "Read :" << size_read << " bytes = " << len_array << " elements." << std::endl;

    char* memblock = new char[size_read];
    file.seekg(0, std::ios::beg);
    file.read (memblock, size_read);    file.close();
    std::cout << "Correctly loaded "<< path_to_data_points_file << std::endl;
    *ptr = (float*)memblock;

    return len_array;
}

/////// Find Maximum
__global__ void maxReduceKernel(float *d_in, size_t len_array){
	//

    __shared__ float sdata[BLOCK_SIZE];
    unsigned int tid = threadIdx.x;
    unsigned int idx = blockIdx.x * blockDim.x + threadIdx.x;

    // Load or identity for max
    if (idx < len_array) {
        sdata[tid] = d_in[idx];
    }
    else {
        sdata[tid] = -FLT_MAX;    // identity first element is absolute lowest
    }
    __syncthreads();

    // Perform Reduction
    for (unsigned int stride = blockDim.x / 2; stride > 0; stride >>= 1) {
        if (tid < stride) {
            if (sdata[tid] < sdata[tid + stride]) {
                sdata[tid] = sdata[tid + stride];
            }
        }
        __syncthreads();
    }

    // Write block�s maximum
    if (tid == 0) {
        d_in[blockIdx.x] = sdata[0];
    }
    //
}


float findMaxValue(float* samples_h, size_t len_array){
	//
    // Allocate GPU memory checking for errors
    float* d_data;
    cudaError_t err;
    err = cudaMalloc((void**)&d_data, len_array * sizeof(float));
    if (err != cudaSuccess) {
        std::cout << "CUDA Error allocating memory for d_data: " << cudaGetErrorString(err) << std::endl;
        exit(-1);
    }
    // Copy input from CPU to GPU
    err = cudaMemcpy(d_data, samples_h, len_array * sizeof(float), cudaMemcpyHostToDevice);
    if (err != cudaSuccess) {
        std::cout << "CUDA Error copying samples_h to d_data: " << cudaGetErrorString(err) << std::endl;
        exit(-1);
    }
    // Multi-block reduction
    size_t len_active = len_array;
    int num_blocks = (len_active + BLOCK_SIZE - 1) / BLOCK_SIZE;
    while (len_active > BLOCK_SIZE) {
        std::cout << "len :" << len_active << " num_blocks: " << num_blocks << std::endl;
        maxReduceKernel <<< num_blocks, BLOCK_SIZE >> > (d_data, len_active);
        len_active = num_blocks;
        num_blocks = (len_active + BLOCK_SIZE - 1) / BLOCK_SIZE;
    }
    // Last pass
    maxReduceKernel <<< 1, BLOCK_SIZE >> > (d_data, len_active);

    // Copy result of reduction to CPU
    float max_val;
    err = cudaMemcpy(&max_val, d_data, sizeof(float), cudaMemcpyDeviceToHost);
    if (err != cudaSuccess) {
        std::cout << "CUDA Error copying result to max_val: " << cudaGetErrorString(err) << std::endl;
        exit(-1);
    }
    cudaFree(d_data);
    return max_val;
}



/////// Find Minimum
__global__ void minReduceKernel(float *d_in, size_t len_array){
	//
    __shared__ float sdata[BLOCK_SIZE];
    unsigned int tid = threadIdx.x;
    size_t idx = blockIdx.x * blockDim.x + tid;
    // load element or identity
    if (idx < len_array) {
        sdata[tid] = d_in[idx];
    }
    else {
        sdata[tid] = FLT_MAX;  // identity for min
    }
    __syncthreads();
    // reduction tree to find block minima
    for (unsigned int stride = blockDim.x / 2; stride > 0; stride >>= 1) {
        if (tid < stride) {
            if (sdata[tid] > sdata[tid + stride]) {
                sdata[tid] = sdata[tid + stride];
            }
        }
        __syncthreads();
    }
    // write block result
    if (tid == 0) {
        d_in[blockIdx.x] = sdata[0];
    }

	//
}


float findMinValue(float* samples_h, size_t len_array){
	//
    // Allocate GPU memory checking for errors
    float* d_data;
    cudaError_t err;
    err = cudaMalloc((void**)&d_data, len_array * sizeof(float));
    if (err != cudaSuccess) {
        std::cout << "CUDA Error allocating memory for d_data: " << cudaGetErrorString(err) << std::endl;
        exit(-1);
    }
    // Copy input from CPU to GPU
    err = cudaMemcpy(d_data, samples_h, len_array * sizeof(float), cudaMemcpyHostToDevice);
    if (err != cudaSuccess) {
        std::cout << "CUDA Error copying samples_h to d_data: " << cudaGetErrorString(err) << std::endl;
        exit(-1);
    }
    // Multi-block reduction
    size_t len_active = len_array;
    int num_blocks = (len_active + BLOCK_SIZE - 1) / BLOCK_SIZE;
    while (len_active > BLOCK_SIZE) {
        std::cout << "len :" << len_active << " num_blocks: " << num_blocks << std::endl;
        minReduceKernel <<< num_blocks, BLOCK_SIZE >>> (d_data, len_active);
        len_active = num_blocks;
        num_blocks = (len_active + BLOCK_SIZE - 1) / BLOCK_SIZE;
    }
    // Last pass
    minReduceKernel <<< 1, BLOCK_SIZE >> > (d_data, len_active);

    // Copy result of reduction to CPU
    float min_val;
    err = cudaMemcpy(&min_val, d_data, sizeof(float), cudaMemcpyDeviceToHost);
    if (err != cudaSuccess) {
        std::cout << "CUDA Error copying result to min_val: " << cudaGetErrorString(err) << std::endl;
        exit(-1);
    }
    cudaFree(d_data);
    return min_val;

	//
}



/////// Create Histogram
__global__ void histogramKernel512(float *d_in, unsigned int *hist, size_t len_array, float min_value, float max_value) {
	//
    __shared__ unsigned int hist_shared[NUM_BINS];
    for (size_t b = threadIdx.x; b < NUM_BINS; b += blockDim.x) {
        hist_shared[b] = 0u; // identity values all bin values are 0 in order to allow for addition
    }
    __syncthreads(); //sync make sure all threads reach here before starting computation
    size_t tid = blockIdx.x * blockDim.x + threadIdx.x; //index for threads
    if (tid < len_array) {
        //now i will normalize the data, since we dont know if it starts at 0 or not,
        //we will make sure to translate the data in a way the min value is at bin 0
        // then since we translate all values by min value the denominator value is max - min
        //then ofcourse convert to unsigned int
        unsigned int bin = (d_in[tid] - min_value) * NUM_BINS / (max_value - min_value);

        //atomicadd so no 2 threads are trying to access memory at once
        if (bin >= NUM_BINS) {
            bin = NUM_BINS - 1;
        } //for the 511th bin
        atomicAdd(&hist_shared[bin], 1);;
    }
    __syncthreads();
    for (size_t b = threadIdx.x; b < NUM_BINS; b += blockDim.x) {
        //copying data to global memory
        unsigned int count = hist_shared[b];
        if (count > 0) atomicAdd(&hist[b], count);
    }

	//
}



/// histogram
void histogram512(float *samples_h, size_t len_array, unsigned int **hist_h, float min_value, float max_value) {
	//
	// Timing variables:
    cudaEvent_t start, stop;
    cudaEventCreate(&start);
    cudaEventCreate(&stop);

    // Device pointers
    float* input_d;
    unsigned int* hist_d;
    cudaError_t err;

    // Allocate GPU Memory for input_d
    err = cudaMalloc((void**)&input_d, len_array * sizeof(float));
    if (err != cudaSuccess) {
        std::cout << "CUDA Error allocating memory for input_d: " << cudaGetErrorString(err) << std::endl;
        exit(-1);
    }
    // Allocate GPU Memory for hist_d
    err = cudaMalloc((void**)&hist_d, NUM_BINS * sizeof(unsigned int));
    if (err != cudaSuccess) {
        std::cout << "CUDA Error allocating memory for hist_d: " << cudaGetErrorString(err) << std::endl;
        exit(-1);
    }
    // Zero initial histogram in GPU
    err = cudaMemset(hist_d, 0, NUM_BINS * sizeof(unsigned int));
    if (err != cudaSuccess) {
        std::cout << "CUDA Error setting values of hist_d to zero: " << cudaGetErrorString(err) << std::endl;
        exit(-1);
    }

    // Copy cpu input to gpu input_h --> input_d
    err = cudaMemcpy(input_d, samples_h, len_array * sizeof(float), cudaMemcpyHostToDevice);
    if (err != cudaSuccess) {
        std::cout << "CUDA Error copying samples_h to input_d: " << cudaGetErrorString(err) << std::endl;
        exit(-1);
    }

    // Determine grid size
    dim3 grid_size((len_array + BLOCK_SIZE - 1) / BLOCK_SIZE);
    std::cout << "Number of blocks being launched (grid_size): " << grid_size.x << std::endl;

    // Launch histogram kernel with timing
    cudaEventRecord(start);
    size_t sharedSize = NUM_BINS * sizeof(unsigned int);
    histogramKernel512<<<grid_size, BLOCK_SIZE, sharedSize>>>(input_d, hist_d, len_array, min_value, max_value);
    cudaEventRecord(stop);

    // Copy hist_d back into hist_h
    *hist_h = new unsigned int[NUM_BINS]();
    err = cudaMemcpy(*hist_h, hist_d, NUM_BINS * sizeof(unsigned int), cudaMemcpyDeviceToHost);
    if (err != cudaSuccess) {
        std::cout << "CUDA Error copying hist_d back into hist_h: " << cudaGetErrorString(err) << std::endl;
        exit(-1);
    }

    // Finish timing
    cudaEventSynchronize(stop);
    float milliseconds = 0;
    cudaEventElapsedTime(&milliseconds, start, stop);
    std::cout << "Kernel took " << milliseconds << "ms to finish." << std::endl;

    // Freeing GPU Memory
    cudaFree(hist_d);
    cudaFree(input_d);
	//
}
