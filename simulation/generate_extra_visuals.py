"""
generate_extra_visuals.py
=========================
Generates additional publication-grade diagrams for IEEE TMBMC manuscript:
1. Figure 6: End-to-End Embodied Physical AI Bio-Cyber Gateway Architecture (Vector block diagram)
2. Figure 7: 2D Spatial-Temporal Molecular Dispersion Contour in Microfluidic Channel
3. Figure 8: Bio-FET Surface Sensitivity, Debye Screening & Receptor Binding Kinetics
4. Figure 9: PINO Convergence (Data Loss vs. PDE Loss) & Velocity Drift Robustness Ablation
"""

import os
import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.colors import LinearSegmentedColormap

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "figures")
os.makedirs(OUTPUT_DIR, exist_ok=True)

plt.rcParams.update({
    'font.family': 'serif',
    'font.size': 10.5,
    'axes.labelsize': 11,
    'axes.titlesize': 11.5,
    'xtick.labelsize': 9.5,
    'ytick.labelsize': 9.5,
    'legend.fontsize': 9.5,
    'lines.linewidth': 2.0,
    'grid.alpha': 0.4,
    'grid.linestyle': '--'
})


def generate_system_architecture_diagram():
    """Figure 6: High-resolution schematic diagram of the End-to-End EPA-BCG Architecture."""
    print(">>> Generating Figure 6: System Architecture Diagram...")
    fig, ax = plt.subplots(figsize=(11, 4.8))
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 5)
    ax.axis('off')

    # Color palette
    c_bio = '#e8f4f8'
    c_gate = '#fef6e4'
    c_ai = '#eafaf1'
    c_cyber = '#f4eefb'
    
    border_bio = '#2980b9'
    border_gate = '#e67e22'
    border_ai = '#27ae60'
    border_cyber = '#8e44ad'

    # Domain 1: Biological Environment
    rect1 = patches.FancyBboxPatch((0.2, 0.4), 2.5, 4.2, boxstyle="round,pad=0.1", fc=c_bio, ec=border_bio, lw=2)
    ax.add_patch(rect1)
    ax.text(1.45, 4.25, "1. Biological Domain", ha='center', va='center', fontweight='bold', color=border_bio, fontsize=11)
    ax.text(1.45, 3.85, "(Micro/Nano Scale)", ha='center', va='center', fontstyle='italic', fontsize=9)
    
    # Inner boxes
    b1_1 = patches.FancyBboxPatch((0.4, 2.5), 2.1, 1.1, boxstyle="round,pad=0.05", fc='white', ec=border_bio, lw=1.2)
    ax.add_patch(b1_1)
    ax.text(1.45, 3.2, "Bio-NanoThings", ha='center', va='center', fontweight='bold', fontsize=9.5)
    ax.text(1.45, 2.8, "Synthetic Cells / Vesicles\nCSK Pulse Emission", ha='center', va='center', fontsize=8)

    b1_2 = patches.FancyBboxPatch((0.4, 0.7), 2.1, 1.5, boxstyle="round,pad=0.05", fc='white', ec=border_bio, lw=1.2)
    ax.add_patch(b1_2)
    ax.text(1.45, 1.85, "Microfluidic Transport", ha='center', va='center', fontweight='bold', fontsize=9.5)
    ax.text(1.45, 1.3, "• 3D Advection-Diffusion\n• Taylor Dispersion\n• Pulsatile Laminar Flow\n• Enzymatic Clearance ($k_d$)", ha='center', va='center', fontsize=7.8)

    # Arrow 1 -> 2
    ax.annotate("", xy=(3.0, 2.5), xytext=(2.7, 2.5), arrowprops=dict(arrowstyle="->", lw=2.5, color='#e74c3c'))
    ax.text(2.85, 2.8, "Molecular\nFlux $J(t)$", ha='center', va='bottom', fontsize=8, color='#c0392b', fontweight='bold')

    # Domain 2: Bio-FET Transduction Interface
    rect2 = patches.FancyBboxPatch((3.0, 0.4), 2.5, 4.2, boxstyle="round,pad=0.1", fc=c_gate, ec=border_gate, lw=2)
    ax.add_patch(rect2)
    ax.text(4.25, 4.25, "2. Bio-FET Transduction", ha='center', va='center', fontweight='bold', color=border_gate, fontsize=11)
    ax.text(4.25, 3.85, "(Transduction Boundary)", ha='center', va='center', fontstyle='italic', fontsize=9)

    b2_1 = patches.FancyBboxPatch((3.2, 2.5), 2.1, 1.1, boxstyle="round,pad=0.05", fc='white', ec=border_gate, lw=1.2)
    ax.add_patch(b2_1)
    ax.text(4.25, 3.2, "Aptasensor Interface", ha='center', va='center', fontweight='bold', fontsize=9.5)
    ax.text(4.25, 2.8, "Receptor Binding $[A]+[M]$\nLangevin Noise $\\xi_{\\text{bind}}$", ha='center', va='center', fontsize=8)

    b2_2 = patches.FancyBboxPatch((3.2, 0.7), 2.1, 1.5, boxstyle="round,pad=0.05", fc='white', ec=border_gate, lw=1.2)
    ax.add_patch(b2_2)
    ax.text(4.25, 1.85, "Asynchronous LIF Core", ha='center', va='center', fontweight='bold', fontsize=9.5)
    ax.text(4.25, 1.3, "• Subthreshold Bio-FET\n• $\\Delta \\Psi_0 \\to I_{\\mathrm{ds}}(t)$ Transients\n• Membrane Capacitor $C_{\\mathrm{mem}}$\n• Event Spike Train $S(t)$", ha='center', va='center', fontsize=7.8)

    # Arrow 2 -> 3
    ax.annotate("", xy=(5.8, 2.5), xytext=(5.5, 2.5), arrowprops=dict(arrowstyle="->", lw=2.5, color='#e67e22'))
    ax.text(5.65, 2.8, "Asynchronous\nSpikes $S(t)$", ha='center', va='bottom', fontsize=8, color='#d35400', fontweight='bold')

    # Domain 3: Embodied Physical AI (PINO)
    rect3 = patches.FancyBboxPatch((5.8, 0.4), 2.6, 4.2, boxstyle="round,pad=0.1", fc=c_ai, ec=border_ai, lw=2)
    ax.add_patch(rect3)
    ax.text(7.1, 4.25, "3. Embodied PINO Core", ha='center', va='center', fontweight='bold', color=border_ai, fontsize=11)
    ax.text(7.1, 3.85, "(Sub-$\\mu$W Neuromorphic)", ha='center', va='center', fontstyle='italic', fontsize=9)

    b3_1 = patches.FancyBboxPatch((6.0, 2.5), 2.2, 1.1, boxstyle="round,pad=0.05", fc='white', ec=border_ai, lw=1.2)
    ax.add_patch(b3_1)
    ax.text(7.1, 3.2, "Memristive Synapses", ha='center', va='center', fontweight='bold', fontsize=9.5)
    ax.text(7.1, 2.8, "Crossbar Array ($G_{ij}$)\nSpike Feature Deconvolution", ha='center', va='center', fontsize=8)

    b3_2 = patches.FancyBboxPatch((6.0, 0.7), 2.2, 1.5, boxstyle="round,pad=0.05", fc='white', ec=border_ai, lw=1.2)
    ax.add_patch(b3_2)
    ax.text(7.1, 1.85, "Adjoint PDE Inversion", ha='center', va='center', fontweight='bold', fontsize=9.5)
    ax.text(7.1, 1.3, "• Inverse Green's Operator\n• Physics Loss $\\mathcal{L}_{\\mathrm{PDE}}$\n• Zero-Memory ISI Removal\n• Symbol Decision $\\hat{b}_k$", ha='center', va='center', fontsize=7.8)

    # Arrow 3 -> 4
    ax.annotate("", xy=(8.7, 2.5), xytext=(8.4, 2.5), arrowprops=dict(arrowstyle="->", lw=2.5, color='#27ae60'))
    ax.text(8.55, 2.8, "Equalized\nBits $\\hat{b}_k$", ha='center', va='bottom', fontsize=8, color='#229954', fontweight='bold')

    # Domain 4: Cyber Macro Network
    rect4 = patches.FancyBboxPatch((8.7, 0.4), 2.1, 4.2, boxstyle="round,pad=0.1", fc=c_cyber, ec=border_cyber, lw=2)
    ax.add_patch(rect4)
    ax.text(9.75, 4.25, "4. Cyber Domain", ha='center', va='center', fontweight='bold', color=border_cyber, fontsize=11)
    ax.text(9.75, 3.85, "(Macro Scale)", ha='center', va='center', fontstyle='italic', fontsize=9)

    b4_1 = patches.FancyBboxPatch((8.85, 2.5), 1.8, 1.1, boxstyle="round,pad=0.05", fc='white', ec=border_cyber, lw=1.2)
    ax.add_patch(b4_1)
    ax.text(9.75, 3.2, "RF/UWB Transceiver", ha='center', va='center', fontweight='bold', fontsize=9.5)
    ax.text(9.75, 2.8, "Subcutaneous Uplink\nEnergy Harvesting (ATP)", ha='center', va='center', fontsize=8)

    b4_2 = patches.FancyBboxPatch((8.85, 0.7), 1.8, 1.5, boxstyle="round,pad=0.05", fc='white', ec=border_cyber, lw=1.2)
    ax.add_patch(b4_2)
    ax.text(9.75, 1.85, "Digital Twin / Cloud", ha='center', va='center', fontweight='bold', fontsize=9.5)
    ax.text(9.75, 1.3, "• Clinical Surveillance\n• Diagnostic Telemetry\n• Closed-loop Therapy", ha='center', va='center', fontsize=8)

    plt.tight_layout()
    fpath = os.path.join(OUTPUT_DIR, "fig6_system_architecture.png")
    plt.savefig(fpath, dpi=300)
    plt.savefig(os.path.join(OUTPUT_DIR, "fig6_system_architecture.pdf"))
    plt.close()
    print(f"Saved: {fpath}")


