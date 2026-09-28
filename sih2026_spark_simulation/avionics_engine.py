import numpy as np

# =============================================================================
# NAVIC (IRNSS) CONSTELLATION SIMULATOR
# Indian Regional Navigation Satellite System: 7 Satellites (3 GEO + 4 GSO)
# =============================================================================
NAVIC_SATELLITES = [
    {"name": "IRNSS-1A (GSO 55°E)", "azimuth": 215.4, "elevation": 62.1, "snr": 44.2, "status": "L5/S Operational"},
    {"name": "IRNSS-1B (GSO 55°E)", "azimuth": 222.1, "elevation": 59.8, "snr": 43.8, "status": "L5/S Operational"},
    {"name": "IRNSS-1C (GEO 83°E)", "azimuth": 145.2, "elevation": 71.4, "snr": 46.5, "status": "L5/S Operational"},
    {"name": "IRNSS-1D (GSO 111.75°E)", "azimuth": 105.8, "elevation": 52.3, "snr": 42.1, "status": "L5/S Operational"},
    {"name": "IRNSS-1E (GSO 111.75°E)", "azimuth": 112.3, "elevation": 54.0, "snr": 43.0, "status": "L5/S Operational"},
    {"name": "IRNSS-1F (GEO 32.5°E)", "azimuth": 258.9, "elevation": 45.6, "snr": 41.5, "status": "L5/S Operational"},
    {"name": "IRNSS-1I (GSO 83°E)", "azimuth": 152.0, "elevation": 73.1, "snr": 47.0, "status": "L5/S Operational"},
]

def get_navic_constellation_metrics():
    """Returns synthetic NavIC constellation telemetry summary."""
    n_visible = len(NAVIC_SATELLITES)
    mean_snr = float(np.mean([s["snr"] for s in NAVIC_SATELLITES]))
    hdop = 1.12  # Horizontal Dilution of Precision
    vdop = 1.45  # Vertical Dilution of Precision
    return {
        "visible_satellites": n_visible,
        "mean_snr_dbhz": mean_snr,
        "hdop": hdop,
        "vdop": vdop,
        "constellation_status": "L5 / S Dual-Band Operational (Anti-Jam Active)"
    }

# =============================================================================
# 16-STATE ERROR-STATE EKF & EW JAMMING SIMULATOR
# =============================================================================
def simulate_ekf_telemetry(t_arr, z_arr, jamming_active=False, jam_start_s=30.0, jam_duration_s=20.0):
    """
    Simulates 16-State Error-State Extended Kalman Filter (ES-EKF) telemetry.
    Tracks estimated position error, 1-sigma, and 3-sigma covariance bounds.
    """
    n_pts = len(t_arr)
    true_error_x = np.zeros(n_pts)
    sigma_1 = np.zeros(n_pts)
    sigma_3 = np.zeros(n_pts)
    nav_status = []
    
    jam_end_s = jam_start_s + jam_duration_s
    
    # EKF Covariance propagation loop
    curr_sigma = 0.5  # Initial alignment uncertainty (m)
    
    for i in range(n_pts):
        t = t_arr[i]
        z = z_arr[i]
        
        if t <= 6.0:
            # Stage 1: High-G setback blackout (0-6s)
            # Satellite signal lost due to plasma shock, IMU dead-reckoning only
            curr_sigma += 0.35 * (t_arr[1] - t_arr[0]) if i > 0 else 0.0
            status = "IMU_BLACKOUT"
            err_val = np.sin(t * 1.5) * curr_sigma * 0.4
        elif jamming_active and (jam_start_s <= t <= jam_end_s):
            # Stage 2: EW Jamming Window (Signals denied by hostile EW)
            curr_sigma += 0.28 * (t_arr[i] - t_arr[i-1]) if i > 0 else 0.0
            status = "EW_JAMMING_ACTIVE"
            err_val = np.cos(t * 0.8) * curr_sigma * 0.6
        else:
            # Stage 3: NavIC Satellite Measurement Update (Kalman Gain converges)
            # Re-acquisition collapses error covariance down to < 1.2m
            target_sigma = 0.85
            curr_sigma = curr_sigma * 0.88 + target_sigma * 0.12
            status = "NAVIC_L5_LOCK"
            err_val = np.sin(t * 2.0) * curr_sigma * 0.25
            
        sigma_1[i] = curr_sigma
        sigma_3[i] = curr_sigma * 3.0
        true_error_x[i] = err_val
        nav_status.append(status)

    return {
        "t": t_arr,
        "est_error_x": true_error_x,
        "sigma_1": sigma_1,
        "sigma_3": sigma_3,
        "nav_status": nav_status
    }
