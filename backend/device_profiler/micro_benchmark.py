"""
Micro-Benchmark module for GreenMind.
Performs lightweight, non-invasive computational and memory benchmarks
to test real-time floating point throughput (GFLOPS) and memory bandwidth.
"""

import time
from typing import Dict, Any

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False


class MicroBenchmark:
    """Lightweight system compute and memory benchmark."""

    def __init__(self, matrix_size: int = 1024, iterations: int = 4, mem_size_mb: int = 64):
        self.matrix_size = matrix_size
        self.iterations = iterations
        self.mem_size_mb = mem_size_mb

    def run(self) -> Dict[str, Any]:
        """Runs the benchmark suite and returns metrics."""
        results = {
            "gflops": 0.0,
            "compute_latency_ms": 0.0,
            "mem_bandwidth_gbps": 0.0,
            "benchmark_duration_ms": 0.0,
            "backend": "none",
        }

        total_start = time.perf_counter()

        if NUMPY_AVAILABLE:
            results.update(self._run_numpy_benchmark())
        else:
            results.update(self._run_fallback_benchmark())

        results["benchmark_duration_ms"] = round((time.perf_counter() - total_start) * 1000, 2)
        return results

    def _run_numpy_benchmark(self) -> Dict[str, Any]:
        """NumPy BLAS-accelerated floating point benchmark."""
        n = self.matrix_size
        # 1. Warm-up
        a = np.random.rand(n, n).astype(np.float32)
        b = np.random.rand(n, n).astype(np.float32)
        _ = np.dot(a, b)

        # 2. Compute Benchmark (Matrix Multiplication: 2 * n^3 FLOPs)
        start_compute = time.perf_counter()
        for _ in range(self.iterations):
            _ = np.dot(a, b)
        compute_elapsed = time.perf_counter() - start_compute

        total_flops = 2.0 * (n ** 3) * self.iterations
        gflops = (total_flops / (compute_elapsed * 1e9)) if compute_elapsed > 0 else 0.0
        avg_latency_ms = (compute_elapsed / self.iterations) * 1000

        # 3. Memory Read Bandwidth Benchmark
        # Allocate array of requested size
        num_floats = (self.mem_size_mb * 1024 * 1024) // 4
        mem_arr = np.ones(num_floats, dtype=np.float32)

        start_mem = time.perf_counter()
        # Sum reduction forces reading all elements from memory
        _ = np.sum(mem_arr)
        mem_elapsed = time.perf_counter() - start_mem

        mem_gb = mem_arr.nbytes / (1024 ** 3)
        mem_bw = (mem_gb / mem_elapsed) if mem_elapsed > 0 else 0.0

        return {
            "gflops": round(gflops, 2),
            "compute_latency_ms": round(avg_latency_ms, 2),
            "mem_bandwidth_gbps": round(mem_bw, 2),
            "backend": f"NumPy (BLAS/Vectorized, {n}x{n} float32)",
        }

    def _run_fallback_benchmark(self) -> Dict[str, Any]:
        """Pure Python fallback if NumPy is missing."""
        n = 100
        start = time.perf_counter()
        a = [[1.0] * n for _ in range(n)]
        b = [[2.0] * n for _ in range(n)]
        c = [[0.0] * n for _ in range(n)]
        for i in range(n):
            for j in range(n):
                c[i][j] = sum(a[i][k] * b[k][j] for k in range(n))
        elapsed = time.perf_counter() - start

        flops = 2 * (n ** 3)
        gflops = (flops / (elapsed * 1e9)) if elapsed > 0 else 0.0
        return {
            "gflops": round(gflops, 4),
            "compute_latency_ms": round(elapsed * 1000, 2),
            "mem_bandwidth_gbps": 0.0,
            "backend": "Pure Python (Single-Threaded Fallback)",
        }
