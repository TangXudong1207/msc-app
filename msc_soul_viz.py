### msc_soul_viz.py ###
import streamlit as st
import streamlit.components.v1 as components
import streamlit_antd_components as sac
import msc_viz as viz
import msc_soul_gen as gen
import json

def render_soul_scene(radar_dict, user_nodes=None):
    if user_nodes is None: user_nodes = []
    
    # 1. 计算数据
    nodes, edges, physics_config, p_attr, s_attr = gen.generate_soul_network(radar_dict, user_nodes)
    
    lang = st.session_state.get('language', 'en')
    
    # ... (保持原有的文案映射逻辑) ...
    ARCHETYPE_NAMES = {
        "Agency":        {"en": "Starburst Structure", "zh": "爆发结构"},
        "Care":          {"en": "Dense Cluster",      "zh": "凝聚结构"},
        "Curiosity":     {"en": "Wide Web",           "zh": "发散网络"},
        "Coherence":     {"en": "Crystalline Grid",   "zh": "晶格结构"},
        "Reflection":    {"en": "Deep Swirl",         "zh": "深旋结构"},
        "Transcendence": {"en": "Ascending Cloud",    "zh": "升腾云结构"},
        "Aesthetic":     {"en": "Harmonic Sphere",    "zh": "和谐球体"}
    }
    ASPECT_NAMES = {
        "Agency":        {"en": "Volatile Mode",   "zh": "躁动模式"},
        "Care":          {"en": "Gentle Mode",     "zh": "柔缓模式"},
        "Curiosity":     {"en": "Flowing Mode",    "zh": "流转模式"},
        "Coherence":     {"en": "Stable Mode",     "zh": "稳定模式"},
        "Reflection":    {"en": "Breathing Mode",  "zh": "呼吸模式"},
        "Transcendence": {"en": "Drifting Mode",   "zh": "漂浮模式"},
        "Aesthetic":     {"en": "Elegant Mode",    "zh": "优雅模式"}
    }

    p_name = ARCHETYPE_NAMES.get(p_attr, {}).get(lang, p_attr)
    s_name = ASPECT_NAMES.get(s_attr, {}).get(lang, s_attr)
    
    if len(user_nodes) == 0:
        creature_title = "Proto-Field" if lang=='en' else "初生场域"
        creature_desc = "Awaiting thought injection..." if lang=='en' else "等待思想注入..."
    else:
        creature_title = p_name
        creature_desc = f"operating in {s_name}" if lang=='en' else f"运行于 {s_name}"

    label_title = "SOUL FORM" if lang=='en' else "灵魂形态"
    sac.divider(label=label_title, icon='layers', align='center', color='gray')
    st.markdown(f"<div style='text-align:center; margin-bottom: -20px;'><b>{creature_title}</b><br><span style='font-size:0.8em;color:gray'>{creature_desc}</span></div>", unsafe_allow_html=True)
    
    # 2. 准备嵌入的 HTML/JS 代码
    # 我们使用 json.dumps 将 Python 数据转为 JS 对象
    nodes_json = json.dumps(nodes)
    edges_json = json.dumps(edges)
    physics_json = json.dumps(physics_config)
    
    # 🌟 关键参数配置区 (你可以在这里修改) 🌟
    AUTO_ROTATE_SPEED = 50  # 旋转速度
    CAMERA_DISTANCE = 700   # 相机距离 (越小越近)
    BLOOM_INTENSITY = 0.8    # 发光强度
    AXIS_RANGE = 250         # 坐标轴范围
    
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <!-- 引入最新的 ECharts 和 ECharts-GL -->
        <script src="https://cdn.jsdelivr.net/npm/echarts/dist/echarts.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/echarts-gl/dist/echarts-gl.min.js"></script>
    </head>
    <body style="margin: 0; background-color: #000000;">
        <div id="main" style="width: 100%; height: 350px;"></div>
        <script type="text/javascript">
            var chartDom = document.getElementById('main');
            var myChart = echarts.init(chartDom);
            var option;

            // 从 Python 传入的数据
            var nodes = {nodes_json};
            var edges = {edges_json};
            var physics = {physics_json};

            option = {{
                backgroundColor: '#000000',
                tooltip: {{
                    show: true,
                    formatter: function (params) {{
                        return params.name + '<br/>' + (params.value || '');
                    }},
                    backgroundColor: 'rgba(50,50,50,0.8)',
                    textStyle: {{ color: '#fff' }}
                }},
                // 3D 坐标系配置
                grid3D: {{
                    show: false,
                    viewControl: {{
                        projection: 'perspective',
                        autoRotate: true,
                        autoRotateSpeed: {AUTO_ROTATE_SPEED}, 
                        distance: {CAMERA_DISTANCE},
                        minDistance: 100,
                        maxDistance: 800,
                        alpha: 20,
                        beta: 40
                    }},
                    light: {{
                        main: {{
                            intensity: 1.5,
                            alpha: 30,
                            beta: 30
                        }},
                        ambient: {{ intensity: 0.5 }}
                    }},
                    postEffect: {{
                        enable: true,
                        bloom: {{
                            enable: true,
                            bloomIntensity: {BLOOM_INTENSITY}
                        }}
                    }},
                    environment: '#000000'
                }},
                xAxis3D: {{ show: false, min: -{AXIS_RANGE}, max: {AXIS_RANGE} }},
                yAxis3D: {{ show: false, min: -{AXIS_RANGE}, max: {AXIS_RANGE} }},
                zAxis3D: {{ show: false, min: -{AXIS_RANGE}, max: {AXIS_RANGE} }},
                series: [
                    {{
                        type: 'graphGL',
                        layout: 'force',
                        data: nodes,
                        links: edges,
                        force: {{
                            repulsion: physics.repulsion,
                            gravity: physics.gravity,
                            friction: physics.friction,
                            edgeLength: physics.edgeLength,
                            initLayout: 'spherical'
                        }},
                        itemStyle: {{ opacity: 1 }},
                        lineStyle: {{ width: 0.5, opacity: 0.2 }},
                        emphasis: {{
                            itemStyle: {{ borderColor: '#FFF', borderWidth: 2 }},
                            label: {{ show: true }}
                        }}
                    }}
                ]
            }};

            myChart.setOption(option);
            
            // 响应式调整大小
            window.addEventListener('resize', function() {{
                myChart.resize();
            }});
        </script>
    </body>
    </html>
    """
    
    # 3. 使用原生 HTML 组件渲染
    # height=350 对应正方形视窗
    components.html(html_code, height=350)
    
    # 渲染图例 (保持不变)
    viz.render_spectrum_legend()