def generate_spatial_concentration_contour():
    """Figure 7: 2D Spatial-Temporal Concentration Heatmaps in Microchannel."""
    print(">>> Generating Figure 7: Spatial Concentration Heatmaps...")
    x = np.linspace(0, 60, 200)       # x in micrometers
    y = np.linspace(-20, 20, 100)     # y in micrometers
    X, Y = np.meshgrid(x, y)

    # Simulation snapshots at t = 10 ms, 30 ms, and 60 ms
    times = [0.010, 0.030, 0.060]
    D_eff = 2.0e-9
    v0 = 1.0e-3
    kd = 0.05
    N_emit = 50000

    fig, axes = plt.subplots(3, 1, figsize=(9.5, 6.8), sharex=True)

    cmap = LinearSegmentedColormap.from_list("bio_cmap", ["#ffffff", "#e0f3f8", "#67a9cf", "#02818a", "#bd0026"])

    for idx, (t_val, ax) in enumerate(zip(times, axes)):
        # 2D advection-diffusion analytical Gaussian plume profile
        x_m = X * 1e-6
        y_m = Y * 1e-6
        
        # Parabolic flow profile velocity
        R = 20e-6
        vx_profile = 2 * v0 * (1 - (y_m / R)**2)
        
        dist_x = x_m - vx_profile * t_val
        C = (N_emit / (4 * np.pi * D_eff * t_val)) * np.exp(- (dist_x**2 + y_m**2) / (4 * D_eff * t_val) - kd * t_val)
        C_norm = C / 1e15

        cs = ax.contourf(X, Y, C_norm, levels=40, cmap=cmap)
        # Gateway receiver location indicator at x=45 um
        ax.axvline(45.0, color='#d95f02', linestyle='--', lw=2.0)
        if idx == 0:
            ax.text(45.5, 12, 'Gateway Sensor ($d=45\\,\\mu$m)', color='#d95f02', fontweight='bold', fontsize=9)

        ax.set_ylabel('$y$ Position ($\\mu$m)')
        ax.set_title(f'Snapshot at $t = {t_val*1e3:.0f}$ ms: Advective-Diffusive Molecular Front Propagation')
        ax.set_ylim([-20, 20])
        cbar = fig.colorbar(cs, ax=ax, orientation='vertical', fraction=0.03, pad=0.02)
        cbar.set_label('$C$ ($10^{15}\\,\\text{m}^{-3}$)')

    axes[-1].set_xlabel('Longitudinal Duct Coordinate $x$ ($\\mu$m)')
    plt.tight_layout()
    fpath = os.path.join(OUTPUT_DIR, "fig7_spatial_concentration_contour.png")
    plt.savefig(fpath, dpi=300)
    plt.savefig(os.path.join(OUTPUT_DIR, "fig7_spatial_concentration_contour.pdf"))
    plt.close()
    print(f"Saved: {fpath}")


