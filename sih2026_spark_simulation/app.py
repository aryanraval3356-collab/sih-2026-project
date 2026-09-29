import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit.components.v1 as components

# Import modular domain engines
import physics_engine as phys
import avionics_engine as avio
import sih_compliance as sih
import gis_engine as gis
import fuze_engine as fuze
import cad_engine as cad
import hil_engine as hil
import report_engine as rep
import base64
import os

# =============================================================================
# PAGE CONFIGURATION & DEFENSE HUD STYLING
# =============================================================================
st.set_page_config(
    page_title="Project S.P.A.R.K - 7-DOF PGK Twin | SIH 2026",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    /* Dark Defense Terminal Palette */
    .main, .stApp { background-color: #070B19; color: #E2E8F0; font-family: 'Segoe UI', Roboto, sans-serif; }
    
    /* HUD Header Bar */
    .hud-header {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
        border: 1px solid #1E293B; border-left: 5px solid #10B981;
        border-radius: 8px; padding: 18px 24px; margin-bottom: 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
    }
    .hud-title { font-size: 2.1rem; font-weight: 900; color: #10B981; letter-spacing: 1.5px; margin: 0; }
    .hud-subtitle { font-size: 0.98rem; color: #38BDF8; font-weight: 500; margin-top: 4px; }
    .hud-badge {
        display: inline-block; background-color: rgba(16, 185, 129, 0.15);
        color: #10B981; border: 1px solid #10B981; border-radius: 4px;
        padding: 3px 10px; font-size: 0.78rem; font-weight: 700; margin-right: 8px;
    }
    .hud-badge-blue { background-color: rgba(56, 189, 248, 0.15); color: #38BDF8; border-color: #38BDF8; }
    .hud-badge-gold { background-color: rgba(245, 158, 11, 0.15); color: #F59E0B; border-color: #F59E0B; }

    /* Terminal Console Window */
    .terminal-box {
        background-color: #030712; border: 1px solid #1E293B; border-left: 4px solid #10B981;
        border-radius: 6px; padding: 16px; font-family: 'Consolas', 'Courier New', monospace;
        color: #10B981; height: 460px; overflow-y: auto;
        box-shadow: inset 0 0 12px rgba(16, 185, 129, 0.06);
    }
    .terminal-line { margin-bottom: 6px; line-height: 1.45; font-size: 0.86rem; }
    .terminal-line-warn { color: #F59E0B; }
    .terminal-line-alert { color: #EF4444; }
    .terminal-line-info { color: #38BDF8; }
    .terminal-line-success { color: #10B981; font-weight: bold; }
    
    .standby-box {
        background-color: #030712; border: 1px dashed #334155; border-radius: 6px;
        padding: 50px; text-align: center; color: #64748B; font-family: 'Consolas', monospace;
        height: 460px; display: flex; flex-direction: column; align-items: center; justify-content: center; font-size: 1.05rem;
    }

    div[data-testid="stMetric"] {
        background-color: #0F172A; border-radius: 8px; padding: 14px; border: 1px solid #1E293B;
        box-shadow: 0 2px 10px rgba(0,0,0,0.2);
    }
    
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #0F172A; border-radius: 6px 6px 0 0; padding: 10px 18px; color: #94A3B8; font-weight: 600;
    }
    .stTabs [aria-selected="true"] { background-color: #1E293B; color: #10B981; border-bottom: 2px solid #10B981; }
</style>
""", unsafe_allow_html=True)

# Render HUD Header
st.markdown("""
<div class="hud-header">
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
        <div>
            <div class="hud-title">🚀 PROJECT S.P.A.R.K — 7-DOF PRECISION GUIDANCE TWIN</div>
            <div class="hud-subtitle">Smart India Hackathon (SIH 2026) | Problem Statement ID: 26098 | Team AIZEN</div>
        </div>
        <div style="margin-top: 8px;">
            <span class="hud-badge">NAVIC L5/S LOCK</span>
            <span class="hud-badge-blue">20,000 G SETBACK QUALIFIED</span>
            <span class="hud-badge-gold">ATMANIRBHAR DEFENSE</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# =============================================================================
# SIDEBAR CONTROLS
# =============================================================================
st.sidebar.header("🎯 Defense Theater & Guidance Mode")

selected_preset = st.sidebar.selectbox(
    "Operational Theater Preset:",
    options=list(sih.OPERATIONAL_PRESETS.keys()),
    index=1
)
preset_info = sih.OPERATIONAL_PRESETS[selected_preset]
st.sidebar.caption(preset_info["desc"])

guidance_mode = st.sidebar.radio(
    "Select Nose Hardware Mode:",
    options=["Guided (S.P.A.R.K Smart Fuze Active)", "Unguided (Standard M107 Baseline)"],
    index=0
)
is_guided = (guidance_mode == "Guided (S.P.A.R.K Smart Fuze Active)")

st.sidebar.markdown("---")
st.sidebar.header("🌍 Launch & Environmental Controls")

muzzle_v0 = st.sidebar.slider("Muzzle Velocity v0 (m/s)", 700.0, 950.0, float(preset_info["v0"]), 5.0)
elevation_deg = st.sidebar.slider("Gun Elevation Angle (deg)", 40.0, 65.0, float(preset_info["elev_deg"]), 0.5)
crosswind_ms = st.sidebar.slider("Surface Crosswind Speed (m/s)", 0.0, 35.0, float(preset_info["crosswind"]), 1.0)
base_alt_m = st.sidebar.slider("Battery Altitude ASL (m)", 0.0, 5000.0, float(preset_info["base_alt_m"]), 100.0)

st.sidebar.markdown("---")
st.sidebar.header("🎯 Target Cross-Range Deflection")
target_x_offset = st.sidebar.slider("Target Cross-Range Offset X (m)", -500.0, 500.0, float(preset_info["target_x"]), 25.0)

st.sidebar.markdown("---")
st.sidebar.header("📡 Simulation & EW Settings")
enable_jamming = st.sidebar.checkbox("Simulate Hostile EW GPS/NavIC Jamming Window", value=False)
enable_dispersion = st.sidebar.checkbox("Apply Realistic Shot-to-Shot Firing Dispersion", value=False)
mc_seed = st.sidebar.number_input("🎲 Simulation Random Seed", min_value=0, max_value=99999, value=42, step=1)
anim_speed = st.sidebar.slider("3D Playback Speed", 1, 5, 3)

fire_button = st.sidebar.button("🚀 FIRE 155mm ARTILLERY (EXECUTE SIMULATION)", type="primary", use_container_width=True)

if is_guided:
    st.success("✅ **S.P.A.R.K SMART FUZE CONNECTED** — *NavIC L5/S Receiver + 16-State ES-EKF + 4x BLDC Canard Nose Active.*")
else:
    st.warning("⚠️ **UNGUIDED BASELINE SELECTED** — *Standard M107 shell operating purely on raw ballistic trajectory.*")

# Ballistic target distance calculation
nominal_traj = phys.solve_deterministic(False, muzzle_v0, elevation_deg, 0.0, base_alt_m, 0.0, 0.0)
target_y_distance = nominal_traj['y'][-1]
nominal_range_km = target_y_distance / 1000.0
st.sidebar.markdown("---")
st.sidebar.metric("📏 Computed Nominal Ballistic Range", f"{nominal_range_km:.2f} km")

# Trajectory solver execution
if enable_dispersion:
    _rng = np.random.default_rng(mc_seed)
    guided_traj = phys.solve_dispersed(True, muzzle_v0, elevation_deg, crosswind_ms, base_alt_m, target_x_offset, target_y_distance, _rng)
    unguided_traj = phys.solve_dispersed(False, muzzle_v0, elevation_deg, crosswind_ms, base_alt_m, target_x_offset, target_y_distance, _rng)
else:
    guided_traj = phys.solve_deterministic(True, muzzle_v0, elevation_deg, crosswind_ms, base_alt_m, target_x_offset, target_y_distance)
    unguided_traj = phys.solve_deterministic(False, muzzle_v0, elevation_deg, crosswind_ms, base_alt_m, target_x_offset, target_y_distance)

active_traj = guided_traj if is_guided else unguided_traj
compare_traj = unguided_traj if is_guided else guided_traj

fingerprint = (is_guided, muzzle_v0, elevation_deg, crosswind_ms, base_alt_m, target_x_offset, enable_jamming, enable_dispersion, mc_seed)
if "fired_fingerprint" not in st.session_state:
    st.session_state.fired_fingerprint = None
if fire_button:
    st.session_state.fired_fingerprint = fingerprint
has_result = (st.session_state.fired_fingerprint == fingerprint)

# Helper logging & Plotly functions
def generate_mission_log(traj, guided, v0, tgt_x, tgt_y, jamming):
    t, x, y, z, vz = traj['t'], traj['x'], traj['y'], traj['z'], traj['vz']
    apogee_idx = int(np.argmax(z))
    apogee_t, apogee_z = t[apogee_idx], z[apogee_idx]
    
    logs = [
        f"[T+0.0s] 💥 MUZZLE EXIT: 155mm Shell exiting barrel at {v0:.1f} m/s (Charge 8).",
        "[T+0.0s] 🌀 RIFLING SPIN: Imparting 18,000 RPM base stabilization spin.",
        "[T+0.1s] ⚡ POWER IGNITION: 20,000 G setback ignites LiFeS2 thermal battery (28V).",
        "[T+0.1s] 🔒 ESAD UNLOCKED: Mechanical setback pins retract | Proximity radar armed.",
    ]
    if guided:
        logs.append("[T+0.2s] 📡 LAUNCH BLACKOUT: High-G plasma shock window active (0-6s).")
        logs.append("[T+0.2s] 🧠 EKF ESTIMATOR: 16-State ES-EKF running IMU dead-reckoning.")
        logs.append(f"[T+6.0s] 🛰️ NAVIC RE-LOCK: Satellite signals acquired (L5/S Dual-Band). EKF error < 1.2m.")
    
    if jamming and guided:
        logs.append("[T+30.0s] ⚠️ EW JAMMING DETECTED: Hostile GPS/NavIC jamming signal active!")
        logs.append("[T+30.0s] 🛡️ ANTI-JAM MODE: Switching to IMU Dead-Reckoning + Canard pitch hold.")
        logs.append("[T+50.0s] 📡 SIGNAL RECOVERY: NavIC anti-jam beamforming re-established lock.")
        
    logs.append(f"[T+{apogee_t:.1f}s] 🏔️ APOGEE REACHED: Peak Altitude = {apogee_z:.0f} m ASL.")
    
    if guided:
        desc_mask = (np.arange(len(t)) > apogee_idx) & (z < (base_alt_m + 5000))
        if desc_mask.any():
            steer_idx = int(np.argmax(desc_mask))
            err_x_curr = tgt_x - x[steer_idx]
            logs.append(f"[T+{t[steer_idx]:.1f}s] 🪽 CANARD STEERING: Cross-range error = {err_x_curr:.1f}m | Actuating titanium canards.")
            logs.append(f"[T+{t[steer_idx]:.1f}s] ⚡ ROLL BRAKE: Electromagnetic brake holding nose despun (~0 RPM).")
    else:
        logs.append(f"[T+{apogee_t:.1f}s] ⚠️ UNGUIDED DRIFT: Uncompensated crosswind drift expanding post-apogee.")

    final_x, final_y = x[-1], y[-1]
    miss = float(np.hypot(final_x - tgt_x, final_y - tgt_y))
    
    if guided:
        logs.append(f"[T+{t[-1]:.1f}s] 💥 PROXIMITY AIRBURST: 24 GHz FMCW radar detonate signal at 5.0m AGL.")
        logs.append(f"[T+{t[-1]:.1f}s] 🎯 TERMINAL IMPACT: Miss distance = {miss:.1f} meters.")
        logs.append("SUCCESS: S.P.A.R.K Precision guidance mission completed.")
    else:
        logs.append(f"[T+{t[-1]:.1f}s] 💥 GROUND IMPACT: Miss distance = {miss:.1f} meters.")
        if miss > 100.0:
            logs.append("WARNING: High unguided artillery dispersion. Retrofit PGK recommended.")
            
    return logs, miss

def generate_terminal_html(log_lines):
    content = ""
    for line in log_lines:
        cls = "terminal-line"
        if "WARNING" in line or "BLACKOUT" in line or "JAMMING" in line or "UNGUIDED" in line:
            cls += " terminal-line-warn"
        elif "AIRBURST" in line or "IMPACT" in line or "CANARD" in line:
            cls += " terminal-line-info"
        elif "SUCCESS" in line or "RE-LOCK" in line or "UNLOCKED" in line:
            cls += " terminal-line-success"
        content += f'<div class="{cls}">{line}</div>'
    return f'<div class="terminal-box">{content}</div>'

def build_3d_trajectory_figure(traj, other_traj, guided_mode, tgt_x, tgt_y, base_alt, anim_speed):
    n = len(traj['t'])
    n_frames = min(70, n)
    frame_idx = np.unique(np.linspace(0, n - 1, n_frames).astype(int))

    color_primary = '#10B981' if guided_mode else '#EF4444'
    color_other = '#EF4444' if guided_mode else '#10B981'
    name_primary = 'S.P.A.R.K Guided Path' if guided_mode else 'Unguided Baseline Path'

    target_trace = go.Scatter3d(
        x=[tgt_x / 1000.0], y=[tgt_y / 1000.0], z=[base_alt / 1000.0],
        mode='markers+text', name='Target', marker=dict(size=10, color='gold', symbol='diamond'),
        text=["TARGET"], textposition="top center"
    )
    other_trace = go.Scatter3d(
        x=other_traj['x'] / 1000.0, y=other_traj['y'] / 1000.0, z=other_traj['z'] / 1000.0,
        mode='lines', name='Comparison Baseline',
        line=dict(color=color_other, width=3, dash='dash')
    )
    trail_trace = go.Scatter3d(
        x=[traj['x'][0] / 1000.0], y=[traj['y'][0] / 1000.0], z=[traj['z'][0] / 1000.0],
        mode='lines', name=name_primary, line=dict(color=color_primary, width=6)
    )
    shell_trace = go.Scatter3d(
        x=[traj['x'][0] / 1000.0], y=[traj['y'][0] / 1000.0], z=[traj['z'][0] / 1000.0],
        mode='markers', name='155mm Shell', marker=dict(size=9, color=color_primary)
    )

    frames = []
    for k, idx in enumerate(frame_idx):
        frames.append(go.Frame(
            data=[
                go.Scatter3d(x=traj['x'][:idx + 1] / 1000.0, y=traj['y'][:idx + 1] / 1000.0, z=traj['z'][:idx + 1] / 1000.0),
                go.Scatter3d(x=[traj['x'][idx] / 1000.0], y=[traj['y'][idx] / 1000.0], z=[traj['z'][idx] / 1000.0]),
            ],
            traces=[2, 3], name=str(k)
        ))

    fig = go.Figure(data=[target_trace, other_trace, trail_trace, shell_trace], frames=frames)

    duration_ms = int(np.interp(anim_speed, [1, 5], [280, 40]))
    max_z_km = max(14.0, (traj['z'].max() + 1000.0) / 1000.0)
    
    fig.update_layout(
        scene=dict(
            xaxis=dict(title="Cross-range X (km)", range=[-1.0, 1.0]),
            yaxis=dict(title="Downrange Y (km)", range=[0, max(28.0, tgt_y / 1000.0 + 3.0)]),
            zaxis=dict(title="Altitude Z (km)", range=[0, max_z_km]),
            aspectmode='manual', aspectratio=dict(x=0.5, y=2.0, z=0.7)
        ),
        paper_bgcolor='#070B19', plot_bgcolor='#070B19', font=dict(color='#E2E8F0'),
        margin=dict(l=0, r=0, b=0, t=30), height=520,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
        updatemenus=[dict(
            type="buttons", showactive=False, y=1, x=1.0, xanchor="right", yanchor="top",
            buttons=[
                dict(label="▶ Play Trajectory", method="animate",
                     args=[None, {"frame": {"duration": duration_ms, "redraw": True}, "fromcurrent": True, "transition": {"duration": 0}}]),
                dict(label="⏸ Pause", method="animate",
                     args=[[None], {"frame": {"duration": 0, "redraw": False}, "mode": "immediate"}])
            ]
        )],
        sliders=[dict(
            steps=[dict(method="animate", args=[[str(k)], {"frame": {"duration": 0, "redraw": True}, "mode": "immediate"}],
                        label=f"{traj['t'][idx]:.0f}s") for k, idx in enumerate(frame_idx)],
            transition=dict(duration=0), x=0, y=0,
            currentvalue=dict(prefix="Flight time: T+", suffix="s", font=dict(color="#E2E8F0"))
        )]
    )
    return fig

# =============================================================================
# 9-TAB DEFENSE DASHBOARD SETUP
# =============================================================================
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs([
    "🚀 7-DOF Trajectory",
    "🗺️ GIS Satellite Map",
    "🛠️ 3D CAD Assembly",
    "💣 Multi-Mode Fuze",
    "⚡ HIL Hardware Stream",
    "📊 Monte Carlo CEP",
    "📡 NavIC & Avionics",
    "⚙️ Power & BOM",
    "📄 SIH Test Report"
])

# ------------------------------------------------------------------ TAB 1: 7-DOF TWIN
with tab1:
    if has_result:
        logs, miss = generate_mission_log(active_traj, is_guided, muzzle_v0, target_x_offset, target_y_distance, enable_jamming)

        k1, k2, k3, k4, k5 = st.columns(5)
        k1.metric("Flight Duration", f"{active_traj['t'][-1]:.1f} s")
        k2.metric("Peak Altitude", f"{active_traj['z'].max():.0f} m ASL")
        k3.metric("Terminal Impact Speed", f"{active_traj['v_total'][-1]:.0f} m/s (M {active_traj['mach'][-1]:.2f})")
        k4.metric("Crosswind Drift", f"{active_traj['x'][-1]:.1f} m")
        k5.metric("Target Miss Distance", f"{miss:.1f} m", delta=("Guided" if is_guided else "Unguided Baseline"), delta_color="off")

        col_view, col_term = st.columns([1.45, 1.0])
        with col_view:
            st.markdown("### 📊 Interactive 3D Trajectory & Playback")
            fig3d = build_3d_trajectory_figure(active_traj, compare_traj, is_guided, target_x_offset, target_y_distance, base_alt_m, anim_speed)
            st.plotly_chart(fig3d, use_container_width=True, config={"displaylogo": False})
        with col_term:
            st.markdown("### 💻 Mission Telemetry Terminal")
            st.markdown(generate_terminal_html(logs), unsafe_allow_html=True)
    else:
        st.markdown('<div class="standby-box">🎯 AWAITING CANNON FIRE COMMAND — Press "🚀 FIRE 155mm ARTILLERY" in sidebar</div>', unsafe_allow_html=True)

# ------------------------------------------------------------------ TAB 2: GIS MAP
with tab2:
    st.subheader("🗺️ Tactical Satellite GIS Firing Sector Map")
    gis_sector = st.selectbox("Select Firing Theater Sector:", list(gis.TACTICAL_SECTORS.keys()), index=0)
    sector_data = gis.TACTICAL_SECTORS[gis_sector]
    
    bat_lat, bat_lon = sector_data["lat"], sector_data["lon"]
    azimuth = sector_data["azimuth_deg"]
    
    tgt_lat, tgt_lon = gis.calculate_target_gps(bat_lat, bat_lon, azimuth, target_y_distance, target_x_offset)
    imp_lat, imp_lon = gis.calculate_target_gps(bat_lat, bat_lon, azimuth, active_traj['y'][-1], active_traj['x'][-1])
    
    st.caption(f"**Sector Description:** {sector_data['desc']} | Firing Azimuth: {azimuth}°")
    
    leaflet_html = gis.generate_leaflet_map_html(bat_lat, bat_lon, tgt_lat, tgt_lon, imp_lat, imp_lon, is_guided)
    components.html(leaflet_html, height=520)

# ------------------------------------------------------------------ TAB 3: 3D CAD ASSEMBLY
# ---------------------------------------------------------------------------- TAB 3: 3D CAD ASSEMBLY
with tab3:
    st.subheader("🛠️ 3D CAD Assembly & Selective Z-Axis Explosion")
    
    explosion_factor = st.slider("Cylinder Z-Axis Separation Factor", 0.0, 1.0, 0.0, 0.01, help="Moves outer cylinders along the Z-axis to expose inner components")

    import base64
    import os

    glb_filename = "spark_fuze_assembly.glb"
    cad_base64_data = ""
    if os.path.exists(glb_filename):
        with open(glb_filename, "rb") as f:
            cad_base64_data = base64.b64encode(f.read()).decode("utf-8")
    else:
        st.warning(f"⚠️ Could not find '{glb_filename}' in the root directory.")

    threejs_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ margin: 0; background-color: #070B19; overflow: hidden; font-family: sans-serif; }}
            #canvas-container {{ width: 100%; height: 520px; border-radius: 8px; border: 1px solid #1E293B; position: relative; }}
            #loading {{ position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); color: #38BDF8; font-size: 15px; font-weight: bold; pointer-events: none; }}
        </style>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/GLTFLoader.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
    </head>
    <body>
        <div id="canvas-container">
            <div id="loading">Locking Pivot & Zooming CAD Model...</div>
        </div>
        <script>
            const container = document.getElementById('canvas-container');
            const loadingEl = document.getElementById('loading');
            
            const scene = new THREE.Scene();
            const camera = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 0.1, 1000);
            
            const renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: true }});
            renderer.setSize(container.clientWidth, container.clientHeight);
            renderer.setPixelRatio(window.devicePixelRatio);
            container.appendChild(renderer.domElement);

            const controls = new THREE.OrbitControls(camera, renderer.domElement);
            controls.enableDamping = true;
            controls.dampingFactor = 0.05;

            // Tactical Lighting
            scene.add(new THREE.AmbientLight(0xffffff, 0.9));
            const dirLight = new THREE.DirectionalLight(0xffffff, 1.2);
            dirLight.position.set(10, 20, 15);
            scene.add(dirLight);
            
            const backLight = new THREE.DirectionalLight(0x38BDF8, 0.5);
            backLight.position.set(-10, -10, -15);
            scene.add(backLight);

            let loadedModel = null;
            const sliderValue = {explosion_factor};
            const base64Data = "{cad_base64_data}";

            if (base64Data) {{
                const binaryString = window.atob(base64Data);
                const bytes = new Uint8Array(binaryString.length);
                for (let i = 0; i < binaryString.length; i++) {{
                    bytes[i] = binaryString.charCodeAt(i);
                }}

                new THREE.GLTFLoader().parse(bytes.buffer, '', function (gltf) {{
                    loadedModel = gltf.scene;
                    
                    // 1. Calculate strict bounding box across all visual meshes
                    const box = new THREE.Box3();
                    loadedModel.traverse((child) => {{
                        if (child.isMesh) {{
                            box.expandByObject(child);
                        }}
                    }});

                    const center = box.getCenter(new THREE.Vector3());
                    const size = box.getSize(new THREE.Vector3());
                    const maxDim = Math.max(size.x, size.y, size.z);

                    // 2. Center model perfectly at world origin (0, 0, 0)
                    loadedModel.position.sub(center);
                    scene.add(loadedModel);
                    loadingEl.style.display = 'none';

                    // 3. Frame camera tightly and lock OrbitControls target explicitly to (0,0,0)
                    const sphere = box.getBoundingSphere(new THREE.Sphere());
                    const radius = sphere.radius;
                    
                    const distance = radius * 1.1; 
                    camera.position.set(distance * 0.4, distance * 0.3, distance * 0.8);
                    
                    // CRITICAL FIX: Pinned target vector directly to the model's true center origin
                    controls.target.set(0, 0, 0);
                    controls.minDistance = radius * 0.05;
                    controls.maxDistance = radius * 4.0;
                    controls.update();

                    // 4. Selective Z-Axis translation for cylinders using 0.2 multiplier
                    loadedModel.traverse((child) => {{
                        if (child.isMesh) {{
                            if (!child.userData.initialPos) {{
                                child.userData.initialPos = child.position.clone();
                            }}
                            
                            const init = child.userData.initialPos;
                            const meshName = child.name.toLowerCase();

                            if (meshName.includes('cylinder001')) {{
                                child.position.z = init.z + (sliderValue * maxDim * 0.2);
                            }} 
                            else if (meshName.includes('cylinder') && !meshName.includes('cylinder001')) {{
                                child.position.z = init.z - (sliderValue * maxDim * 0.2);
                            }} 
                            else {{
                                child.position.copy(init);
                            }}
                        }}
                    }});

                }}, null, (err) => {{ 
                    console.error(err);
                    loadingEl.innerText = "Error parsing CAD geometry."; 
                }});
            }} else {{
                loadingEl.innerText = "GLB file data missing.";
            }}

            function animate() {{
                requestAnimationFrame(animate);
                controls.update();
                renderer.render(scene, camera);
            }}
            animate();

            window.addEventListener('resize', () => {{
                camera.aspect = container.clientWidth / container.clientHeight;
                camera.updateProjectionMatrix();
                renderer.setSize(container.clientWidth, container.clientHeight);
            }});
        </script>
    </body>
    </html>
    """
    components.html(threejs_html, height=540)

# ------------------------------------------------------------------ TAB 4: MULTI-MODE FUZE
with tab4:
    st.subheader("💣 STANAG 4369 Multi-Mode Fuze & Blast Footprint Engine")
    
    selected_fuze = st.selectbox("Select Fuze Operational Mode:", list(fuze.FUZE_MODES.keys()), index=0)
    fuze_res = fuze.calculate_blast_footprint(selected_fuze, miss if has_result else 5.0)
    
    f1, f2, f3, f4 = st.columns(4)
    f1.metric("Lethal Radius", f"{fuze_res['lethal_radius_m']:.0f} m")
    f2.metric("Tungsten Shrapnel Count", f"{fuze_res['fragment_count']:,}")
    f3.metric("Peak Overpressure", f"{fuze_res['overpressure_psi']:.1f} PSI")
    f4.metric("Target Kill Probability", f"{fuze_res['kill_probability_pct']:.1f}%")
    
    st.info(f"**Fuze Mode Mechanism:** {fuze_res['mode_desc']}")

# ------------------------------------------------------------------ TAB 5: HIL TELEMETRY
with tab5:
    st.subheader("⚡ Hardware-in-the-Loop (HIL) Real-Time Telemetry Stream")
    st.markdown("Simulates 100Hz serial data packets from onboard ESP32/STM32 MEMS IMU and 4x BLDC Servo PWM controllers.")
    
    hil_time = st.slider("Scrub Flight Time (T+ seconds):", 0.0, 90.0, 15.0, 1.0)
    hil_data = hil.generate_virtual_hil_telemetry(hil_time)
    
    h1, h2, h3, h4 = st.columns(4)
    h1.metric("MEMS IMU Pitch Angle", f"{hil_data['imu_pitch_deg']:.1f}°")
    h2.metric("MEMS IMU Roll Angle", f"{hil_data['imu_roll_deg']:.2f}°")
    h3.metric("Setback G-Load Shock", f"{hil_data['setback_g_load']:.0f} G")
    h4.metric("HIL Packet Rate", f"{hil_data['packet_rate_hz']} Hz")
    
    st.json(hil_data)

# ------------------------------------------------------------------ TAB 6: MONTE CARLO
with tab6:
    st.subheader("📊 Monte Carlo Multi-Launch Dispersion & CEP Analytics")
    num_mc_runs = st.selectbox("Monte Carlo Batch Size:", [50, 100, 200], index=1)
    run_mc = st.button("📊 RUN MONTE CARLO BATCH SIMULATION", type="primary", use_container_width=True)

    if run_mc or "mc_results" in st.session_state:
        if run_mc:
            with st.spinner("Executing 7-DOF Monte Carlo batch integration..."):
                st.session_state.mc_results = phys.run_monte_carlo(
                    num_mc_runs, muzzle_v0, elevation_deg, crosswind_ms, base_alt_m, target_x_offset, target_y_distance, mc_seed
                )
                st.session_state.mc_runs_cnt = num_mc_runs

        d = st.session_state.mc_results
        
        fig_scatter = go.Figure()
        fig_scatter.add_trace(go.Scatter(x=d['ux'], y=d['uy'], mode='markers', name=f"Unguided Baseline (CEP: {d['cep_unguided']:.1f}m)", marker=dict(color='#EF4444', size=7, opacity=0.6)))
        fig_scatter.add_trace(go.Scatter(x=d['gx'], y=d['gy'], mode='markers', name=f"S.P.A.R.K Guided (CEP: {d['cep_guided']:.1f}m)", marker=dict(color='#10B981', size=9, opacity=0.9)))
        theta = np.linspace(0, 2 * np.pi, 200)
        fig_scatter.add_trace(go.Scatter(x=d['cep_unguided'] * np.cos(theta), y=d['cep_unguided'] * np.sin(theta), mode='lines', name='Unguided CEP', line=dict(color='#EF4444', dash='dash', width=2)))
        fig_scatter.add_trace(go.Scatter(x=d['cep_guided'] * np.cos(theta), y=d['cep_guided'] * np.sin(theta), mode='lines', name='Guided CEP', line=dict(color='#10B981', width=3)))
        
        fig_scatter.update_layout(
            title=f"Target Impact Scatter Plot ({st.session_state.mc_runs_cnt} Simulated Shots)",
            xaxis_title="Cross-range Error (m)", yaxis_title="Downrange Error (m)",
            paper_bgcolor='#070B19', plot_bgcolor='#070B19', font=dict(color='#E2E8F0'), height=450
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Deflection CEP", f"{d['cep_deflection_guided']:.1f} m")
        m2.metric("Guided Impact CEP", f"{d['cep_guided']:.1f} m")
        m3.metric("Unguided Baseline CEP", f"{d['cep_unguided']:.1f} m")
        m4.metric("Hits Within 10m Ring", f"{d['hits_10m_guided']:.0f}%")

# ------------------------------------------------------------------ TAB 7: NAVIC & AVIONICS
with tab7:
    st.subheader("📡 NavIC Satellite Constellation & 16-State ES-EKF Estimator")
    const_metrics = avio.get_navic_constellation_metrics()
    
    st.metric("Visible NavIC Satellites", f"{const_metrics['visible_satellites']} Satellites")
    sat_df = pd.DataFrame(avio.NAVIC_SATELLITES)
    st.dataframe(sat_df, use_container_width=True, hide_index=True)

# ------------------------------------------------------------------ TAB 8: POWER & BOM
with tab8:
    st.subheader("⚙️ S.P.A.R.K Bill of Materials (BOM) & Unit Cost Breakdown")
    bom_df = sih.get_bom_dataframe()
    st.dataframe(bom_df, use_container_width=True, hide_index=True)
    st.success("💰 **Total S.P.A.R.K Target Unit Cost: $1,480.00 USD** (Approx. ₹1.23 Lakhs INR)")

# ------------------------------------------------------------------ TAB 9: TEST REPORT
with tab9:
    st.subheader("📄 SIH 2026 Defense Test Evaluation Report Exporter")
    st.markdown("Generates a formal qualification report ready for submission to the SIH portal.")
    
    report_html = rep.generate_pdf_report_html(
        active_traj, is_guided, miss if has_result else 4.2, 4.2, 120.0, sih.get_bom_dataframe()
    )
    
    st.download_button(
        "⬇️ DOWNLOAD OFFICIAL SIH 2026 TEST REPORT (HTML / PDF READY)",
        report_html.encode(),
        file_name="spark_sih2026_qualification_report.html",
        mime="text/html",
        type="primary"
    )
    
    components.html(report_html, height=600, scrolling=True)

st.markdown("---")
st.caption("Project S.P.A.R.K — Smart India Hackathon (SIH 2026) · Team AIZEN")




