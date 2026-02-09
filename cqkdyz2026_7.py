import streamlit as st
import numpy as np
import plotly.graph_objects as go

# --- 1. 页面配置与超深色文字样式 ---
st.set_page_config(page_title="重庆康德物理2024-7: 三星连珠", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #F6F4F0; }
    
    /* 强制所有文字为纯黑，加深颜色 */
    h1, h2, h3, p, span, label, .stMarkdown, [data-testid="stText"] {
        color: #000000 !important;
        font-weight: 600 !important;
    }

    /* 全屏铺满水印层 */
    .watermark-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        z-index: 9999;
        pointer-events: none;
        background-image: radial-gradient(circle, transparent 0%, transparent 100%), 
                          repeating-linear-gradient(45deg, rgba(0,0,0,0.03) 0px, rgba(0,0,0,0.03) 2px, transparent 2px, transparent 150px);
    }
    
    /* 动态生成文字水印 */
    .watermark-text-grid {
        position: fixed;
        top: 0;
        left: 0;
        width: 200%;
        height: 200%;
        z-index: 9998;
        pointer-events: none;
        display: flex;
        flex-wrap: wrap;
        transform: rotate(-30deg);
        opacity: 0.04; /* 调整此值改变平铺文字的深浅 */
        font-family: sans-serif;
    }
    
    .watermark-item {
        padding: 80px;
        font-size: 20px;
        font-weight: bold;
        color: #000;
    }

    /* 左下角固定水印 */
    .fixed-watermark {
        position: fixed; 
        left: 20px; 
        bottom: 20px;
        color: #000000; 
        font-size: 14px; 
        font-weight: bold;
        z-index: 10000; 
        opacity: 0.9; 
        pointer-events: none;
    }
    </style>

    <div class="watermark-overlay"></div>
    <div class="watermark-text-grid">
        <div class="watermark-item">xiaohongshu / douyin ID: 851015711 / 383604055</div>
        <div class="watermark-item">xiaohongshu / douyin ID: 851015711 / 383604055</div>
        <div class="watermark-item">xiaohongshu / douyin ID: 851015711 / 383604055</div>
        <div class="watermark-item">xiaohongshu / douyin ID: 851015711 / 383604055</div>
        <div class="watermark-item">xiaohongshu / douyin ID: 851015711 / 383604055</div>
        <div class="watermark-item">xiaohongshu / douyin ID: 851015711 / 383604055</div>
        <div class="watermark-item">xiaohongshu / douyin ID: 851015711 / 383604055</div>
        <div class="watermark-item">xiaohongshu / douyin ID: 851015711 / 383604055</div>
        <div class="watermark-item">xiaohongshu / douyin ID: 851015711 / 383604055</div>
        <div class="watermark-item">xiaohongshu / douyin ID: 851015711 / 383604055</div>
        <div class="watermark-item">xiaohongshu / douyin ID: 851015711 / 383604055</div>
        <div class="watermark-item">xiaohongshu / douyin ID: 851015711 / 383604055</div>
    </div>

    <div class="fixed-watermark">
        小红书/抖音/B站：赛诺的物理可视化<br>
        xiaohongshu | douyin ID: 851015711 | 383604055
    </div>
