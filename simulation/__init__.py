"""
Embodied Physical AI Bio-Cyber Gateways (EPA-BCG) Simulation Package
=====================================================================
Modules:
- channel_solver: 3D Taylor-Aris advection-diffusion-reaction solver with pulsatile flow
- biofet_transduction: Bio-FET aptasensor interface with Markov ligand kinetics & LIF spikes
- pino_equalizer: Physics-Informed Neuromorphic Operator with PyTorch adjoint PDE loss
- run_simulation: End-to-end benchmark suite across 4 decoding schemes
- generate_extra_visuals: Generates Figures 6-9
- generate_flagship_visuals: Generates Figures 10-13
"""

from .channel_solver import MolecularChannelConfig, MolecularChannelSolver
from .biofet_transduction import BioFETConfig, NeuromorphicEncoderConfig, BioFETTransducer
from .pino_equalizer import PINOEqualizer

__all__ = [
    "MolecularChannelConfig",
    "MolecularChannelSolver",
    "BioFETConfig",
    "NeuromorphicEncoderConfig",
    "BioFETTransducer",
    "PINOEqualizer"
]