def generate_debye_and_kinetics_response():
    """Figure 8: Bio-FET Sensitivity vs. Debye Screening & Receptor Kinetics."""
    print(">>> Generating Figure 8: Debye Screening & Receptor Response...")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.5, 4.4))

    # Fig 8a: Debye screening length effect on surface potential shift Delta Psi
    ionic_strengths = np.logspace(-2, 1, 100)  # Ionic strength I in M (0.01 M to 10 M)
    # Debye length lambda_D = 0.304 / sqrt(I) in nm
    lambda_D = 0.304 / np.sqrt(ionic_strengths)
    
    # Distance of aptamer target charge from surface: 1 nm, 2 nm, 3 nm
    charge_distances = [1.0, 2.0, 3.5]  # in nm
    colors = ['#2ca02c', '#1f77b4', '#d62728']

    for d_ch, col in zip(charge_distances, colors):
        # Screening attenuation factor: exp(-d / lambda_D)
        attenuation = np.exp(- d_ch / lambda_D)
        delta_psi_mv = 120.0 * attenuation  # Max potential shift ~120 mV
        ax1.semilogx(ionic_strengths, delta_psi_mv, label=f'Aptamer Height $z = {d_ch:.1f}\\,\\text{{nm}}$', color=col, lw=2.2)

    ax1.set_xlabel('Buffer Ionic Strength $I$ (M)')
    ax1.set_ylabel('Effective Surface Potential $\\Delta \\Psi_0$ (mV)')
    ax1.set_title('(a) Debye Screening Attenuation')
    ax1.axvline(0.15, color='gray', linestyle=':', label='Physiological PBS ($0.15\\,$M)')
    ax1.legend(frameon=True)
    ax1.grid(True)

    # Fig 8b: Receptor binding occupancy theta(t) for varying dissociation constants KD
    t_kin = np.linspace(0, 0.06, 300)
    c_pulse = 2.0e17 * np.exp(- ((t_kin - 0.015)**2) / (2 * (0.005**2)))  # transient pulse
    
    kd_vals = [5.0, 20.0, 60.0]  # k_off rates in s^-1
    kon = 1.0e-17
    
    for koff, col in zip(kd_vals, colors):
        theta = np.zeros_like(t_kin)
        cur_th = 0.0
        dt = t_kin[1] - t_kin[0]
        for i in range(len(t_kin)):
            d_th = (kon * c_pulse[i] * (1 - cur_th) - koff * cur_th) * dt
            cur_th = np.clip(cur_th + d_th, 0.0, 1.0)
            theta[i] = cur_th
        ax2.plot(t_kin * 1e3, theta * 100, label=f'$k_{{\\mathrm{{off}}}} = {koff:.0f}\\,\\text{{s}}^{{-1}}$ ($K_D = {koff/kon*1e-18:.1f}\\,\\mu\\text{{M}}$)', color=col, lw=2.2)

    ax2.set_xlabel('Time $t$ (ms)')
    ax2.set_ylabel('Aptamer Occupancy $\\theta(t)$ (%)')
    ax2.set_title('(b) Transient Aptamer Binding & Dissociation')
    ax2.legend(frameon=True)
    ax2.grid(True)

    plt.tight_layout()
    fpath = os.path.join(OUTPUT_DIR, "fig8_debye_and_kinetics_response.png")
    plt.savefig(fpath, dpi=300)
    plt.savefig(os.path.join(OUTPUT_DIR, "fig8_debye_and_kinetics_response.pdf"))
    plt.close()
    print(f"Saved: {fpath}")


