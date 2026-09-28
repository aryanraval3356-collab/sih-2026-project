import physics_engine as phys
import avionics_engine as avio
import sih_compliance as sih

print("Imports verified successfully!")

# Solve deterministic trajectory to get nominal range
nominal = phys.solve_deterministic(
    guided=False, v0=827.0, elev_deg=50.0, crosswind_surface=12.0, base_alt_m=0.0, target_x=0.0, target_y=0.0
)
nominal_range = nominal['y'][-1]

res = phys.solve_deterministic(
    guided=True, v0=827.0, elev_deg=50.0, crosswind_surface=12.0, base_alt_m=0.0, target_x=0.0, target_y=nominal_range
)

print(f"Trajectory solved! Steps: {len(res['t'])}, Impact Range: {res['y'][-1]:.1f}m, Max Altitude: {res['z'].max():.1f}m")

# Test Monte Carlo 50-launch batch matching reference dataset
mc = phys.run_monte_carlo(50, 827.0, 50.0, 12.0, 0.0, 0.0, nominal_range, seed=42)
print(f"Monte Carlo 50 Launches Completed!")
print(f"Unguided X Mean: {mc['ux'].mean():.2f}m, Std: {mc['ux'].std():.2f}m")
print(f"Unguided Y Mean: {mc['uy'].mean():.2f}m, Std: {mc['uy'].std():.2f}m")
print(f"Unguided CEP: {mc['cep_unguided']:.2f}m, Max Miss: {mc['miss_unguided'].max():.2f}m")

print(f"\nGuided X Mean: {mc['gx'].mean():.2f}m, Std: {mc['gx'].std():.2f}m")
print(f"Guided Y Mean: {mc['gy'].mean():.2f}m, Std: {mc['gy'].std():.2f}m")
print(f"Guided CEP: {mc['cep_guided']:.2f}m, Max Miss: {mc['miss_guided'].max():.2f}m")
