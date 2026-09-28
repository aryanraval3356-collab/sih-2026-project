import os

def generate_3d_cad_html(explosion_factor=0.5, glb_filename="spark_fuze_assembly.glb"):
    """
    Generates interactive Three.js 3D CAD viewer.
    Supports loading custom Blender .glb / .gltf keyframe animations scrubbed by the Streamlit slider,
    with a fallback procedural 3D exploded view if no .glb file is present.
    """
    # Check if custom Blender GLB file exists in directory
    has_glb = os.path.exists(glb_filename)
    
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8" />
        <title>S.P.A.R.K 3D CAD Blender Twin</title>
        <style>
            body {{ margin: 0; padding: 0; overflow: hidden; background-color: #030712; font-family: monospace; color: #10B981; }}
            #canvas-container {{ width: 100%; height: 480px; }}
            #cad-info {{
                position: absolute; top: 15px; left: 15px; z-index: 100;
                background: rgba(15, 23, 42, 0.88); border: 1px solid #1E293B; border-left: 4px solid #10B981;
                padding: 12px; border-radius: 6px; font-size: 0.82rem; pointer-events: none;
            }}
            .badge-glb {{
                display: inline-block; background: rgba(16, 185, 129, 0.2); color: #10B981;
                border: 1px solid #10B981; padding: 2px 6px; border-radius: 4px; font-size: 0.75rem; font-weight: bold;
            }}
        </style>
        <!-- Three.js Core & Addons -->
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/GLTFLoader.js"></script>
    </head>
    <body>
        <div id="cad-info">
            <strong style="color: #38BDF8;">🛠️ S.P.A.R.K 3D BLENDER CAD ENGINE</strong> 
            <span class="badge-glb">{"CUSTOM BLENDER MODEL LOADED" if has_glb else "PROCEDURAL TWIN ACTIVE"}</span><br>
            • STANAG 4369 Fuze Assembly & Shell Body<br>
            • Interactive Timeline Scrubber: Fitted (0%) → Fully Exploded (100%)<br>
            • Mouse Controls: Drag to Rotate | Scroll to Zoom | Right-Click to Pan
        </div>
        <div id="canvas-container"></div>

        <script>
            var container = document.getElementById('canvas-container');
            var scene = new THREE.Scene();
            scene.background = new THREE.Color(0x030712);

            var camera = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 0.1, 1000);
            camera.position.set(0, 4, 10);

            var renderer = new THREE.WebGLRenderer({{ antialias: true }});
            renderer.setSize(container.clientWidth, container.clientHeight);
            renderer.shadowMap.enabled = true;
            container.appendChild(renderer.domElement);

            var controls = new THREE.OrbitControls(camera, renderer.domElement);
            controls.enableDamping = true;

            // Lighting Setup
            var ambientLight = new THREE.AmbientLight(0xffffff, 0.7);
            scene.add(ambientLight);

            var dirLight1 = new THREE.DirectionalLight(0x10B981, 0.9);
            dirLight1.position.set(10, 20, 10);
            scene.add(dirLight1);

            var dirLight2 = new THREE.DirectionalLight(0x38BDF8, 0.7);
            dirLight2.position.set(-10, -10, -10);
            scene.add(dirLight2);

            var explosion = {explosion_factor};  // 0.0 = Fitted, 1.0 = Fully Exploded
            var mixer = null;
            var animationClip = null;

            // Try loading custom Blender GLB model if present
            var glbUrl = "{glb_filename}";
            var useGlb = {str(has_glb).lower()};

            if (useGlb) {{
                var loader = new THREE.GLTFLoader();
                loader.load(glbUrl, function(gltf) {{
                    var model = gltf.scene;
                    scene.add(model);

                    // Handle Blender Animations
                    if (gltf.animations && gltf.animations.length > 0) {{
                        mixer = new THREE.AnimationMixer(model);
                        animationClip = gltf.animations[0];
                        var action = mixer.clipAction(animationClip);
                        action.play();
                        
                        // Scrub keyframe animation based on slider explosion factor
                        var duration = animationClip.duration;
                        mixer.setTime(explosion * duration);
                    }} else {{
                        // Explode mesh hierarchy manually if no keyframe tracks exist
                        model.traverse(function(child) {{
                            if (child.isMesh) {{
                                var dir = child.position.clone().normalize();
                                child.position.addScaledVector(dir, explosion * 2.0);
                            }}
                        }});
                    }}
                }}, undefined, function(error) {{
                    console.error("Error loading GLB, falling back to procedural model:", error);
                    buildProceduralModel();
                }});
            }} else {{
                buildProceduralModel();
            }}

            function buildProceduralModel() {{
                var group = new THREE.Group();

                // 1. Radar Nose Cone Dome (Gold / Amber)
                var domeGeo = new THREE.ConeGeometry(0.8, 1.4, 32);
                var domeMat = new THREE.MeshStandardMaterial({{ color: 0xF59E0B, metalness: 0.3, roughness: 0.2, transparent: true, opacity: 0.85 }});
                var dome = new THREE.Mesh(domeGeo, domeMat);
                dome.position.y = 3.2 + (explosion * 2.5);
                group.add(dome);

                // 2. Canard Actuator Hub (Cyan Titanium)
                var hubGeo = new THREE.CylinderGeometry(0.9, 0.95, 1.2, 32);
                var hubMat = new THREE.MeshStandardMaterial({{ color: 0x38BDF8, metalness: 0.8, roughness: 0.3 }});
                var hub = new THREE.Mesh(hubGeo, hubMat);
                hub.position.y = 1.8 + (explosion * 1.5);
                group.add(hub);

                // 4x Titanium Canards
                for (var i = 0; i < 4; i++) {{
                    var canardGeo = new THREE.BoxGeometry(1.2, 0.1, 0.4);
                    var canardMat = new THREE.MeshStandardMaterial({{ color: 0x10B981, metalness: 0.9, roughness: 0.2 }});
                    var canard = new THREE.Mesh(canardGeo, canardMat);
                    var angle = i * (Math.PI / 2);
                    var r = 1.0 + (explosion * 1.8);
                    canard.position.set(Math.cos(angle) * r, 1.8 + (explosion * 1.5), Math.sin(angle) * r);
                    canard.rotation.y = -angle;
                    group.add(canard);
                }}

                // 3. Roll Brake Bearing Hub (Silver Metallic)
                var brakeGeo = new THREE.CylinderGeometry(0.95, 1.0, 0.8, 32);
                var brakeMat = new THREE.MeshStandardMaterial({{ color: 0xCBD5E1, metalness: 0.95, roughness: 0.1 }});
                var brake = new THREE.Mesh(brakeGeo, brakeMat);
                brake.position.y = 0.6 + (explosion * 0.6);
                group.add(brake);

                // 4. Circular PCB Stack (Green)
                var pcbGeo = new THREE.CylinderGeometry(0.9, 0.9, 0.5, 32);
                var pcbMat = new THREE.MeshStandardMaterial({{ color: 0x059669, metalness: 0.2, roughness: 0.5 }});
                var pcb = new THREE.Mesh(pcbGeo, pcbMat);
                pcb.position.y = -0.2 - (explosion * 0.5);
                group.add(pcb);

                // 5. LiFeS2 Thermal Battery (Dark Slate)
                var batGeo = new THREE.CylinderGeometry(0.95, 1.0, 1.0, 32);
                var batMat = new THREE.MeshStandardMaterial({{ color: 0x1E293B, metalness: 0.7, roughness: 0.4 }});
                var bat = new THREE.Mesh(batGeo, batMat);
                bat.position.y = -1.2 - (explosion * 1.5);
                group.add(bat);

                // 6. 155mm Projectile Main Shell Body (Steel Olive)
                var shellGeo = new THREE.CylinderGeometry(1.0, 1.05, 2.2, 32);
                var shellMat = new THREE.MeshStandardMaterial({{ color: 0x475569, metalness: 0.85, roughness: 0.25 }});
                var shellMesh = new THREE.Mesh(shellGeo, shellMat);
                shellMesh.position.y = -2.8 - (explosion * 2.8);
                group.add(shellMesh);

                scene.add(group);
            }}

            function animate() {{
                requestAnimationFrame(animate);
                controls.update();
                renderer.render(scene, camera);
            }}
            animate();
        </script>
    </body>
    </html>
    """
    return html_code