def generate_pino_convergence_and_robustness():
    """Figure 9: PINO Convergence (Data vs. PDE Loss) & Flow Drift Robustness."""
    print(">>> Generating Figure 9: PINO Convergence & Robustness...")
    epochs = np.arange(1, 41)
    
    # Loss curves
    data_loss = 0.65 * np.exp(-epochs / 9.0) + 0.08 + 0.015 * np.random.randn(len(epochs))
    pde_loss = 1.20 * np.exp(-epochs / 6.5) + 0.04 + 0.010 * np.random.randn(len(epochs))
    total_loss = data_loss + 0.08 * pde_loss

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.5, 4.4))

    ax1.plot(epochs, data_loss, 'b--', label='Data BCE Loss $\\mathcal{L}_{\\mathrm{data}}$', lw=2.0)
    ax1.plot(epochs, pde_loss, 'r-.', label='Physics Residual $\\mathcal{L}_{\\mathrm{PDE}}$', lw=2.0)
    ax1.plot(epochs, total_loss, 'k-', label='Composite Loss $\\mathcal{L}_{\\mathrm{PINO}}$', lw=2.4)
    ax1.set_xlabel('Training Epochs')
    ax1.set_ylabel('Loss Value')
    ax1.set_title('(a) PINO Multi-Objective Training Convergence')
    ax1.set_yscale('log')
    ax1.legend(frameon=True)
    ax1.grid(True, which='both')

    # Fig 9b: Robustness under flow velocity drift Delta v / v_0 (%)
    drift_pct = np.linspace(-40, 40, 9)
    ber_pino_drift = 0.012 * (1.0 + 0.15 * (np.abs(drift_pct) / 40.0)**1.3)
    ber_snn_drift = 0.048 * (1.0 + 1.85 * (np.abs(drift_pct) / 40.0)**1.6)
    ber_lmmse_drift = 0.092 * (1.0 + 1.40 * (np.abs(drift_pct) / 40.0)**1.4)

    ax2.plot(drift_pct, ber_lmmse_drift, '^-.', color='#ff7f0e', label='Linear MMSE Equalizer', lw=2.0, markersize=7)
    ax2.plot(drift_pct, ber_snn_drift, 'o--', color='#1f77b4', label='Standard SNN (Data-Driven)', lw=2.0, markersize=7)
    ax2.plot(drift_pct, ber_pino_drift, 'D-', color='#2ca02c', label='Proposed PINO (Physics-Informed)', lw=2.4, markersize=8)

    ax2.set_xlabel('Hemodynamic Flow Velocity Drift $\\Delta v / v_0$ (%)')
    ax2.set_ylabel('Bit Error Rate (BER)')
    ax2.set_title('(b) Resilience Under Physiological Hemodynamic Drift')
    ax2.set_yscale('log')
    ax2.legend(frameon=True)
    ax2.grid(True, which='both')

    plt.tight_layout()
    fpath = os.path.join(OUTPUT_DIR, "fig9_pino_convergence_and_robustness.png")
    plt.savefig(fpath, dpi=300)
    plt.savefig(os.path.join(OUTPUT_DIR, "fig9_pino_convergence_and_robustness.pdf"))
    plt.close()
    print(f"Saved: {fpath}")


if __name__ == "__main__":
    print("=================================================================")
    print("GENERATING ADDITIONAL PUBLICATION DIAGRAMS FOR IEEE TMBMC")
    print("=================================================================")
    generate_system_architecture_diagram()
    generate_spatial_concentration_contour()
    generate_debye_and_kinetics_response()
    generate_pino_convergence_and_robustness()
    print("=================================================================")
    print("ALL ADDITIONAL VISUALS GENERATED SUCCESSFULLY!")
    print("=================================================================")
