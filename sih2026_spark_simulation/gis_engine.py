import numpy as np

# =============================================================================
# GIS TACTICAL BATTERY COORDINATE PRESETS
# =============================================================================
TACTICAL_SECTORS = {
    "🏔️ Kargil / Dras Sector (Tiger Hill)": {
        "lat": 34.4284,
        "lon": 75.8421,
        "azimuth_deg": 45.0,
        "desc": "High altitude mountain artillery position facing border ridge lines."
    },
    "🏜️ Pokhran Field Firing Range": {
        "lat": 27.0238,
        "lon": 71.7512,
        "azimuth_deg": 90.0,
        "desc": "Desert proving ground for standard proof firing and CEP qualification."
    },
    "⛰️ Tawang Forward Operating Base": {
        "lat": 27.5860,
        "lon": 91.8594,
        "azimuth_deg": 15.0,
        "desc": "Eastern Sector high-altitude artillery position."
    }
}

def calculate_target_gps(battery_lat, battery_lon, azimuth_deg, downrange_m, crossrange_m):
    """
    Computes target GPS latitude and longitude given firing position, downrange, cross-range, and azimuth.
    """
    R_earth = 6371000.0  # Earth radius in meters
    
    # Total displacement distance and bearing angle
    dist = np.hypot(downrange_m, crossrange_m)
    alpha = np.arctan2(crossrange_m, downrange_m)
    total_bearing = np.radians(azimuth_deg) + alpha
    
    lat1 = np.radians(battery_lat)
    lon1 = np.radians(battery_lon)
    
    delta = dist / R_earth
    
    lat2 = np.arcsin(np.sin(lat1) * np.cos(delta) + np.cos(lat1) * np.sin(delta) * np.cos(total_bearing))
    lon2 = lon1 + np.arctan2(np.sin(total_bearing) * np.sin(delta) * np.cos(lat1),
                             np.cos(delta) - np.sin(lat1) * np.sin(lat2))
    
    return float(np.degrees(lat2)), float(np.degrees(lon2))

def generate_leaflet_map_html(battery_lat, battery_lon, target_lat, target_lon, impact_lat, impact_lon, is_guided):
    """
    Generates an interactive Leaflet.js satellite tactical map HTML component.
    """
    map_color = "#10B981" if is_guided else "#EF4444"
    status_label = "S.P.A.R.K GUIDED IMPACT" if is_guided else "UNGUIDED BASELINE DRIFT"

    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8" />
        <title>Tactical GIS Map</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
        <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
        <style>
            body {{ margin: 0; padding: 0; background-color: #070B19; color: #E2E8F0; font-family: sans-serif; }}
            #map {{ width: 100%; height: 500px; border-radius: 8px; border: 1px solid #1E293B; }}
            .leaflet-container {{ background: #070B19; }}
            .map-legend {{
                position: absolute; bottom: 20px; left: 20px; z-index: 1000;
                background: rgba(7, 11, 25, 0.85); border: 1px solid #1E293B; border-left: 4px solid {map_color};
                padding: 10px 14px; border-radius: 6px; font-size: 0.82rem; font-family: monospace;
            }}
        </style>
    </head>
    <body>
        <div id="map"></div>
        <div class="map-legend">
            <div><strong style="color: {map_color};">🎯 MODE: {status_label}</strong></div>
            <div>📍 Battery Lat/Lon: {battery_lat:.4f}, {battery_lon:.4f}</div>
            <div>🎯 Target Lat/Lon: {target_lat:.4f}, {target_lon:.4f}</div>
            <div>💥 Impact Lat/Lon: {impact_lat:.4f}, {impact_lon:.4f}</div>
        </div>

        <script>
            var map = L.map('map').setView([{battery_lat}, {battery_lon}], 11);

            // OpenStreetMap Satellite / Topo tiles
            L.tileLayer('https://{{s}}.tile.opentopomap.org/{{z}}/{{x}}/{{y}}.png', {{
                maxZoom: 17,
                attribution: 'OpenTopoMap | Project S.P.A.R.K GIS Twin'
            }}).addTo(map);

            // Battery Marker
            var batteryIcon = L.divIcon({{
                className: 'custom-div-icon',
                html: "<div style='background-color:#38BDF8; width:14px; height:14px; border-radius:50%; border:2px solid white;'></div>",
                iconSize: [14, 14]
            }});
            L.marker([{battery_lat}, {battery_lon}], {{icon: batteryIcon}}).addTo(map)
                .bindPopup("<b>🎯 155mm Artillery Battery</b><br>Firing Position");

            // Target Marker & Collateral Damage Circles
            var targetMarker = L.circleMarker([{target_lat}, {target_lon}], {{
                radius: 8, color: '#F59E0B', fillColor: '#F59E0B', fillOpacity: 0.9
            }}).addTo(map).bindPopup("<b>🎯 TARGET BUNKERS</b>");

            // 10m, 25m, 50m Collateral Damage Rings
            L.circle([{target_lat}, {target_lon}], {{ radius: 10, color: '#10B981', weight: 2, fill: false }}).addTo(map);
            L.circle([{target_lat}, {target_lon}], {{ radius: 25, color: '#F59E0B', weight: 1.5, dashArray: '4,4', fill: false }}).addTo(map);
            L.circle([{target_lat}, {target_lon}], {{ radius: 50, color: '#EF4444', weight: 1, dashArray: '2,4', fill: false }}).addTo(map);

            // Impact Point Marker
            L.circleMarker([{impact_lat}, {impact_lon}], {{
                radius: 7, color: '{map_color}', fillColor: '{map_color}', fillOpacity: 0.95
            }}).addTo(map).bindPopup("<b>💥 IMPACT POINT</b>");

            // Trajectory Line
            var latlngs = [
                [{battery_lat}, {battery_lon}],
                [{impact_lat}, {impact_lon}]
            ];
            var polyline = L.polyline(latlngs, {{ color: '{map_color}', weight: 3, dashArray: '6,6' }}).addTo(map);

            map.fitBounds(polyline.getBounds(), {{ padding: [40, 40] }});
        </script>
    </body>
    </html>
    """
    return html_code
