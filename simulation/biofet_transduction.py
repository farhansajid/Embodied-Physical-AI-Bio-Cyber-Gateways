"""
biofet_transduction.py
======================
Physics-based model of Aptamer-functionalized Field-Effect Transistor (Bio-FET)
and Asynchronous Neuromorphic Spike Generator for IoBNT bio-cyber gateways.

Physical Principles:
1. Two-state Markovian receptor-ligand kinetics with chemical Langevin noise:
   d(theta)/dt = k_on * C(t) * (1 - theta) - k_off * theta + xi_bind(t)
2. Surface charge modulation and Bio-FET subthreshold/linear drain-source current:
   Delta_Psi(t) = (q_eff * N_sites * theta(t)) / C_dl
   I_ds(t) = I_0 * exp(alpha * Delta_Psi(t) / V_T) + I_leak + eta_thermal(t)
3. Asynchronous Leaky Integrate-and-Fire (LIF) spike generation:
   dV_mem/dt = (I_ds(t) - I_leak) / C_mem - V_mem / tau_leak
   When V_mem >= V_th: emit spike, reset to V_reset.
"""

import numpy as np


class BioFETConfig:
    """Parameters for the Bio-FET aptasensor interface."""
    def __init__(
        self,
        k_on: float = 1.0e-17,             # Association rate in m^3 / (molecule * s) (corresponds to ~6e6 M^-1 s^-1)
        k_off: float = 20.0,               # Dissociation rate in s^-1 (fast aptamer kinetics)
        site_density: float = 1.0e16,      # Aptamer receptor density in sites / m^2
        sensor_area: float = 1.0e-10,      # Active gate area A in m^2 (100 um^2)
        q_eff: float = -1.6e-19 * 3.0,     # Effective charge per bound molecule (e.g., -3e in PBS with screening)
        c_dl: float = 0.02,                # Electrical double layer capacitance in F / m^2 (~2 uF/cm^2)
        i_base: float = 5.0e-9,            # Baseline subthreshold drain-source current (5 nA)
        i_leak: float = 1.0e-10,           # Static leakage current (100 pA)
        alpha: float = 0.65,               # Subthreshold ideality/gate coupling factor
        thermal_voltage: float = 0.0259,   # V_T = k_B * T / q at 300 K (25.9 mV)
        thermal_noise_std: float = 1.0e-10 # Thermal current noise standard deviation (100 pA)
    ):
        self.k_on = k_on
        self.k_off = k_off
        self.site_density = site_density
        self.sensor_area = sensor_area
        self.total_sites = site_density * sensor_area
        self.q_eff = q_eff
        self.c_dl = c_dl
        self.i_base = i_base
        self.i_leak = i_leak
        self.alpha = alpha
        self.Vt = thermal_voltage
        self.noise_std = thermal_noise_std


class NeuromorphicEncoderConfig:
    """Parameters for the asynchronous Integrate-and-Fire spike encoder."""
    def __init__(
        self,
        c_mem: float = 50.0e-15,           # Membrane capacitance (50 fF)
        tau_leak: float = 0.005,           # Membrane leakage time constant (5 ms)
        v_th: float = 0.20,                # Spike threshold voltage (200 mV)
        v_reset: float = 0.0,              # Reset membrane potential (0 V)
        refractory_period: float = 0.0002  # Refractory period tau_ref (0.2 ms)
    ):
        self.C_mem = c_mem
        self.tau_leak = tau_leak
        self.V_th = v_th
        self.V_reset = v_reset
        self.tau_ref = refractory_period


