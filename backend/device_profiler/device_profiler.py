"""
GreenMind Device Profiler (Phase 1 CLI Tool).
Measures available computational power, hardware telemetry, and derives S_avail.
"""

import argparse
import datetime
import json
import sys
import time
from typing import Optional

from .hardware_detector import HardwareDetector
from .micro_benchmark import MicroBenchmark
from .scoring import ComputeScoreCalculator, DeviceProfile


class DeviceProfiler:
    """Coordinates hardware detection, micro-benchmarking, and score calculation."""

    def __init__(self):
        self.detector = HardwareDetector()

    def profile(self, run_benchmark: bool = True) -> DeviceProfile:
        """Collects full profile and computes S_avail score."""
        timestamp_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        telemetry = self.detector.get_complete_telemetry()

        if run_benchmark:
            benchmark = MicroBenchmark(matrix_size=1024, iterations=4).run()
        else:
            benchmark = {
                "gflops": 0.0,
                "compute_latency_ms": 0.0,
                "mem_bandwidth_gbps": 0.0,
                "benchmark_duration_ms": 0.0,
                "backend": "Skipped (--quick)",
            }

        return ComputeScoreCalculator.calculate(telemetry, benchmark, timestamp_str)


def format_progress_bar(val: float, max_val: float = 100.0, width: int = 24) -> str:
    """Renders a text progress bar."""
    filled = int((val / max_val) * width)
    filled = max(0, min(width, filled))
    bar = "█" * filled + "░" * (width - filled)
    return f"[{bar}] {val:5.1f} / {max_val:.0f}"


def print_cli_report(profile: DeviceProfile):
    """Prints a streamlined terminal report showing only device info, calculation steps, and final score."""
    p = profile
    c = p.calculation_details
    cpu = p.cpu_info
    mem = p.memory_info
    power = p.power_info

    # Ensure UTF-8 output on Windows consoles
    if sys.stdout and hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    print("\n" + "=" * 68)
    print("           GREENMIND: EDGE COMPUTATIONAL POWER PROFILER            ")
    print("=" * 68)

    # 1. DEVICE INFO
    print("\n[1] DEVICE INFORMATION")
    print(f"  - CPU Model         : {cpu['model']}")
    clock_val = cpu.get('max_frequency_mhz') or cpu.get('current_frequency_mhz') or 'N/A'
    print(f"  - Hardware Specs    : {cpu['physical_cores']} Physical Cores | {cpu['logical_threads']} Threads @ {clock_val} MHz")
    print(f"  - System Memory     : {mem['total_gb']} GB Total ({mem['available_gb']} GB Available / Free)")
    gpu_names = ", ".join([f"{g['name']} ({g.get('dedicated_vram_gb', 0)} GB VRAM)" for g in p.gpu_info])
    print(f"  - GPU Accelerator   : {gpu_names}")
    print(f"  - Current Workload  : CPU Load: {c['cpu_load']}% | RAM Used: {c['ram_load']}%")
    print(f"  - Power & Battery   : {power['status']} ({power['percent']}%)")

    # 2. CALCULATION STEPS
    print("\n[2] CALCULATION STEPS")
    print("  Step A: Compute Potential (C_base: max 40 pts)")
    print(f"    - Cores Score     : ({c['physical_cores']} / 16) * 15.0 pts          = {c['core_score']:4.2f} pts")
    print(f"    - Clock Score     : ({c['clock_mhz']} / 4500) * 10.0 pts       = {c['clock_score']:4.2f} pts")
    print(f"    - Benchmark Math  : ({c['gflops']} GFLOPS / 250) * 8.0 pts = {c['benchmark_score']:4.2f} pts")
    gpu_label = p.gpu_info[0]['name'] if p.gpu_info else "Integrated"
    print(f"    - GPU Accelerator : {gpu_label[:20]}         = {c['gpu_score']:4.2f} pts")
    print(f"    -> Subtotal C_base: {c['core_score']} + {c['clock_score']} + {c['benchmark_score']} + {c['gpu_score']} = {c['c_base']:4.2f} / 40.0 pts")

    print("\n  Step B: Memory Headroom (M_room: max 35 pts)")
    print(f"    - Available RAM   : {c['avail_ram_gb']} GB Free                   = {c['m_score']:4.2f} / 35.0 pts")

    print("\n  Step C: Raw Hardware Potential (normalized to 100)")
    print(f"    - Raw Potential   : ({c['c_base']} + {c['m_score']}) * (100 / 75)      = {c['raw_potential']:4.2f} / 100")

    print("\n  Step D: Real-Time Operating Adjusters")
    print(f"    - Combined Load    : (0.65 * {c['cpu_load']}%) + (0.35 * {c['ram_load']}%)   = {c['combined_load']}%")
    print(f"    - Load Factor (L)  : Headroom multiplier based on load = x{c['load_factor']:0.2f}")
    print(f"    - Battery Factor (B): Multiplier for power/battery     = x{c['battery_factor']:0.2f}")

    print("\n  Step E: Final Available Score (S_avail)")
    print(f"    - Final Formula    : {c['raw_potential']} * {c['load_factor']} * {c['battery_factor']}           = {c['s_available']:4.1f} / 100")

    # 3. FINAL SCORE
    print("\n" + "=" * 68)
    bar_str = format_progress_bar(p.s_available, 100.0, 24)
    print(f"  FINAL SCORE (S_avail) : {bar_str}")
    print("=" * 68 + "\n")


def main():
    parser = argparse.ArgumentParser(description="GreenMind Edge Computational Power Profiler (Phase 1)")
    parser.add_argument("--quick", action="store_true", help="Skip micro-benchmark for instantaneous telemetry (<50ms)")
    parser.add_argument("--json", action="store_true", help="Output raw telemetry and score as JSON")
    parser.add_argument("--output", type=str, default=None, help="Save profile JSON to specified filepath")
    parser.add_argument("--prompt", "-p", type=str, default=None, help="Evaluate prompt complexity and routing feasibility against this device profile")
    parser.add_argument("--watch", type=int, default=None, metavar="SECONDS", help="Continuously monitor and refresh score every N seconds")

    args = parser.parse_args()
    profiler = DeviceProfiler()

    if args.watch:
        try:
            print(f"Starting GreenMind live monitor (refreshing every {args.watch}s). Press Ctrl+C to stop.")
            while True:
                profile = profiler.profile(run_benchmark=not args.quick)
                # Clear terminal screen (Windows / POSIX compatible)
                print("\033[H\033[J", end="")
                print_cli_report(profile)
                time.sleep(args.watch)
        except KeyboardInterrupt:
            print("\nMonitoring stopped.")
            sys.exit(0)

    profile = profiler.profile(run_benchmark=not args.quick)

    if args.prompt:
        from src.analyzer.workload_router import WorkloadRouter, print_routing_report
        router = WorkloadRouter()
        decision = router.route(args.prompt, profile)
        if args.json:
            print(json.dumps(decision.to_dict(), indent=2))
        else:
            print_cli_report(profile)
            print_routing_report(decision)
        return

    if args.json:
        print(json.dumps(profile.to_dict(), indent=2))
    else:
        print_cli_report(profile)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(profile.to_dict(), f, indent=2)
        print(f"📁 Profile successfully saved to: {args.output}")


if __name__ == "__main__":
    main()
