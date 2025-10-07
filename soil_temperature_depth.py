#%%
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from datetime import datetime, timedelta
import matplotlib
matplotlib.rc("font",family='Heiti TC')

# --- 1. 模拟数据生成 ---
time_points = np.arange(0, 72, 0.25)
depth_points = np.linspace(0, -50, 51)
time_grid, depth_grid = np.meshgrid(time_points, depth_points)

surface_temp_amplitude = 10
surface_temp_mean = 25
k = 0.005 * 3600  # 土壤热扩散率 (cm^2/h)
P = 24            # 波动周期 (24小时)
z = -depth_grid

decay_factor = np.exp(-z * np.sqrt(np.pi / (k * P)))
phase_lag = -z * np.sqrt(np.pi / (k * P))

soil_temperature = surface_temp_mean + surface_temp_amplitude * decay_factor * np.sin(np.pi * (time_grid - 8) / 12 + phase_lag)

# --- 2. 提取特定深度的数据 ---
# 找到与我们关心的深度最接近的索引
depths_to_plot = [-5, -10, -20, -50]
depth_indices = [np.abs(depth_points - d).argmin() for d in depths_to_plot]

# 提取这些深度在所有时间点的温度数据
temp_data_5cm = soil_temperature[depth_indices[0], :]
temp_data_10cm = soil_temperature[depth_indices[1], :]
temp_data_20cm = soil_temperature[depth_indices[2], :]
temp_data_50cm = soil_temperature[depth_indices[3], :]

# --- 3. 动画生成 ---
fig, ax = plt.subplots(figsize=(8, 6),constrained_layout=True)
# 设置全局字体以支持中文
plt.rcParams['axes.unicode_minus'] = False

# a) 初始化四条空的曲线
line_5cm, = ax.plot([], [], lw=2, label='5 cm 深度')
line_10cm, = ax.plot([], [], lw=2, label='10 cm 深度')
line_20cm, = ax.plot([], [], lw=2, label='20 cm 深度')
line_50cm, = ax.plot([], [], lw=2, label='50 cm 深度')
lines = [line_5cm, line_10cm, line_20cm, line_50cm]
data_series = [temp_data_5cm, temp_data_10cm, temp_data_20cm, temp_data_50cm]

# 添加一个垂直线来指示当前时间
time_marker = ax.axvline(x=0, color='r', linestyle='--', lw=1.5, alpha=0.8)

# 添加时间文本
time_text = ax.text(0.02, 1.01, '', transform=ax.transAxes, fontsize=12)

# b) 设置图表样式
ax.set_xlim(0, 72)
ax.set_ylim(np.min(soil_temperature) - 1, np.max(soil_temperature) + 1)
ax.set_xlabel('时间 (小时)', fontsize=14)
ax.set_ylabel('土壤温度 (°C)', fontsize=14)
ax.set_title('不同土壤深度的温度日变化', fontsize=16, pad=20)
ax.legend(loc='upper right')
ax.grid(True, linestyle='--', alpha=0.6)
ax.set_xticks(np.arange(0, 73, 6))


# --- 4. 定义动画更新函数 ---
def update(frame):
    # 当前动画帧的时间点
    current_time_point = time_points[frame]

    # 更新每条曲线的数据，只画到当前时间点
    for line, data in zip(lines, data_series):
        line.set_data(time_points[:frame+1], data[:frame+1])

    # 更新垂直标记线的位置
    time_marker.set_xdata([current_time_point, current_time_point])

    # 更新时间文本
    current_time_obj = datetime(2023, 1, 1, 0, 0) + timedelta(minutes=int(current_time_point * 60))
    time_str = current_time_obj.strftime('%H:%M')
    time_text.set_text(f'当前时间: {time_str}')

    # blit=True 要求返回所有更新的 artist
    return lines + [time_marker, time_text]

# --- 5. 创建并保存动画 ---
ani = FuncAnimation(fig, update, frames=len(time_points),
                    blit=True, interval=80)

gif_path = "soil_temperature_depth_comparison.gif"
ani.save(gif_path, writer='pillow', fps=15)

plt.close()

print(f"动图已成功保存至: {gif_path}")
# %%
