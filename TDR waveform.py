#%%
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Rectangle

# --- 1. 定义物理和波形参数 ---
cable_length = 35.0  # cable部分长度
sensor_body_length = 10.0  # sensor body长度  
probe_apparent_length = 70.0 # 对应参考图中的红色曲线 (La = 70 cm)
plot_start_position = 30.0  # 图的起始位置
cable_apparent_length = plot_start_position + cable_length + sensor_body_length  # 第一次反射点
total_apparent_length = cable_apparent_length + probe_apparent_length  # 第二次反射点
plot_end_distance = 200.0 # 图的x轴范围
num_frames = 250

# --- 2. 创建更真实的静态TDR波形 ---
def create_realistic_waveform(x_data, x1, x2):
    """根据参考图(红色曲线)生成一个真实的TDR波形"""
    y = np.zeros_like(x_data)

    # a) 添加cable部分的平直线
    mask_cable = x_data < x1 - 5
    y[mask_cable] = 0.0

    # b) x1 处的初始反射峰 (高斯函数模拟)
    peak1_amplitude = 0.12
    peak1_std_dev = 1.5
    y += peak1_amplitude * np.exp(-0.5 * ((x_data - x1) / peak1_std_dev)**2)

    # c) x1 和 x2 之间的过渡区
    mask_between = (x_data > x1 + 2) & (x_data < x2 - 2)
    if np.sum(mask_between) > 0:
        x_between = x_data[mask_between]
        normalized_x = (x_between - (x1 + 2)) / ((x2 - 2) - (x1 + 2))
        
        start_val = 0.05  # 第一个峰后的起始值
        end_val = -0.05   # 第二个反射点前的结束值
        
        decay_factor = 0.8  # 控制衰减速度
        y[mask_between] = start_val + (end_val - start_val) * (normalized_x ** decay_factor)

    reflection_mask = (x_data >= x2 - 2) & (x_data <= x2 + 5)
    if np.sum(reflection_mask) > 0:
        x_reflection = x_data[reflection_mask]
        transition_factor = (x_reflection - x2) / 2.0
        reflection_amplitude = 0.25
        y[reflection_mask] += reflection_amplitude * (np.tanh(transition_factor * 3) + 1) / 2

    mask_after = x_data > x2 + 5
    if np.sum(mask_after) > 0:
        stable_level = 0.2
        y[mask_after] = stable_level

    return y

x_waveform = np.linspace(0, plot_end_distance, 800)
y_waveform = create_realistic_waveform(x_waveform, cable_apparent_length, total_apparent_length)


# --- 3. 设置绘图区域 (与之前类似) ---
fig = plt.figure(figsize=(10, 8))
gs = fig.add_gridspec(3, 1)
ax1 = fig.add_subplot(gs[0:2, 0])
ax2 = fig.add_subplot(gs[2, 0])
fig.subplots_adjust(hspace=0.4)

# --- 4. 初始化上方子图 (TDR波形) ---
ax1.set_xlim(plot_start_position, 200)
ax1.set_ylim(-0.1, 0.3)
ax1.set_ylabel(r"Reflection coefficient, $\rho$", fontsize=12)
ax1.set_xlabel("Apparent distance [cm]", fontsize=12)
ax1.grid(True, linestyle=':', alpha=0.7)
waveform_line, = ax1.plot([], [], 'r-', lw=2)
# 预设注释
an_x1 = ax1.axvline(cable_apparent_length, color='k', linestyle='--', visible=False)
an_x2 = ax1.axvline(total_apparent_length, color='k', linestyle='--', visible=False)
an_La = ax1.annotate("", xy=(cable_apparent_length, 0.25), xytext=(total_apparent_length, 0.25),
                   arrowprops=dict(arrowstyle='<->', color='k'), visible=False)
an_La_text = ax1.text((cable_apparent_length + total_apparent_length)/2, 0.28, r'$L_a = x_2 - x_1$',
                    ha='center', va='bottom', fontsize=12, visible=False)
an_x1_text = ax1.text(cable_apparent_length, -0.45, r'$x_1$', ha='center', va='bottom', fontsize=12, visible=False)
an_x2_text = ax1.text(total_apparent_length, -0.45, r'$x_2$', ha='center', va='bottom', fontsize=12, visible=False)

# --- 5. 绘制下方子图 (物理示意图) ---
ax2.set_xlim(plot_start_position, 200)
ax2.set_ylim(-1, 1)
ax2.set_yticks([])

# 绘制cable部分 (灰色)
ax2.add_patch(Rectangle((plot_start_position, -0.1), cable_length, 0.2, facecolor='gray', alpha=0.6))
ax2.text(plot_start_position + cable_length/2, 0.3, 'Cable', ha='center', va='center', fontsize=10)

# 绘制sensor body (黑色) - 修正连接位置
ax2.add_patch(Rectangle((plot_start_position + cable_length, -0.4), sensor_body_length, 0.8, facecolor='black'))
ax2.text(plot_start_position + cable_length + sensor_body_length/2, 0, 'Sensor Body', color='white', ha='center', va='center', fontsize=9)

# 绘制土壤区域 (棕色背景)
ax2.add_patch(Rectangle((cable_apparent_length, -0.8), plot_end_distance-cable_apparent_length, 1.6, facecolor='saddlebrown', alpha=0.2))

# 绘制探针在土壤中的部分 (黑线)
ax2.plot([cable_apparent_length, total_apparent_length], [0.2, 0.2], 'k-', lw=3)
ax2.plot([cable_apparent_length, total_apparent_length], [-0.2, -0.2], 'k-', lw=3)

# 添加标签
ax2.text(cable_apparent_length + probe_apparent_length/2, -0.6, 'Soil', ha='center', va='center', fontsize=10)

signal_arrow = ax2.arrow(0, 0, 0, 0, head_width=0.2, head_length=2, fc='r', ec='r', lw=2)


# --- 6. 定义动画更新函数 ---
def update(frame):
    current_dist = plot_start_position + (frame / num_frames) * (plot_end_distance - plot_start_position)  # 从plot_start_position开始显示cable
    mask = x_waveform <= current_dist
    waveform_line.set_data(x_waveform[mask], y_waveform[mask])
    signal_arrow.set_data(x=current_dist, y=0.5, dx=0, dy=-0.2)
    # 显示注释
    if current_dist > cable_apparent_length + 2:
        an_x1.set_visible(True)
        an_x1_text.set_visible(True)
    if current_dist > total_apparent_length + 2:
        an_x2.set_visible(True)
        an_x2_text.set_visible(True)
        an_La.set_visible(True)
        an_La_text.set_visible(True)
    return waveform_line, signal_arrow, an_x1, an_x2, an_La, an_La_text, an_x1_text, an_x2_text

# --- 7. 创建并保存动画 ---
ani = FuncAnimation(fig, update, frames=num_frames+1, blit=True, interval=40)
gif_path = "tdr_waveform_realistic.gif"
ani.save(gif_path, writer='pillow', fps=25)
plt.close()
# %%
