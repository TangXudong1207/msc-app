### msc_soul_viz.py ###
import streamlit as st
import streamlit.components.v1 as components
import streamlit_antd_components as sac
import msc_viz as viz
import msc_soul_gen as gen
import json

def render_soul_scene(radar_dict, user_nodes=None):
    if user_nodes is None: user_nodes = []
    
    # 1. 准备数据
    try:
        payload, p_attr, s_attr = gen.prepare_soul_data(radar_dict, user_nodes)
    except AttributeError:
        st.error("System Updating... Please refresh.")
        return
        
    payload_json = json.dumps(payload)
    lang = st.session_state.get('language', 'en')
    
    # 文案
    SHAPE_NAMES = {
        "Agency": "Starburst", "Care": "Cluster", "Curiosity": "Nebula",
        "Coherence": "Grid", "Reflection": "Vortex", "Transcendence": "Ascension", "Aesthetic": "Sphere"
    }
    title = SHAPE_NAMES.get(p_attr, p_attr)
    
    sac.divider(label="SOUL FORM", icon='layers', align='center', color='gray')
    st.markdown(f"<div style='text-align:center; margin-bottom:10px; font-family:serif; letter-spacing:2px; font-size:0.9em; color:#AAA;'>{title.upper()}</div>", unsafe_allow_html=True)

    # ==========================================
    # 🧬 注入原生 JS 粒子引擎 (无拖影版)
    # ==========================================
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
            let fov = 350; // 视场深度
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
                    // 初始位置生成
                    let u = Math.random();
                    let v = Math.random();
                    let theta = 2 * Math.PI * u;
                    let phi = Math.acos(2 * v - 1);
                    let r = 0;
                    
                    // 基于 Primary 决定分布范围
                    if (PRIMARY === 'Agency') {{ r = Math.random() * 220 + 20; }}
                    else if (PRIMARY === 'Care') {{ r = Math.random() * 90; }}
                    else if (PRIMARY === 'Coherence') {{ 
                        let step = 50; 
                        this.baseX = Math.round((Math.random()-0.5)*350/step)*step;
                        this.baseY = Math.round((Math.random()-0.5)*350/step)*step;
                        this.baseZ = Math.round((Math.random()-0.5)*350/step)*step;
                        r = 0; 
                    }}
                    else if (PRIMARY === 'Transcendence') {{ 
                        this.x = (Math.random()-0.5)*120; 
                        this.y = (Math.random()-0.5)*120; 
                        this.z = (Math.random()-0.5)*400;
                        r = 0;
                    }}
                    else {{ r = (Math.random() - 0.5) * 350; }}

                    if (PRIMARY !== 'Coherence' && PRIMARY !== 'Transcendence') {{
                        this.x = r * Math.sin(phi) * Math.cos(theta);
                        this.y = r * Math.sin(phi) * Math.sin(theta);
                        this.z = r * Math.cos(phi);
                    }} else if (PRIMARY === 'Coherence') {{
                        this.x = this.baseX; this.y = this.baseY; this.z = this.baseZ;
                    }}

                    // 属性
                    if (this.isThought) {{
                        this.color = thoughtData.color;
                        this.sizeBase = 3.5;
                        this.x *= 0.7; this.y *= 0.7; this.z *= 0.7;
                    }} else {{
                        this.color = ATMOS_COLORS[Math.floor(Math.random() * ATMOS_COLORS.length)];
                        this.sizeBase = Math.random() * 1.5 + 0.5; // 变小一点，像尘埃
                    }}

                    this.phase = Math.random() * Math.PI * 2;
                    this.speed = Math.random() * 0.5 + 0.5;
                    this.ox = this.x; this.oy = this.y; this.oz = this.z;
                }}

                update(t) {{
                    let x = this.ox;
                    let y = this.oy;
                    let z = this.oz;
                    let p = this.phase;
                    let s = this.speed;

                    // 物理动态 (Motion)
                    // 增加随机扰动 (Jitter)，防止形成完美线条
                    let jitter = Math.sin(t * 5 + p) * 2; 

                    if (SECONDARY === 'Agency') {{ 
                        let pulse = 1 + 0.15 * Math.sin(t * 2 * s + p);
                        x = (x + jitter) * pulse; y = (y + jitter) * pulse; z = (z + jitter) * pulse;
                    }} 
                    else if (SECONDARY === 'Reflection') {{
                        let d = Math.sqrt(x*x + y*y);
                        let ang = t * (300 / (d+10)) * s * 0.3;
                        let nx = x * Math.cos(ang) - y * Math.sin(ang);
                        let ny = x * Math.sin(ang) + y * Math.cos(ang);
                        x = nx + jitter; y = ny + jitter;
                    }}
                    else if (SECONDARY === 'Transcendence') {{
                        z = ((this.oz + t * 40 * s + 200) % 400) - 200;
                        x += jitter; y += jitter;
                    }}
                    else if (SECONDARY === 'Care') {{
                        let pulse = 1 + 0.05 * Math.sin(t * s + p);
                        x *= pulse; y *= pulse; z *= pulse;
                    }}
                    else {{
                        x += jitter; y += jitter; z += jitter;
                    }}
                    
                    // 全局旋转
                    let cosG = Math.cos(globalAngle);
                    let sinG = Math.sin(globalAngle);
                    let xFinal = x * cosG - z * sinG;
                    let zRot = x * sinG + z * cosG;
                    
                    // 3D 投影
                    let scale = fov / (fov + zRot);
                    let x2d = xFinal * scale + cx;
                    let y2d = y * scale + cy;
                    
                    // 渲染
                    if (scale > 0 && zRot > -fov) {{
                        ctx.beginPath();
                        ctx.arc(x2d, y2d, this.sizeBase * scale, 0, Math.PI * 2);
                        
                        // 🟢 关键修改：普通填充，不使用 lighter
                        ctx.fillStyle = this.color;
                        // 降低透明度，制造雾气感
                        ctx.globalAlpha = this.isThought ? 1.0 : (0.3 * scale); 
                        ctx.fill();
                        
                        // 恒星核心加一点点光晕，但不是全局叠加
                        if (this.isThought) {{
                            ctx.strokeStyle = "rgba(255,255,255,0.4)";
                            ctx.lineWidth = 0.5 * scale;
                            ctx.stroke();
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
                // 🟢 关键修改：每一帧用纯黑覆盖，消除所有拖影
                ctx.globalAlpha = 1.0;
                ctx.fillStyle = "black";
                ctx.fillRect(0, 0, width, height);
                
                time += 0.01;
                globalAngle += 0.003; // 极慢自旋
                
                // 恢复叠加模式为默认
                ctx.globalCompositeOperation = 'source-over'; 

                particles.forEach(p => p.update(time));
                requestAnimationFrame(animate);
            }}
            animate();
        </script>
    </body>
    </html>
    """
    components.html(html_code, height=350, scrolling=False)
    viz.render_spectrum_legend()
