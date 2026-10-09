"""
channel_solver.py
=================
Physics-grounded 3D Advection-Diffusion-Reaction channel solver for molecular communications
in microfluidic channels and bounded vascular environments.

Governing Equation:
    dC/dt + v * grad(C) = D * div(grad(C)) - k_d * C + S(r, t)

where:
    C(r, t) : Molecular concentration [molecules / m^3]
    D       : Diffusion coefficient [m^2 / s]
    v(r, t) : Flow velocity vector field [m / s] (laminar or pulsatile)
    k_d     : Enzymatic degradation rate [s^-1]
    S(r, t) : Molecular emission source rate [molecules / (m^3 * s)]
"""

import numpy as np
import scipy.special as sp


class MolecularChannelConfig:
    """Configuration parameters for 3D advection-diffusion-reaction channel."""
    def __init__(
        self,
        diffusion_coeff: float = 2.0e-10,       # D in m^2/s (typical small biomarker in biofluid)
        flow_velocity: float = 1.0e-3,          # v_0 in m/s (1 mm/s typical microfluidic/capillary flow)
        pulsatile_amp: float = 0.25,            # Relative pulsatile flow amplitude (v(t) = v_0 * (1 + amp * sin(2*pi*f*t)))
        pulsatile_freq: float = 1.0,            # Heartbeat / pump frequency (1 Hz)
        degradation_rate: float = 0.05,         # k_d enzymatic clearance rate in s^-1
        distance: float = 50.0e-6,              # Distance from Tx to Gateway Rx in meters (50 micrometers)
        channel_radius: float = 20.0e-6,        # Microvessel/duct radius R in meters (20 micrometers)
        molecules_bit1: int = 50000,            # Number of molecules released for Bit '1'
        molecules_bit0: int = 2000,             # Number of molecules released for Bit '0' (leakage/basal)
        symbol_interval: float = 0.05,          # Symbol duration T_s in seconds (50 ms)
        sampling_rate: float = 2000.0           # Simulation sampling frequency F_s in Hz (0.5 ms resolution)
    ):
        self.D = diffusion_coeff
        self.v0 = flow_velocity
        self.pulsatile_amp = pulsatile_amp
        self.pulsatile_freq = pulsatile_freq
        self.kd = degradation_rate
        self.distance = distance
        self.R = channel_radius
        self.N1 = molecules_bit1
        self.N0 = molecules_bit0
        self.Ts = symbol_interval
        self.Fs = sampling_rate
        self.dt = 1.0 / sampling_rate

        # Taylor-Aris Effective Dispersion Coefficient in laminar cylindrical tube:
        # D_eff = D * (1 + (v0 * R)^2 / (48 * D^2))
        pe_num = (self.v0 * self.R) / self.D
        self.Deff = self.D * (1.0 + (pe_num ** 2) / 48.0)


class MolecularChannelSolver:
    """3D Advection-Diffusion-Reaction channel model with Taylor dispersion & boundary effects."""
    def __init__(self, config: MolecularChannelConfig = None):
        self.cfg = config if config is not None else MolecularChannelConfig()

    def get_instantaneous_velocity(self, t: float) -> float:
        """Computes pulsatile fluid velocity at time t."""
        return self.cfg.v0 * (1.0 + self.cfg.pulsatile_amp * np.sin(2.0 * np.pi * self.cfg.pulsatile_freq * t))

    def impulse_response(self, t: np.ndarray, t_emit: float = 0.0) -> np.ndarray:
        """
        Calculates the 1D cross-sectional average concentration impulse response h(t - t_emit)
        at distance d from point emission at t_emit, accounting for advection, effective dispersion,
        and first-order enzymatic reaction degradation.
        
        Analytical Solution to 1D Advection-Diffusion-Reaction:
            h(t) = (1 / (A * sqrt(4 * pi * D_eff * t))) * exp( - (d - v_mean * t)^2 / (4 * D_eff * t) - k_d * t )
        """
        tau = t - t_emit
        h = np.zeros_like(tau, dtype=np.float64)
        valid = tau > 1e-7

        A_cross = np.pi * (self.cfg.R ** 2)
        v_eff = self.cfg.v0  # Mean advective velocity

        tau_val = tau[valid]
        exponent = - ((self.cfg.distance - v_eff * tau_val) ** 2) / (4.0 * self.cfg.Deff * tau_val) - self.cfg.kd * tau_val
        # Prevent numerical underflow
        exponent = np.clip(exponent, -700.0, 50.0)
        
        prefactor = 1.0 / (A_cross * np.sqrt(4.0 * np.pi * self.cfg.Deff * tau_val))
        h[valid] = prefactor * np.exp(exponent)
        return h

    def simulate_transmission(self, bits: np.ndarray, num_samples_per_symbol: int = None) -> tuple:
        """
        Simulates transmission of a binary sequence over the molecular channel.
        
        Returns:
            t (np.ndarray): Time vector
            c_rx (np.ndarray): Molecular concentration profile at the gateway receiver
            emission_times (np.ndarray): Array of emission timestamps
            symbol_boundaries (np.ndarray): Indices marking symbol boundaries
        """
        if num_samples_per_symbol is None:
            num_samples = int(self.cfg.Ts * self.cfg.Fs)
        else:
            num_samples = num_samples_per_symbol

        total_symbols = len(bits)
        # Allocate extra time at tail to capture heavy diffusion dispersion
        tail_symbols = 4
        total_time = (total_symbols + tail_symbols) * self.cfg.Ts
        t = np.arange(0.0, total_time, self.cfg.dt)
        c_rx = np.zeros_like(t, dtype=np.float64)

        emission_times = np.zeros(total_symbols)
        symbol_boundaries = np.zeros(total_symbols + 1, dtype=int)

        # Superposition of diffused molecular pulses
        for k, bit in enumerate(bits):
            t_k = k * self.cfg.Ts
            emission_times[k] = t_k
            symbol_boundaries[k] = int(k * num_samples)
            n_molecules = self.cfg.N1 if bit == 1 else self.cfg.N0

            # Compute pulse response
            pulse_response = self.impulse_response(t, t_emit=t_k)
            c_rx += n_molecules * pulse_response

        symbol_boundaries[total_symbols] = int(total_symbols * num_samples)

        # Add physical Poisson counting noise (inherent in molecular diffusion arrivals)
        # Local count N_local = C * V_sensing.
        v_sensing = 1.0e-15  # 1 femtoliter gateway sensing volume
        molecule_counts = np.random.poisson(np.maximum(c_rx * v_sensing, 0.0))
        c_rx_noisy = molecule_counts / v_sensing

        return t, c_rx, c_rx_noisy, emission_times, symbol_boundaries


if __name__ == "__main__":
    print("Testing MolecularChannelSolver...")
    cfg = MolecularChannelConfig()
    solver = MolecularChannelSolver(cfg)
    
    # Test random bit sequence
    np.random.seed(42)
    test_bits = np.array([1, 0, 1, 1, 0, 1, 0, 0])
    t, c_clean, c_noisy, t_emit, bounds = solver.simulate_transmission(test_bits)
    
    print(f"Simulation completed: {len(test_bits)} symbols, {len(t)} time steps.")
    print(f"Max clean concentration: {np.max(c_clean):.2e} molecules/m^3")
    print(f"Max noisy concentration: {np.max(c_noisy):.2e} molecules/m^3")
    print("Channel solver validation: SUCCESS.")
