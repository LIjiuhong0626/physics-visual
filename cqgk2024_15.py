import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# ========== 每个分支只改这一行 ==========
PASSWORD = "stu_2025_cq15_XXXX"
# =======================================

pw = st.text_input("请输入访问密码", type="password")
if pw != PASSWORD:
    st.warning("密码错误，请联系赛诺获取正确密码")
    st.stop()

# --- 页面配置 ---
st.set_page_config(page_title="重庆高考2024-15题", layout="wide")

hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        </style>
        """
st.markdown(hide_menu_style, unsafe_allow_html=True)

# ====================== 莫兰迪浅色系（最终定稿）======================
BG_MAIN      = "#F6F4F0"      # 主背景（暖米白）
BG_SIDEBAR   = "#EFEBE5"      # 侧边栏（浅莫兰迪）
TEXT_NORMAL  = "#3A3A38"      # 文字（深灰，绝对清晰）
TEXT_TITLE   = "#555550"      # 标题
GRID_LINE    = "#D9D5CF"      # 网格

# 莫兰迪轨迹色（低饱和、白底清晰）
COLOR_M      = "#336699"  # 深钢蓝 (Steel Blue)
COLOR_N      = "#228B72"  # 深海绿 (Ocean Green)
COLOR_PROJ   = "#CC3333"  # 朱红 (Crimson Red)

plt.rcParams.update({
    "axes.facecolor": BG_MAIN,
    "figure.facecolor": BG_MAIN,
    "text.color": TEXT_NORMAL,
    "axes.labelcolor": TEXT_NORMAL,
    "xtick.color": TEXT_NORMAL,
    "ytick.color": TEXT_NORMAL,
    "grid.color": GRID_LINE,
    "font.sans-serif": ["SimHei", "Microsoft YaHei", "Arial Unicode MS", "Deja Sans"],
    "axes.unicode_minus": False
})

# --- 全局 CSS ---
st.markdown(f"""
<style>
    
    .stApp {{
        background-color: {BG_MAIN};
        color: {TEXT_NORMAL};
    }}
    [data-testid="stSidebar"] > div:first-child {{
        background-color: {BG_SIDEBAR};
        color: {TEXT_NORMAL};
    }}
    h1, h2, h3, h4 {{
        color: {TEXT_TITLE} !important;
    }}
    p, span, div, label {{
        color: {TEXT_NORMAL} !important;
    }}
    .stMetric {{
        background-color: #F1EDE8;
        border: 1px solid {GRID_LINE};
        border-radius: 6px;
        padding: 10px;
    }}
    body::after {{
        content: "小红书/抖音/B站：赛诺的物理可视化";
        position: fixed;
        left: 15px;
        bottom: 15px;
        font-size: 14px;
        color: #888888;
        opacity: 0.7;
        z-index: 999999 !important; /* 最高层级 */
        pointer-events: none;
        background: transparent;
    }}


