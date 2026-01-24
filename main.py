import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        </style>
        """
st.markdown(hide_menu_style, unsafe_allow_html=True)

# --- 页面配置 ---
st.set_page_config(page_title="重庆高考2024-15题", layout="wide")

# --- 配色方案 (Morandi Dark) ---
BG_COLOR = "#1e1e1e"
PRIMARY_COLOR = "#FF9F80"  # 珊瑚粉 (B球/平抛)
SECONDARY_COLOR = "#70A4B2"  # 青蓝 (绕M轨迹)
TEXT_COLOR = "#E6E6E6"
GRID_COLOR = "#3A3A3A"
ACCENT_COLOR = "#A8D8B9"   # 薄荷绿 (绕N轨迹)

plt.rcParams.update({
    "axes.facecolor": BG_COLOR, "figure.facecolor": BG_COLOR,
    "text.color": TEXT_COLOR, "axes.labelcolor": TEXT_COLOR,
    "xtick.color": TEXT_COLOR, "ytick.color": TEXT_COLOR,
    "grid.color": GRID_COLOR, "font.sans-serif": ["Arial Unicode MS", "Heiti TC"]
})

# --- 自定义 CSS ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: {BG_COLOR}; color: {TEXT_COLOR}; }}
    h1, h2, h3 {{ color: {PRIMARY_COLOR} !important; }}
    .stMetric {{ background-color: #2a2a2a; border: 1px solid {GRID_COLOR}; padding: 10px; border-radius: 5px; }}
    </style>
""", unsafe_allow_html=True)

st.title("分段缠绕与临界断裂可视化")

# --- 侧边栏交互 ---
with st.sidebar:
    st.header("参数设置")
    config_mode = st.radio("场景选择", ["自定义探索", "临界最小值 (nh=5a/3)", "临界最大值 (n=1)"])
    
    a = 1.0
    g = 9.8
    
    if config_mode == "自定义探索":
        n = st.number_input("旋转圈数 n", 1, 5, 1)
        h = st.slider("MN 间距 h (a)", 0.1, 5.0, 1.0, step=0.01)
    elif "最小值" in config_mode:
        n = 1
        h = 5/3  # nh = 5/3a
    else:
        n = 1
        h = 30/7 # n=1 时的最大 nh

# --- 核心物理引擎 (整合断裂判定) ---
def compute_corrected_trajectory(a, n, h):
    L0 = 10 * a
    dt = 0.02
    nh = n * h
    
    # 【核心判定】只有 nh >= 5/3a 时，最低点拉力才可能达到 12mg
    is_breakable = nh >= (5/3 * a)
    
    traj_points = []
    current_R = L0
    
    # 模拟 n 圈旋转轨迹
    for i in range(n):
        # 阶段 1：右半圆 (绕 M)
        angles_up = np.arange(-np.pi/2, np.pi/2, dt)
        for theta in angles_up:
            traj_points.append([current_R * np.cos(theta), 10*a + current_R * np.sin(theta), 0, current_R])
            
        # 阶段 2：左半圆 (绕 N)
        R_down = current_R - h
        if R_down <= 0: break
        angles_down = np.arange(np.pi/2, 1.5*np.pi, dt)
        for theta in angles_down:
            traj_points.append([R_down * np.cos(theta), (10*a + h) + R_down * np.sin(theta), 1, R_down])
        
        current_R -= 2 * h

    final_R = 10*a - 2*nh
    
    # 几何与物理合法性检查
    if final_R <= 0:
        return np.array(traj_points), np.array([]), 0, 0, "GEOM_ERR"
    if not is_breakable:
        return np.array(traj_points), np.array([]), final_R, 0, "FORCE_ERR"

    # 满足断裂条件，计算平抛
    # v_n^2 = 60ga + 2gR_n [根据答案推导]
    v_break = np.sqrt(60*g*a + 2*g*final_R)
    h_fall = 10*a - final_R
    t_fall = np.sqrt(2 * h_fall / g)
    t_vals = np.arange(0, t_fall, dt)
    
    fall_x = v_break * t_vals
    fall_y = h_fall - 0.5 * g * t_vals**2
    fall_points = np.column_stack((fall_x, fall_y))
    
    # 理论位移公式: s = 4 * sqrt(20anh - (nh)^2)
    s_theory = 4 * np.sqrt(20*a*nh - nh**2)
    
    return np.array(traj_points), fall_points, final_R, s_theory, "SUCCESS"

