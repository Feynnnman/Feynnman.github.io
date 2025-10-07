#%%
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from datetime import datetime, timedelta
import matplotlib
matplotlib.rc("font",family='Heiti TC')

# --- 1. 模拟数据生成 ---

# 模拟一天24小时，每15分钟一个数据点
time_points = np.arange(0, 24, 0.25)
# 模拟土壤深度，从地表(0)到地下50cm
depth_points = np.linspace(0, -50, 50)

# 创建时间和深度的网格，用于后续计算
time_grid, depth_grid = np.meshgrid(time_points, depth_points)

# --- 2. 模拟地表和土壤温度变化规律 ---

# a) 模拟地表温度：假设温度在15°C到35°C之间呈正弦变化
surface_temp_amplitude = 10  # 振幅：(35-15)/2
surface_temp_mean = 25       # 平均温度：(35+15)/2
# 使用正弦函数模拟一天内的温度变化，假设下午2点(14时)最热
surface_temperature = surface_temp_mean + surface_temp_amplitude * np.sin(np.pi * (time_grid - 8) / 12)

# b) 模拟热量在土壤中的传播
#    基于热传导方程的解析解，考虑振幅衰减和相位延迟
k = 0.005 * 3600             # 土壤热扩散率 (cm^2/h)，一个典型砂壤土的值
P = 24                       # 温度波动周期 (24小时)
z = -depth_grid              # 将深度转换为正值用于计算

# 计算衰减因子：深度越深，温度波动越小
decay_factor = np.exp(-z * np.sqrt(np.pi / (k * P)))
# 计算相位延迟：深度越深，温度变化响应越慢
phase_lag = -z * np.sqrt(np.pi / (k * P))

# c) 计算最终的土壤温度矩阵
#    每个时间和深度的温度 = 平均温度 + 衰减后的振幅 * sin(周期性变化 + 相位延迟)
soil_temperature = surface_temp_mean + surface_temp_amplitude * decay_factor * np.sin(np.pi * (time_grid - 8) / 12 + phase_lag)


# --- 3. 动画生成 ---

# a) 初始化图表和坐标轴
fig, ax = plt.subplots(figsize=(8, 6), constrained_layout=True)

# 设置全局字体，以防中文显示为方框
# plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False


# b) 绘制第一帧的初始图形
#    line, 后面的逗号是必须的，因为plot返回的是一个列表
line, = ax.plot(soil_temperature[:, 0], depth_points, lw=2, color='r')
# 添加一个文本框用于显示时间
time_text = ax.text(0.05, 0.05, '', transform=ax.transAxes, fontsize=12,
                    bbox=dict(boxstyle='round,pad=0.5', fc='wheat', alpha=0.5))

# c) 设置图表样式
ax.set_xlim(10, 40)
ax.set_ylim(-50, 0)
ax.set_xlabel('土壤温度 (°C)', fontsize=14)
ax.set_ylabel('土壤深度 (cm)', fontsize=14)
ax.set_title('土壤剖面温度日变化模拟', fontsize=16, pad=20)
ax.grid(True, linestyle='--', alpha=0.6)

# 在特定深度添加灰色虚线作为参考
for depth in [-10, -20, -30, -40]:
    ax.axhline(y=depth, color='grey', linestyle=':', linewidth=0.8)
    ax.text(11, depth + 1, f'{abs(depth)} cm', color='grey')


# --- 4. 定义动画更新函数 ---
#    这个函数会被 FuncAnimation 重复调用，每一帧都会执行一次
def update(frame):
    # 更新曲线的数据，传入当前帧(frame)对应的所有深度的温度数据
    line.set_xdata(soil_temperature[:, frame])

    # 更新文本框中的时间显示
    current_time = datetime(2023, 1, 1, 0, 0) + timedelta(minutes=int(time_points[frame] * 60))
    time_str = current_time.strftime('%H:%M')
    time_text.set_text(f'时间: {time_str}')

    # 返回需要更新的图形元素
    return line, time_text


# --- 5. 创建并保存动画 ---

# 创建动画对象
# fig: 在哪个图表上创建
# update: 调用哪个函数来更新
# frames: 总共有多少帧 (等于时间点的数量)
# blit=True: 优化渲染速度
# interval: 每一帧之间的间隔时间 (毫秒)
ani = FuncAnimation(fig, update, frames=len(time_points),
                    blit=True, interval=100)

# 保存为GIF文件
# 需要安装 imagemagick 或者 pillow
gif_path = "soil_temperature_profile_animation.gif"
ani.save(gif_path, writer='pillow', fps=10) # 推荐使用pillow

plt.close() # 关闭图表以释放内存

print(f"动图已成功保存至: {gif_path}")
# %%