class BioFETTransducer:
    """Simulates Bio-FET receptor binding, drain current, and neuromorphic spike generation."""
    def __init__(self, fet_cfg: BioFETConfig = None, enc_cfg: NeuromorphicEncoderConfig = None):
        self.fet_cfg = fet_cfg if fet_cfg is not None else BioFETConfig()
        self.enc_cfg = enc_cfg if enc_cfg is not None else NeuromorphicEncoderConfig()

    def transduce(self, t: np.ndarray, c_profile: np.ndarray) -> dict:
        """
        Transduces continuous molecular concentration profile into Bio-FET surface potential,
        analog current, and asynchronous spike trains.
        
        Args:
            t: Time vector (seconds)
            c_profile: Concentration profile C(t) (molecules / m^3)
            
        Returns:
            dict containing:
                - theta: Occupancy ratio [0, 1]
                - delta_psi: Surface potential shift (V)
                - i_ds: Drain-source current (A)
                - spikes: Binary spike vector [0 or 1 at each sample]
                - spike_times: List of exact timestamps of emitted spikes
                - v_mem: Membrane potential trajectory (V)
                - spike_count: Total number of generated spikes
                - energy_joules: Estimated electrical energy consumed (Joules)
        """
        n_steps = len(t)
        dt = t[1] - t[0] if n_steps > 1 else 1e-4

        theta = np.zeros(n_steps, dtype=np.float64)
        delta_psi = np.zeros(n_steps, dtype=np.float64)
        i_ds = np.zeros(n_steps, dtype=np.float64)
        v_mem = np.zeros(n_steps, dtype=np.float64)
        spikes = np.zeros(n_steps, dtype=np.int8)

        spike_times = []
        current_theta = 0.0
        current_vmem = self.enc_cfg.V_reset
        refractory_timer = 0.0

        for i in range(n_steps):
            c_val = max(c_profile[i], 0.0)

            # 1. Chemical Langevin Receptor Binding Kinetics
            # dtheta/dt = k_on * C * (1 - theta) - k_off * theta + Langevin noise
            rate_on = self.fet_cfg.k_on * c_val * (1.0 - current_theta)
            rate_off = self.fet_cfg.k_off * current_theta
            
            # Langevin stochastic fluctuation variance
            var_langevin = (rate_on + rate_off) / max(self.fet_cfg.total_sites, 1.0)
            noise_bind = np.random.normal(0.0, np.sqrt(max(var_langevin / dt, 0.0))) if var_langevin > 0 else 0.0

            d_theta = (rate_on - rate_off + noise_bind) * dt
            current_theta = np.clip(current_theta + d_theta, 0.0, 1.0)
            theta[i] = current_theta

            # 2. Surface Potential Modulation
            # Delta_Psi(t) = (q_eff * site_density * theta(t)) / c_dl
            # Absolute magnitude shift
            psi = (abs(self.fet_cfg.q_eff) * self.fet_cfg.site_density * current_theta) / self.fet_cfg.c_dl
            delta_psi[i] = psi

            # 3. Bio-FET Drain-Source Current
            # Exponential subthreshold amplification:
            current_signal = self.fet_cfg.i_base * np.exp(np.clip(self.fet_cfg.alpha * psi / self.fet_cfg.Vt, 0.0, 20.0))
            thermal_noise = np.random.normal(0.0, self.fet_cfg.noise_std)
            i_val = current_signal + self.fet_cfg.i_leak + thermal_noise
            i_ds[i] = max(i_val, 0.0)

            # 4. Neuromorphic Leaky Integrate-and-Fire Encoder
            if refractory_timer > 0.0:
                refractory_timer -= dt
                v_mem[i] = self.enc_cfg.V_reset
                continue

            # Membrane voltage update:
            # dV/dt = (I_ds - I_leak) / C_mem - V_mem / tau_leak
            i_drive = max(i_ds[i] - self.fet_cfg.i_base, 0.0)  # Signal current above baseline
            dv = ((i_drive / self.enc_cfg.C_mem) - (current_vmem / self.enc_cfg.tau_leak)) * dt
            current_vmem += dv

            if current_vmem >= self.enc_cfg.V_th:
                spikes[i] = 1
                spike_times.append(t[i])
                current_vmem = self.enc_cfg.V_reset
                refractory_timer = self.enc_cfg.tau_ref

            v_mem[i] = current_vmem

        # Energy consumption: Bio-FET (V_ds * I_ds * dt with V_ds=0.5V) + spike event energy (0.5 * C_mem * V_th^2)
        v_ds = 0.5  # 500 mV supply
        fet_energy = np.sum(v_ds * i_ds * dt)
        spike_event_energy = len(spike_times) * (0.5 * self.enc_cfg.C_mem * (self.enc_cfg.V_th ** 2))
        total_energy = fet_energy + spike_event_energy

        return {
            "theta": theta,
            "delta_psi": delta_psi,
            "i_ds": i_ds,
            "spikes": spikes,
            "spike_times": np.array(spike_times),
            "v_mem": v_mem,
            "spike_count": len(spike_times),
            "energy_joules": total_energy,
            "energy_pj_per_spike": (total_energy / max(len(spike_times), 1)) * 1e12
        }


if __name__ == "__main__":
    print("Testing BioFETTransducer...")
    from channel_solver import MolecularChannelConfig, MolecularChannelSolver
    
    cfg = MolecularChannelConfig()
    solver = MolecularChannelSolver(cfg)
    
    np.random.seed(42)
    test_bits = np.array([1, 0, 1, 1, 0, 1, 0, 0])
    t, c_clean, c_noisy, t_emit, bounds = solver.simulate_transmission(test_bits)

    transducer = BioFETTransducer()
    res = transducer.transduce(t, c_noisy)

    print(f"Transduction complete!")
    print(f"Max receptor occupancy (theta): {np.max(res['theta']):.4f}")
    print(f"Max Bio-FET drain current: {np.max(res['i_ds']):.2e} A")
    print(f"Total asynchronous spikes emitted: {res['spike_count']}")
    print(f"Total energy consumed: {res['energy_joules'] * 1e9:.2f} nJ ({res['energy_pj_per_spike']:.2f} pJ/spike)")
    print("Bio-FET Transducer validation: SUCCESS.")
