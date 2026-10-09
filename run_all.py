#!/usr/bin/env python3
"""
run_all.py
==========
Master reproduction runner for:
"Embodied Physical AI Bio-Cyber Gateways: Physics-Informed Neuromorphic Transduction
and Autonomous Multi-Scale Coordination for IoBNT"

Usage:
    python run_all.py                # Run full reproduction pipeline (simulations + figure generation)
    python run_all.py --sim          # Run end-to-end MC channel & PINO benchmarks (Figs 1-5)
    python run_all.py --figures      # Generate architecture, contour, and protocol figures (Figs 6-13)
"""

import os
import sys
import argparse
import subprocess
import time


REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
SIM_DIR = os.path.join(REPO_ROOT, "simulation")
FIGURES_DIR = os.path.join(REPO_ROOT, "manuscript", "figures")


def print_banner():
    banner = r"""
================================================================================
     EMBODIED PHYSICAL AI BIO-CYBER GATEWAYS (EPA-BCG) REPRODUCTION SUITE
                 IEEE Trans. Mol. Biol. Multi-Scale Commun. (2027)
================================================================================
    """
    print(banner)


def check_python_dependencies():
    print("[*] Checking Python dependencies...")
    missing = []
    for pkg in ["numpy", "scipy", "matplotlib", "torch"]:
        try:
            __import__(pkg)
            print(f"  [+] {pkg}: OK")
        except ImportError:
            missing.append(pkg)
            print(f"  [-] {pkg}: MISSING")
    
    if missing:
        print(f"\n[!] Missing dependencies: {', '.join(missing)}")
        print("    Please run: pip install -r requirements.txt")
        return False
    return True


def run_benchmarks():
    print("\n" + "="*80)
    print("[1/2] RUNNING END-TO-END BENCHMARK SIMULATIONS (Figures 1 - 5)")
    print("="*80)
    t0 = time.time()
    cmd = [sys.executable, os.path.join(SIM_DIR, "run_simulation.py")]
    res = subprocess.run(cmd, cwd=SIM_DIR)
    if res.returncode != 0:
        print("[!] Error running simulation benchmarks.")
        return False
    print(f"[+] Benchmarks completed in {time.time() - t0:.2f} seconds.")
    return True


def run_figure_generators():
    print("\n" + "="*80)
    print("[2/2] GENERATING SYSTEM ARCHITECTURE & MULTI-SCALE FIGURES (Figures 6 - 13)")
    print("="*80)
    t0 = time.time()
    
    # 1. Figures 6 - 9
    print(">>> Executing generate_extra_visuals.py (Figs 6, 7, 8, 9)...")
    res1 = subprocess.run([sys.executable, os.path.join(SIM_DIR, "generate_extra_visuals.py")], cwd=SIM_DIR)
    if res1.returncode != 0:
        print("[!] Error generating extra visuals.")
        return False

    # 2. Figures 10 - 13
    print(">>> Executing generate_flagship_visuals.py (Figs 10, 11, 12, 13)...")
    res2 = subprocess.run([sys.executable, os.path.join(SIM_DIR, "generate_flagship_visuals.py")], cwd=SIM_DIR)
    if res2.returncode != 0:
        print("[!] Error generating flagship visuals.")
        return False

    print(f"[+] All publication figures generated in {time.time() - t0:.2f} seconds.")
    return True


def main():
    print_banner()
    parser = argparse.ArgumentParser(description="Reproduce Embodied Physical AI Bio-Cyber Gateway results.")
    parser.add_argument("--sim", action="store_true", help="Run simulation benchmarks (Figs 1-5)")
    parser.add_argument("--figures", action="store_true", help="Generate architecture & multi-scale figures (Figs 6-13)")
    parser.add_argument("--all", action="store_true", help="Run full pipeline: simulations and figure generation")
    
    args = parser.parse_args()
    run_all_default = not (args.sim or args.figures or args.all)

    if not check_python_dependencies():
        sys.exit(1)

    if args.sim or args.all or run_all_default:
        if not run_benchmarks():
            sys.exit(1)

    if args.figures or args.all or run_all_default:
        if not run_figure_generators():
            sys.exit(1)

    print("\n" + "="*80)
    print("[SUCCESS] ALL REPRODUCTION PIPELINE STAGES COMPLETED CLEANLY.")
    print(f"          Visuals stored in: {FIGURES_DIR}")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