</style>
""", unsafe_allow_html=True)

st.title("重庆高考物理2024-15题")

# --- 侧边栏 ---
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
        h = 5/3
    else:
        n = 1
        h = 30/7

# --- 核心物理引擎（完全不变）---
def compute_corrected_trajectory(a, n, h):
    L0 = 10 * a
    dt = 0.02
    nh = n * h
    is_breakable = nh >= (5/3 * a)
    
    traj_points = []
    current_R = L0
    
    for i in range(n):
        angles_up = np.arange(-np.pi/2, np.pi/2, dt)
        for theta in angles_up:
            traj_points.append([current_R * np.cos(theta), 10*a + current_R * np.sin(theta), 0, current_R])
            
        R_down = current_R - h
        if R_down <= 0: break
        angles_down = np.arange(np.pi/2, 1.5*np.pi, dt)
        for theta in angles_down:
            traj_points.append([R_down * np.cos(theta), (10*a + h) + R_down * np.sin(theta), 1, R_down])
        current_R -= 2 * h

    final_R = 10*a - 2*nh
    
    if final_R <= 0:
        return np.array(traj_points), np.array([]), 0, 0, "GEOM_ERR"
    if not is_breakable:
        return np.array(traj_points), np.array([]), final_R, 0, "FORCE_ERR"

    s_sq = 16 * (20 * a * nh - nh**2)
    s_calc = np.sqrt(max(0, s_sq))
    
    S_MAX_PHYSICAL = 4 * np.sqrt(20 * 1.0 * (30/7) - (30/7)**2) 

    if nh > 30/7 * a:
        s_val = S_MAX_PHYSICAL
        status = "MAX_REACHED"
    else:
        s_val = s_calc
        status = "SUCCESS"

    h_fall = 10*a - final_R
    t_fall = np.sqrt(2 * h_fall / g)
    v_break = s_val / t_fall
    
    t_vals = np.arange(0, t_fall, dt)
    fall_points = np.column_stack((v_break * t_vals, h_fall - 0.5 * g * t_vals**2))
    
    return np.array(traj_points), fall_points, final_R, s_val, status

traj_data, fall_data, R_final, s_val, status = compute_corrected_trajectory(a, n, h)

# --- 绘图 ---
col_map, col_data = st.columns([3, 1])

with col_map:

    if status == "GEOM_ERR":
        st.error("几何错误：绳子已耗尽。")
    elif status == "FORCE_ERR":
        st.warning("物理警告：nh < 1.67a，拉力不足以使绳子断裂。")
    elif status == "MAX_REACHED":
        st.info("提示：nh > 4.29a，超出圆周运动模型边界，位移取极大值。")

    fig, ax = plt.subplots(figsize=(10, 8))
    # 图表内部水印（截图一定会带上，防搬运）
    # 图表内部右下角水印
    
    ax.set_aspect('equal')
    ax.set_xlim(-15 * a, max(40 * a, s_val + 5*a))
    ax.set_ylim(-2 * a, 22 * a)
    ax.axhline(0, color=GRID_LINE, lw=1)
    # 坐标系内部右下角水印
    # 坐标系内左上角水印
    ax.text(0.02, 0.98, 'xiaohongshu ID: 851015711 | douyin ID: 383604055', 
        transform=ax.transAxes,
        fontsize=9, color='#666666', ha='left', va='top', alpha=0.7)
    
    ax.scatter([0, 0], [10*a, 10*a+h], c=[COLOR_M, COLOR_N], s=100, zorder=10)
    ax.text(0.5, 10*a, "M", color=COLOR_M, fontsize=12, weight="bold")
    ax.text(0.5, 10*a+h, "N", color=COLOR_N, fontsize=12, weight="bold")
    
    if len(traj_data) > 0:
        mask_m = traj_data[:, 2] == 0
        mask_n = traj_data[:, 2] == 1
        ax.plot(traj_data[mask_m, 0], traj_data[mask_m, 1], color=COLOR_M, lw=2.5, label="Loop M")
        ax.plot(traj_data[mask_n, 0], traj_data[mask_n, 1], color=COLOR_N, lw=2.5, label="Loop N")
    
    if status in ["SUCCESS", "MAX_REACHED"]:
        ax.plot(fall_data[:, 0], fall_data[:, 1], color=COLOR_PROJ, lw=3, linestyle='--', label="Projectile")
        ax.scatter([s_val], [0], color=COLOR_PROJ, s=180, marker='*', zorder=20)
        ax.text(s_val, -1.5, f"P (s={s_val:.2f}a)", ha='center', color=COLOR_PROJ, fontsize=11, weight='bold')

    total_len = len(traj_data) + len(fall_data)
    frame = st.slider("拖动查看运动过程", 0, total_len - 1, 0 if total_len > 0 else 0)
    
    if total_len > 0:
        if frame < len(traj_data):
            curr_pos = traj_data[frame, :2]
            pivot = [0, 10*a] if traj_data[frame, 2] == 0 else [0, 10*a+h]
            ax.plot([pivot[0], curr_pos[0]], [pivot[1], curr_pos[1]], color="#555550", alpha=0.4, lw=1)
        else:
            curr_pos = fall_data[frame - len(traj_data)]
        ball = patches.Circle(curr_pos, 0.4*a, color=COLOR_PROJ, zorder=15)
        ax.add_patch(ball)

    def add_sparse_watermark(ax, text, density=5):
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
        x_coords = np.linspace(xlim[0], xlim[1], density)
        y_coords = np.linspace(ylim[0], ylim[1], density)
        
        for i, x in enumerate(x_coords):
            for j, y in enumerate(y_coords):
                # 奇数列向上偏移一点，形成交错效果
                y_final = y + (ylim[1]-ylim[0])/density/2 if i % 2 == 0 else y
                ax.text(x, y_final, text, fontsize=11, color='#888888',
                        alpha=0.12, rotation=25, ha='center', va='center', zorder=0, clip_on=True)
    add_sparse_watermark(ax, "xiaohongshu: 851015711 · douyin: 383604055", density=5)

    ax.legend(loc='upper right', facecolor=BG_MAIN, edgecolor=GRID_LINE)
    st.pyplot(fig)

with col_data:
    st.subheader("数值看板")
    st.metric("当前 nh", f"{n*h:.2f} a")
    
    if status in ["SUCCESS", "MAX_REACHED"]:
        st.metric("水平位移 s", f"{s_val:.2f} a")
        st.metric("剩余长度 Rₙ", f"{R_final:.2f} a")
    else:
        st.metric("水平位移 s", "N/A")
        
    st.markdown("---")
    st.write("**物理方程：**")
    st.latex(r"s^2 = 16(20a \cdot nh - (nh)^2)")
    st.write("**理论参考：**")
    st.latex(r"nh_{\text{min}} = 1.67a")
    st.latex(r"s_{\text{max}} \approx 25.95a")
