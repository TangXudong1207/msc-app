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
    payload, p_attr, s_attr = gen.prepare_soul_data(radar_dict, user_nodes)
    payload_json = json.dumps(payload)
    
    lang = st.session_state.get('language', 'en')
    
    # 文案
    SHAPE_NAMES = {
        "Agency": "Starburst", "Care": "Cluster", "Curiosity": "Nebula",
        "Coherence": "Grid", "Reflection": "Vortex", "Transcendence": "Ascension", "Aesthetic": "Sphere"
    }
    MOTION_NAMES = {
        "Agency": "Volatile", "Care": "Gentle", "Curiosity": "Flowing",
        "Coherence": "Frozen", "Reflection": "Swirling", "Transcendence": "Drifting", "Aesthetic": "Harmonic"
    }
    
    shape_name = SHAPE_NAMES.get(p_attr, p_attr)
    motion_name = MOTION_NAMES.get(s_attr, s_attr)
    
    title = f"{shape_name} · {motion_name}"
    # 彻底隐喻化，不解释
    
    sac.divider(label="SOUL FORM", icon='layers', align='center', color='gray')
    st.markdown(f"<div style='text-align:center; margin-bottom:10px; font-family:serif; letter-spacing:2px; font-size:0.9em; color:#AAA;'>{title.upper()}</div>", unsafe_allow_html=True)

    # ==========================================
    # 🧬 注入原生 JS 粒子引擎
    # ==========================================
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body, html {{ margin: 0; padding: 0; width: 100%; height: 100%; overflow: hidden; background-color: #000; }}
            canvas {{ display: block; }}
            #info {{
                position: absolute; bottom: 10px; left: 10px; color: rgba(255,255,255,0.5); 
                font-family: monospace; font-size: 10px; pointer-events: none;
            }}
        </style>
    </head>
    <body>
        <canvas id="soulCanvas"></canvas>
        <div id="info">MSC GENERATIVE ENGINE v1.0</div>
        <script>
            // === 1. 数据接收 ===
            const DATA = {payload_json};
            const PRIMARY = DATA.primary;
            const SECONDARY = DATA.secondary;
            const THOUGHTS = DATA.thoughts;
            const ATMOS_COLORS = DATA.atmos_colors;
            
            const canvas = document.getElementById('soulCanvas');
            const ctx = canvas.getContext('2d');
            
            let width, height, cx, cy;
            let particles = [];
            
            // === 2. 3D 投影参数 ===
            let fov = 400;
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

            // === 3. 粒子类 ===
            class Particle {{
                constructor(isThought, thoughtData) {{
                    this.isThought = isThought;
                    this.init(thoughtData);
                }}

                init(thoughtData) {{
                    // 初始位置生成 (基于 Primary Shape)
                    let u = Math.random();
                    let v = Math.random();
                    let theta = 2 * Math.PI * u;
                    let phi = Math.acos(2 * v - 1);
                    let r = 0;
                    
                    if (PRIMARY === 'Agency') {{ r = Math.random() * 200 + 20; }}
                    else if (PRIMARY === 'Care') {{ r = Math.random() * 80; }}
                    else if (PRIMARY === 'Coherence') {{ 
                        let step = 60; 
                        this.baseX = Math.round((Math.random()-0.5)*400/step)*step;
                        this.baseY = Math.round((Math.random()-0.5)*400/step)*step;
                        this.baseZ = Math.round((Math.random()-0.5)*400/step)*step;
                        r = 0; // coherence 使用网格坐标
                    }}
                    else if (PRIMARY === 'Transcendence') {{ 
                        let w = (Math.random()-0.5)*100;
                        this.x = w; this.y = (Math.random()-0.5)*100; this.z = (Math.random()-0.5)*400;
                        r = 0; // 特殊处理
                    }}
                    else {{ r = (Math.random() - 0.5) * 300; }} // Default Cloud

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
                        this.sizeBase = 4;
                        this.x *= 0.8; this.y *= 0.8; this.z *= 0.8; // 恒星内敛
                    }} else {{
                        this.color = ATMOS_COLORS[Math.floor(Math.random() * ATMOS_COLORS.length)];
                        this.sizeBase = Math.random() * 2 + 0.5;
                    }}

                    this.phase = Math.random() * Math.PI * 2;
                    this.speed = Math.random() * 0.5 + 0.5;
                    
                    // 备份初始坐标用于物理计算
                    this.ox = this.x; this.oy = this.y; this.oz = this.z;
                }}

                update(t) {{
                    // === 物理引擎核心 (基于 Secondary Motion) ===
                    let x = this.ox;
                    let y = this.oy;
                    let z = this.oz;
                    let p = this.phase;
                    let s = this.speed;

                    if (SECONDARY === 'Agency') {{ // 躁动：呼吸 + 抖动
                        let pulse = 1 + 0.2 * Math.sin(t * 3 * s + p);
                        let jitter = Math.sin(t * 10 + p) * 5;
                        x = (x + jitter) * pulse;
                        y = (y + jitter) * pulse;
                        z = (z + jitter) * pulse;
                    }} 
                    else if (SECONDARY === 'Reflection') {{ // 漩涡
                        let d = Math.sqrt(x*x + y*y);
                        let ang = t * (500 / (d+10)) * s * 0.5;
                        let nx = x * Math.cos(ang) - y * Math.sin(ang);
                        let ny = x * Math.sin(ang) + y * Math.cos(ang);
                        x = nx; y = ny;
                    }}
                    else if (SECONDARY === 'Transcendence') {{ // 升腾
                        z = ((this.oz + t * 50 * s + 200) % 400) - 200;
                    }}
                    else if (SECONDARY === 'Curiosity') {{ // 流动
                        x += Math.sin(t * 2 + p) * 20;
                        y += Math.cos(t * 2 + p) * 20;
                    }}
                    else if (SECONDARY === 'Care') {{ // 柔缓
                        let pulse = 1 + 0.05 * Math.sin(t * s + p);
                        x *= pulse; y *= pulse; z *= pulse;
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
                    if (scale > 0) {{
                        ctx.beginPath();
                        ctx.arc(x2d, y2d, this.sizeBase * scale, 0, Math.PI * 2);
                        ctx.fillStyle = this.color;
                        ctx.globalAlpha = this.isThought ? 1.0 : (0.4 * scale); // 远处理更淡
                        ctx.fill();
                        
                        // 恒星发光
                        if (this.isThought) {{
                            ctx.strokeStyle = "rgba(255,255,255,0.5)";
                            ctx.lineWidth = 1 * scale;
                            ctx.stroke();
                        }}
                    }}
                }}
            }}

            // === 4. 初始化 ===
            function initWorld() {{
                particles = [];
                // 氛围粒子 (数量)
                let atmosCount = Math.min(600, Math.max(200, DATA.node_count * 30));
                for(let i=0; i<atmosCount; i++) {{
                    particles.push(new Particle(false, null));
                }}
                // 思想粒子
                THOUGHTS.forEach(t => {{
                    particles.push(new Particle(true, t));
                }});
            }}

            initWorld();

            // === 5. 渲染循环 ===
            let time = 0;
            function animate() {{
                ctx.fillStyle = "#000000";
                ctx.fillRect(0, 0, width, height); // 清空画布
                
                time += 0.01;
                globalAngle += 0.005; // 缓慢自旋
                
                // 简单的深度排序，解决遮挡问题
                particles.sort((a, b) => b.z - a.z); // 实际上需要实时计算后的Z，这里简化处理不排序或根据索引
                // 为了性能，JS粒子通常不每帧排序，或者只做简单混合
                ctx.globalCompositeOperation = 'lighter'; // 叠加模式，增强发光感

                particles.forEach(p => p.update(time));
                
                requestAnimationFrame(animate);
            }}
            animate();
            
            // 交互：点击重置
            canvas.addEventListener('click', () => {{
                globalAngle += 1.0; // 点击加速旋转一下
            }});

        </script>
    </body>
    </html>
    """

    # 渲染 HTML 组件
    # height=350 保持正方形视窗
    components.html(html_code, height=350, scrolling=False)
    
    viz.render_spectrum_legend()
