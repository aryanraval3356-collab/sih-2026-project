import numpy as np

# =============================================================================
# MULTI-MODE FUZE MECHANICS (STANAG 4369 COMPLIANT)
# =============================================================================
FUZE_MODES = {
    "⚡ FMCW Proximity Airburst (5.0m AGL)": {
        "height_agl_m": 5.0,
        "desc": "24 GHz FMCW radar triggers high-explosive burst 5.0m above ground. Ideal for soft targets, exposed personnel, and light vehicles.",
        "lethal_radius_m": 42.0,
        "fragment_count": 8500
    },
    "💥 Point Detonating (Impact Contact)": {
        "height_agl_m": 0.0,
        "desc": "Instantaneous piezoelectric impact detonation upon ground or armor contact. Maximum direct kinetic & blast overpressure payload.",
        "lethal_radius_m": 25.0,
        "fragment_count": 6200
    },
    "🛡️ Delay Penetration (15ms Post-Impact)": {
        "height_agl_m": -1.5,
        "desc": "Pyrotechnic 15ms delay allows 155mm shell to breach fortified concrete earthworks/bunkers before high-explosive initiation.",
        "lethal_radius_m": 18.0,
        "fragment_count": 4800
    }
}

def calculate_blast_footprint(fuze_mode_name, miss_distance_m):
    """
    Computes fragment overpressure density and target lethality probability vs miss distance.
    155mm M107 standard payload: 9.25 kg Comp B High Explosive.
    """
    mode_info = FUZE_MODES.get(fuze_mode_name, FUZE_MODES["💥 Point Detonating (Impact Contact)"])
    lethal_r = mode_info["lethal_radius_m"]
    
    # Overpressure scaling vs distance R (Kingery-Bulmash empirical fit for 9.25 kg HE)
    r_val = max(0.5, miss_distance_m)
    overpressure_psi = 14.7 * (1.2 + (5.4 / (r_val / 3.0)**2) + (1.8 / (r_val / 3.0)**3))
    
    # Target Kill Probability (Pk) using Sperrazza fragment lethality model
    pk = float(np.exp(- (r_val / lethal_r)**2)) * 100.0
    
    return {
        "lethal_radius_m": lethal_r,
        "fragment_count": mode_info["fragment_count"],
        "overpressure_psi": overpressure_psi,
        "kill_probability_pct": pk,
        "mode_desc": mode_info["desc"]
    }
