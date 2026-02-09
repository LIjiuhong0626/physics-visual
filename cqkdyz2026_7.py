import streamlit as st
import numpy as np
import plotly.graph_objects as go

# --- 1. 页面配置与超深色文字样式 ---
st.set_page_config(page_title="重庆康德一诊2026-7:三星连珠", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #F6F4F0; }
    
    /* 强制所有文字为纯黑，加深颜色 */
    h1, h2, h3, p, span, label, .stMarkdown, [data-testid="stText"] {
        color: #000000 !important;
        font-weight: 600 !important;
    }

    /* 侧边栏文字加深 */
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        color: #000000 !important;
        font-weight: bold !important;
    }

    /* 水印加深 */
    .watermark {
        position: fixed; bottom: 20px; right: 20px;
        color: #000000; font-size: 14px; font-weight: bold;
        z-index: 100; opacity: 0.8; pointer-events: none;
    }
    </style>
    <div class="watermark">
        小红书/抖音/B站：赛诺的物理可视化<br>
        ID: 851015711 | 383604055
    </div>
""", unsafe_allow_html=True)

# --- 2. 物理参数 ---
T_A_H, T_B_H, T_S_H = 19.2, 18.0, 24.0
T_a, T_b, T_s = T_A_H/24, T_B_H/24, T_S_H/24
R_a, R_b, R_s = T_a**(2/3), T_b**(2/3), T_s**(2/3)

# 增加采样点让转动更丝滑
steps = 600
t_space = np.linspace(0, 12, steps) 

# 计算坐标 (地球在 0,0 保持不动)
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
        x=r*np.cos(theta_line), 
        y=r*np.sin(theta_line), 
        mode='lines', 
        line=dict(color=color, width=1.8, dash='dot'), 
        hoverinfo='skip'
    ))

# 绘制地球
fig.add_trace(go.Scatter(x=[0], y=[0], mode='markers', marker=dict(size=40, color='#2E86AB'), name="地球"))

# 卫星初始位置
fig.add_trace(go.Scatter(x=[xa[0]], y=[ya[0]], mode='markers+text', name="卫星 a", text="a", 
                         marker=dict(color="#5A5294", size=12), textfont=dict(color="black", size=14, weight="bold")))
fig.add_trace(go.Scatter(x=[xb[0]], y=[yb[0]], mode='markers+text', name="卫星 b", text="b", 
                         marker=dict(color="#327B8C", size=12), textfont=dict(color="black", size=14, weight="bold")))
fig.add_trace(go.Scatter(x=[xs[0]], y=[ys[0]], mode='markers+text', name="同步卫星", text="S", 
                         marker=dict(color="#C1666B", size=14), textfont=dict(color="black", size=16, weight="bold")))

# 时间标注（初始帧）
fig.add_trace(go.Scatter(
    x=[0], y=[1.4], mode="text",
    text=[f"t = {t_space[0]:.2f} 天"],
    textfont=dict(color="#000", size=22, family="Arial Black"),
    showlegend=False, name="时间"
))

# --- 4. 动画逻辑（每一帧都更新时间） ---
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
    legend=dict(
        font=dict(color="#000000", size=14, family="Arial Black"),
        orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
    ),

    updatemenus=[dict(
    type="buttons",
    showactive=False,
    x=0.05, y=0.05,
    # 正确的按钮样式写法
    bgcolor="#1a1a1a",
    bordercolor="#000",
    borderwidth=2,
    font=dict(color="white", size=13, weight="bold"),

    buttons=[
        dict(
            label="▶ 开始慢速模拟", 
            method="animate", 
            args=[None, {"frame": {"duration": 60, "redraw": False}, "fromcurrent": True}]
        ),
        dict(
            label="🔁 重置", 
            method="animate", 
            args=[[f"f{0}"], {"frame": {"duration": 0, "redraw": False}, "mode": "immediate"}]
        )
    ]
)]
)

st.markdown("<h1 style='text-align: center;'>重庆康德一诊2026-7:三星连珠</h1>", unsafe_allow_html=True)
st.plotly_chart(fig, use_container_width=True)

# --- 5. 底部面板 ---
col1, col2 = st.columns(2)
with col1:
    st.markdown("""
    <div style="background-color: #E0DDD7; padding: 20px; border-radius: 10px; border: 2px solid #000000;">
        <h3 style="margin-top:0; color:#000000;">物理数据看板</h3>
        <p>卫星 a 周期: <b>19.2h</b></p>
        <p>卫星 b 周期: <b>18.0h</b></p>
        <p>同步卫星 周期: <b>24.0h</b></p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style="background-color: #E0DDD7; padding: 20px; border-radius: 10px; border: 2px solid #000000;">
        <h3 style="margin-top:0; color:#000000;">临界条件分析</h3>
        <p>各卫星绕地旋转，地球保持静止。当它们再次扫过相同相位时对齐。</p>
        <p>计算得出：<b>12.00 天</b> 后三者将再次形成“三星连珠”。</p>
    </div>
    """, unsafe_allow_html=True)
