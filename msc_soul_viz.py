### msc_soul_viz.py ###
import streamlit as st
import streamlit.components.v1 as components
import streamlit_antd_components as sac
import msc_viz as viz
import msc_soul_gen as gen
import json

def render_soul_scene(radar_dict, user_nodes=None):
    if user_nodes is None: user_nodes = []
    
    try: payload, p_attr, s_attr = gen.prepare_soul_data(radar_dict, user_nodes)
    except: return
        
    payload_json = json.dumps(payload)
    lang = st.session_state.get('language', 'en')
    
    SHAPE_NAMES = {
        "Agency": "Starburst", "Care": "Cluster", "Curiosity": "Nebula",
        "Coherence": "Grid", "Reflection": "Vortex", "Transcendence": "Ascension", "Aesthetic": "Sphere"
    }
    title = SHAPE_NAMES.get(p_attr, p_attr)
    sac.divider(label="SOUL FORM", icon='layers', align='center', color='gray')
    st.markdown(f"<div style='text-align:center; margin-bottom:10px; font-family:serif; letter-spacing:2px; font-size:0.9em; color:#AAA;'>{title.upper()}</div>", unsafe_allow_html=True)

    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body, html {{ margin: 0; padding: 0; width: 100%; height: 100%; overflow: hidden; background-color: #000; }}
            canvas {{ display: block; }}
        </style>
    </head>
    <body>
        <canvas id="soulCanvas"></canvas>
        <script>
            const DATA = {payload_json};
            const PRIMARY = DATA.primary;
            const SECONDARY = DATA.secondary;
            const THOUGHTS = DATA.thoughts;
            const ATMOS_COLORS = DATA.atmos_colors;
            
            const canvas = document.getElementById('soulCanvas');
            const ctx = canvas.getContext('2d');
            
            let width, height, cx, cy;
            let particles = [];
            let fov = 300; 
            let globalAngle = 0;
            
            function resize() {{
                width = window.innerWidth;
                height = window.innerHeight;
                canvas.width = width;
                canvas.height = height;
                cx = width / 2;
                cy = height / 2;
            }}
            window.addEventListener('resize', resize);
            resize();

            class Particle {{
                constructor(isThought, thoughtData) {{
                    this.isThought = isThought;
                    this.init(thoughtData);
                }}

                init(thoughtData) {{
                    let u = Math.random(); let v = Math.random();
                    let theta = 2 * Math.PI * u; let phi = Math.acos(2 * v - 1);
                    let r = 0;
                    
                    if (PRIMARY === 'Agency') {{ r = Math.random() * 250 + 50; }}
                    else if (PRIMARY === 'Care') {{ r = Math.random() * 60; }}
                    else if (PRIMARY === 'Coherence') {{ 
                        let step = 70; 
                        this.baseX = Math.round((Math.random()-0.5)*400/step)*step;
                        this.baseY = Math.round((Math.random()-0.5)*400/step)*step;
                        this.baseZ = Math.round((Math.random()-0.5)*400/step)*step;
                        r = 0;
                    }}
                    else if (PRIMARY === 'Transcendence') {{ 
                        this.x = (Math.random()-0.5)*100; 
                        this.y = (Math.random()-0.5)*100; 
                        this.z = (Math.random()-0.5)*500; 
                        r = 0;
                    }}
                    else if (PRIMARY === 'Reflection') {{
                        let flatR = Math.random() * 180 + 20;
                        let ang = Math.random() * Math.PI * 2;
                        this.x = flatR * Math.cos(ang);
                        this.y = flatR * Math.sin(ang);
                        this.z = (Math.random()-0.5) * 40; 
                        r = 0;
                    }}
                    else {{ r = (Math.random() - 0.5) * 350; }}

                    if (r > 0) {{
                        this.x = r * Math.sin(phi) * Math.cos(theta);
                        this.y = r * Math.sin(phi) * Math.sin(theta);
                        this.z = r * Math.cos(phi);
                    }} else if (PRIMARY === 'Coherence') {{
                        this.x = this.baseX; this.y = this.baseY; this.z = this.baseZ;
                    }}

                    if (this.isThought) {{
                        this.color = thoughtData.color;
                        this.sizeBase = 4.0;
                        this.x *= 0.8; this.y *= 0.8; this.z *= 0.8; 
                    }} else {{
                        this.color = ATMOS_COLORS[Math.floor(Math.random() * ATMOS_COLORS.length)];
                        this.sizeBase = Math.random() * 1.5 + 0.5; 
                    }}

                    this.phase = Math.random() * Math.PI * 2;
                    this.speed = Math.random() * 0.5 + 0.5;
                    this.ox = this.x; this.oy = this.y; this.oz = this.z;
                }}

                update(t) {{
                    let x = this.ox; let y = this.oy; let z = this.oz;
                    let p = this.phase; let s = this.speed;

                    let jitter = Math.sin(t * 8 + p) * 1.5; 

                    if (SECONDARY === 'Agency') {{ 
                        let pulse = 1 + 0.3 * Math.sin(t * 4 * s + p); 
                        x = (x + jitter) * pulse; y = (y + jitter) * pulse; z = (z + jitter) * pulse;
                    }} 
                    else if (SECONDARY === 'Reflection') {{
                        let d = Math.sqrt(x*x + y*y);
                        let ang = t * (400 / (d+20)) * s * 0.5; 
                        let nx = x * Math.cos(ang) - y * Math.sin(ang);
                        let ny = x * Math.sin(ang) + y * Math.cos(ang);
                        x = nx + jitter; y = ny + jitter;
                    }}
                    else if (SECONDARY === 'Transcendence') {{
                        z = ((this.oz + t * 80 * s + 250) % 500) - 250; 
                        x += jitter; y += jitter;
                    }}
                    else if (SECONDARY === 'Care') {{
                        let pulse = 1 + 0.08 * Math.sin(t * 0.8 * s + p);
                        x *= pulse; y *= pulse; z *= pulse;
                    }}
                    else {{
                        x += jitter; y += jitter; z += jitter;
                    }}
                    
                    let cosG = Math.cos(globalAngle);
                    let sinG = Math.sin(globalAngle);
                    let xFinal = x * cosG - z * sinG;
                    let zRot = x * sinG + z * cosG;
                    
                    let scale = fov / (fov + zRot);
                    let x2d = xFinal * scale + cx;
                    let y2d = y * scale + cy;
                    
                    if (scale > 0 && zRot > -fov) {{
                        ctx.beginPath();
                        ctx.arc(x2d, y2d, this.sizeBase * scale, 0, Math.PI * 2);
                        ctx.fillStyle = this.color;
                        ctx.globalAlpha = this.isThought ? 1.0 : (0.4 * scale); 
                        ctx.fill();
                        
                        if (this.isThought) {{
                            ctx.fillStyle = "#FFFFFF";
                            ctx.globalAlpha = 1.0;
                            ctx.beginPath();
                            ctx.arc(x2d, y2d, 2 * scale, 0, Math.PI * 2); 
                            ctx.fill();
                        }}
                    }}
                }}
            }}

            function initWorld() {{
                particles = [];
                let atmosCount = Math.min(500, Math.max(200, DATA.node_count * 25));
                for(let i=0; i<atmosCount; i++) particles.push(new Particle(false, null));
                THOUGHTS.forEach(t => particles.push(new Particle(true, t)));
            }}

            initWorld();

            let time = 0;
            function animate() {{
                ctx.globalAlpha = 1.0;
                ctx.fillStyle = "black";
                ctx.fillRect(0, 0, width, height);
                time += 0.01;
                globalAngle += 0.003;
                particles.forEach(p => p.update(time));
                requestAnimationFrame(animate);
            }}
            animate();
        </script>
    </body>
    </html>
    """
    components.html(html_code, height=350, scrolling=False)
    # 🟢 关键：删除了 viz.render_spectrum_legend()