""", unsafe_allow_html=True)

# --- 2. 物理参数 ---
T_A_H, T_B_H, T_S_H = 19.2, 18.0, 24.0
T_a, T_b, T_s = T_A_H/24, T_B_H/24, T_S_H/24
R_a, R_b, R_s = T_a**(2/3), T_b**(2/3), T_s**(2/3)

steps = 600
t_space = np.linspace(0, 12, steps) 

def get_pos(T, R):
    theta = 2 * np.pi * t_space / T
    return R * np.cos(theta), R * np.sin(theta)

xa, ya = get_pos(T_a, R_a)
xb, yb = get_pos(T_b, R_b)
xs, ys = get_pos(T_s, R_s)

# --- 3. 绘图 ---
fig = go.Figure()

# 绘制轨道
for r, color in zip([R_a, R_b, R_s], ["#6A5ACD", "#4682B4", "#CD853F"]):
    theta_line = np.linspace(0, 2*np.pi, 100)
    fig.add_trace(go.Scatter(
        x=r*np.cos(theta_line), y=r*np.sin(theta_line), 
        mode='lines', line=dict(color=color, width=1.5, dash='dot'), hoverinfo='skip'))

# 绘制中心天体
fig.add_trace(go.Scatter(x=[0], y=[0], mode='markers', marker=dict(size=30, color='#2E86AB'), name="地球"))

# 卫星初始
fig.add_trace(go.Scatter(x=[xa[0]], y=[ya[0]], mode='markers+text', name="卫星 a", text="a", 
                         marker=dict(color="#5A5294", size=12), textfont=dict(color="black", size=14, weight="bold")))
fig.add_trace(go.Scatter(x=[xb[0]], y=[yb[0]], mode='markers+text', name="卫星 b", text="b", 
                         marker=dict(color="#327B8C", size=12), textfont=dict(color="black", size=14, weight="bold")))
fig.add_trace(go.Scatter(x=[xs[0]], y=[ys[0]], mode='markers+text', name="同步卫星", text="S", 
                         marker=dict(color="#C1666B", size=14), textfont=dict(color="black", size=16, weight="bold")))

# 时间显示
fig.add_trace(go.Scatter(x=[0], y=[1.4], mode="text", text=[f"t = {t_space[0]:.2f} 天"],
    textfont=dict(color="#000", size=22, family="Arial Black"), showlegend=False, name="时间"))

# --- 4. 动画 ---
frames = [go.Frame(
    data=[
        go.Scatter(x=[xa[k]], y=[ya[k]]), 
        go.Scatter(x=[xb[k]], y=[yb[k]]), 
        go.Scatter(x=[xs[k]], y=[ys[k]]),
        go.Scatter(x=[0], y=[1.4], text=[f"t = {t_space[k]:.2f} 天"])
    ],
    traces=[4,5,6,7], 
    name=f"f{k}"
) for k in range(steps)]

fig.frames = frames

fig.update_layout(
    xaxis=dict(range=[-1.6, 1.6], visible=False),
    yaxis=dict(range=[-1.6, 1.6], visible=False),
    height=750,
    plot_bgcolor="#F6F4F0",
    paper_bgcolor="#F6F4F0",
    legend=dict(font=dict(color="#000", size=14, family="Arial Black"), orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    updatemenus=[dict(
        type="buttons", direction="left", x=0.05, y=0.05, showactive=False,
        bgcolor="#1a1a1a", bordercolor="#000", font=dict(color="white", size=13),
        buttons=[
            dict(label="▶ 开始慢速模拟", method="animate", args=[None, {"frame": {"duration": 60, "redraw": False}, "fromcurrent": True}]),
            dict(label=" 重置", method="animate", args=[["f0"], {"frame": {"duration": 0, "redraw": False}, "mode": "immediate"}])
        ]
    )]
)

st.markdown("<h1 style='text-align: center;'>重庆康德物理2024-7: 三星连珠</h1>", unsafe_allow_html=True)
st.plotly_chart(fig, use_container_width=True)

# --- 5. 底部面板 ---
c1, c2 = st.columns(2)
with c1:
    st.markdown('<div style="background-color:#E0DDD7;padding:20px;border-radius:10px;border:2px solid #000;"><h3 style="margin-top:0;">物理数据看板</h3><p>卫星 a: 19.2h</p><p>卫星 b: 18.0h</p><p>同步卫星: 24.0h</p></div>', unsafe_allow_html=True)
with c2:
    st.markdown('<div style="background-color:#E0DDD7;padding:20px;border-radius:10px;border:2px solid #000;"><h3 style="margin-top:0;">临界条件分析</h3><p>模拟显示：三颗卫星每隔 <b>12.00 天</b> 会重新回到同一条直线上。</p></div>', unsafe_allow_html=True)
