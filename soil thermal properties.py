#%%
import numpy as np
import matplotlib.pyplot as plt

# --- 1. 定义土壤参数 (典型砂壤土) ---
phi = 0.45       # 孔隙度, Porosity (m³/m³)
C_s = 2.0e6      # 固体矿物容积热容量, Heat capacity of solids (J m⁻³ K⁻¹)
C_w = 4.18e6     # 水的容积热容量, Heat capacity of water (J m⁻³ K⁻¹)
lambda_dry = 0.3 # 干土导热率, Thermal conductivity of dry soil (W m⁻¹ K⁻¹)
lambda_sat = 2.2 # 饱和土导热率, Thermal conductivity of saturated soil (W m⁻¹ K⁻¹)

# --- 2. 生成含水量范围 ---
# 从0(干土)到孔隙度phi(饱和)
theta = np.linspace(0, phi, 200)

# --- 3. 计算各项热力学参数 ---
# a) 容积热容量 (C) - 线性关系
C = (1 - phi) * C_s + theta * C_w

# b) 导热率 (λ) - 非线性关系 (使用简化的经验模型)
# 使用饱和度(Se = theta/phi)来表示，更符合通用模型
Se = theta / phi
lambda_val = lambda_dry + (lambda_sat - lambda_dry) * (1 - (1 + (Se / 0.14) ** (1 / (1 - 0.29))) ** (-0.29))/(1 - (1 + (1 / 0.14) ** (1 / (1 - 0.29))) ** (-0.29))

# c) 热扩散率 (κ) - 定义为 λ/C
# 乘以1e6是为了让数值更易于在图上展示 (单位从 m²/s 变为 mm²/s)
kappa = (lambda_val / C) * 1e6

# --- 4. 绘图 ---
# 由于三个变量的量纲和数值范围差异巨大，将它们归一化到[0, 1]区间以便于在同一张图上比较其变化趋势
C_norm = (C - np.min(C)) / (np.max(C) - np.min(C))
lambda_norm = (lambda_val - np.min(lambda_val)) / (np.max(lambda_val) - np.min(lambda_val))
kappa_norm = (kappa - np.min(kappa)) / (np.max(kappa) - np.min(kappa))

# 设置全局字体以支持中文和特殊符号
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['mathtext.fontset'] = 'stix' # 用于显示优美的LaTeX符号

fig, ax = plt.subplots(figsize=(10, 7))

ax.plot(theta, C_norm, label=r'容积热容量 (C)', color='blue', linestyle='--', lw=2.5)
ax.plot(theta, lambda_norm, label=r'导热率 ($\lambda$)', color='red', linestyle='-', lw=2.5)
ax.plot(theta, kappa_norm, label=r'热扩散率 ($\kappa$)', color='green', linestyle='-.', lw=2.5)

ax.set_xlabel(r'土壤含水量 $\theta$ (m³/m³)', fontsize=18)
ax.set_ylabel('归一化数值', fontsize=18)
ax.legend(fontsize=16, loc='lower right')
ax.grid(True, linestyle=':', alpha=0.7)
ax.tick_params(labelsize=18)
ax.set_xlim(0, phi)
ax.set_ylim(0, 1.1)
plt.tight_layout()

# 保存图像
plt.savefig("soil_thermal_properties.png", dpi=300)
plt.show()
# %%