# 计算数据
traj_data, fall_data, R_final, s_val, status = compute_corrected_trajectory(a, n, h)

# --- 绘图与交互 ---
col_map, col_data = st.columns([3, 1])

with col_map:
    if status == "GEOM_ERR":
        st.error(f"几何错误：当 h={h:.2f}a 时，绳子在第 {n} 圈前就已耗尽。")
    elif status == "FORCE_ERR":
        st.warning(f"物理警告：当前 nh = {n*h:.2f}a < 1.67a。拉力不足 12mg，绳索不会断裂！")
    
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.set_aspect('equal')
    ax.set_xlim(-15 * a, max(40 * a, s_val + 5*a))
    ax.set_ylim(-2 * a, 22 * a)
    ax.axhline(0, color=GRID_COLOR, lw=1) # 地面
    
    # 绘制钉子
    ax.scatter([0, 0], [10*a, 10*a+h], c=[SECONDARY_COLOR, ACCENT_COLOR], s=100, zorder=10)
    ax.text(0.5, 10*a, "M", color=SECONDARY_COLOR)
    ax.text(0.5, 10*a+h, "N", color=ACCENT_COLOR)
    
    # 分段绘制轨迹
    if len(traj_data) > 0:
        mask_m = traj_data[:, 2] == 0
        mask_n = traj_data[:, 2] == 1
        ax.plot(traj_data[mask_m, 0], traj_data[mask_m, 1], color=SECONDARY_COLOR, lw=1, alpha=0.5, label="绕M段")
        ax.plot(traj_data[mask_n, 0], traj_data[mask_n, 1], color=ACCENT_COLOR, lw=1, alpha=0.5, label="绕N段")
    
    # 绘制平抛轨迹与落点
    if status == "SUCCESS":
        ax.plot(fall_data[:, 0], fall_data[:, 1], color=PRIMARY_COLOR, lw=2, label="平抛轨迹")
        ax.scatter([s_val], [0], color=PRIMARY_COLOR, s=150, marker='*', zorder=20)
        ax.text(s_val, -1.5, f"P (s={s_val:.2f}a)", ha='center', color=PRIMARY_COLOR, fontweight='bold')

    # 进度条交互
    total_len = len(traj_data) + len(fall_data)
    frame = st.slider("拖动查看运动过程", 0, total_len - 1, 0 if total_len > 0 else 0)
    
    if total_len > 0:
        if frame < len(traj_data):
            curr_pos = traj_data[frame, :2]
            pivot = [0, 10*a] if traj_data[frame, 2] == 0 else [0, 10*a+h]
            ax.plot([pivot[0], curr_pos[0]], [pivot[1], curr_pos[1]], 'w-', alpha=0.3)
        else:
            curr_pos = fall_data[frame - len(traj_data)]
        
        ball = patches.Circle(curr_pos, 0.4*a, color=PRIMARY_COLOR, zorder=15)
        ax.add_patch(ball)

    ax.legend(loc='upper right')
    st.pyplot(fig)

with col_data:
    st.subheader("临界状态看板")
    st.write(f"当前积 $nh = {n*h:.2f}a$")
    
    # 只有成功断裂才显示具体位移
    if status == "SUCCESS":
        st.metric("水平位移 s", f"{s_val:.2f} a")
        st.metric("断裂高度", f"{10*a - R_final:.2f} a")
    else:
        st.metric("水平位移 s", "N/A (未断裂)")
        
    st.markdown("---")
    st.write("**理论边界：**")
    st.latex(r"nh_{min} = 1.67a")
    st.latex(r"s_{min} = 22.11a")
    
    if status == "SUCCESS":
        st.info("满足断裂条件：\n$nh \ge 1.67a$")
