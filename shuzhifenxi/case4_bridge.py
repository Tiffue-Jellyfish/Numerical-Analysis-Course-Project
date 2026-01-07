import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrow
import os

plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def solve_bridge_equilibrium(spans, forces):
    """
    求解连续梁桥的支座反力
    
    spans: 跨度列表, 如 [10, 12, 10]
    forces: 力列表, 每个力是一个字典:
        - type: 'concentrated' (集中力), 'distributed' (均布荷载), 'moment' (力偶)
        - magnitude: 力的大小
        - position: 作用位置 (从左端起算)
        - start, end: 对于均布荷载
    """
    n_spans = len(spans)
    n_supports = n_spans + 1
    total_length = sum(spans)
    
    # 支座位置
    support_positions = [0]
    for span in spans:
        support_positions.append(support_positions[-1] + span)
    
    # 建立平衡方程
    # 对于连续梁，需要考虑:
    # 1. 垂直方向力平衡: ΣFy = 0
    # 2. 对每个支座的力矩平衡: ΣM = 0
    
    # 方程组: A * R = F
    # R = [R1, R2, R3, ..., Rn] 是支座反力
    
    A = np.zeros((n_supports, n_supports))
    F = np.zeros(n_supports)
    
    # 方程1: 垂直力平衡 ΣRi = Σ外力
    A[0, :] = 1
    total_force = 0
    
    for force in forces:
        if force['type'] == 'concentrated':
            total_force += force['magnitude']
        elif force['type'] == 'distributed':
            length = force['end'] - force['start']
            total_force += force['magnitude'] * length
    
    F[0] = total_force
    
    # 方程2~n: 对各支座取矩 ΣM = 0
    for i in range(1, n_supports):
        moment_point = support_positions[i]
        
        # 其他支座反力产生的力矩
        for j in range(n_supports):
            distance = support_positions[j] - moment_point
            A[i, j] = distance
        
        # 外力产生的力矩
        moment_sum = 0
        for force in forces:
            if force['type'] == 'concentrated':
                distance = force['position'] - moment_point
                moment_sum += force['magnitude'] * distance
            elif force['type'] == 'distributed':
                # 均布荷载等效为作用在中点的集中力
                mid_point = (force['start'] + force['end']) / 2
                distance = mid_point - moment_point
                length = force['end'] - force['start']
                moment_sum += force['magnitude'] * length * distance
            elif force['type'] == 'moment':
                moment_sum += force['magnitude']
        
        F[i] = moment_sum
    
    # 求解线性方程组
    try:
        R = np.linalg.solve(A, F)
    except np.linalg.LinAlgError:
        # 如果矩阵奇异，使用最小二乘解
        R = np.linalg.lstsq(A, F, rcond=None)[0]
    
    # 绘制桥梁结构图
    fig_path = plot_bridge_structure(spans, forces, R, support_positions)
    
    # 验证解的正确性
    verification = verify_equilibrium(R, forces, support_positions)
    
    return {
        'support_reactions': [float(r) for r in R],
        'support_positions': [float(p) for p in support_positions],
        'equation_matrix': A.tolist(),
        'force_vector': F.tolist(),
        'verification': verification,
        'figure_path': fig_path,
        'total_length': float(total_length),
        'num_supports': int(n_supports)
    }

def verify_equilibrium(R, forces, support_positions):
    """验证力平衡和力矩平衡"""
    # 验证垂直力平衡
    total_reaction = sum(R)
    total_external = 0
    
    for force in forces:
        if force['type'] == 'concentrated':
            total_external += force['magnitude']
        elif force['type'] == 'distributed':
            length = force['end'] - force['start']
            total_external += force['magnitude'] * length
    
    force_balance_error = abs(total_reaction - total_external)
    
    # 验证对第一个支座的力矩平衡
    moment_about_first = 0
    
    # 支座反力产生的力矩
    for i, r in enumerate(R):
        moment_about_first += r * support_positions[i]
    
    # 外力产生的力矩
    for force in forces:
        if force['type'] == 'concentrated':
            moment_about_first -= force['magnitude'] * force['position']
        elif force['type'] == 'distributed':
            mid_point = (force['start'] + force['end']) / 2
            length = force['end'] - force['start']
            moment_about_first -= force['magnitude'] * length * mid_point
        elif force['type'] == 'moment':
            moment_about_first -= force['magnitude']
    
    moment_balance_error = abs(moment_about_first)
    
    is_balanced = force_balance_error < 0.01 and moment_balance_error < 0.01
    
    return {
        'force_balance_error': float(force_balance_error),
        'moment_balance_error': float(moment_balance_error),
        'is_balanced': bool(is_balanced),
        'total_reaction': float(total_reaction),
        'total_external': float(total_external)
    }

def plot_bridge_structure(spans, forces, reactions, support_positions):
    """绘制桥梁结构示意图"""
    fig, ax = plt.subplots(figsize=(14, 6))
    
    total_length = sum(spans)
    
    # 绘制梁
    beam_height = 0.3
    ax.add_patch(FancyBboxPatch((0, 0), total_length, beam_height, 
                                boxstyle="round,pad=0.05", 
                                edgecolor='black', facecolor='lightblue', linewidth=2))
    
    # 绘制支座
    for i, pos in enumerate(support_positions):
        # 支座三角形
        triangle = plt.Polygon([(pos-0.3, 0), (pos+0.3, 0), (pos, -0.5)], 
                              color='brown', edgecolor='black', linewidth=1.5)
        ax.add_patch(triangle)
        
        # 支座反力箭头
        if reactions[i] > 0:
            ax.arrow(pos, -0.8, 0, 0.2, head_width=0.3, head_length=0.1, 
                    fc='red', ec='red', linewidth=2)
            ax.text(pos, -1.2, f'R{i+1}={reactions[i]:.2f}kN', 
                   ha='center', fontsize=10, fontweight='bold', color='red')
        else:
            ax.arrow(pos, -0.6, 0, -0.2, head_width=0.3, head_length=0.1, 
                    fc='red', ec='red', linewidth=2)
            ax.text(pos, -1.2, f'R{i+1}={reactions[i]:.2f}kN', 
                   ha='center', fontsize=10, fontweight='bold', color='red')
    
    # 绘制外力
    for force in forces:
        if force['type'] == 'concentrated':
            pos = force['position']
            mag = force['magnitude']
            # 向下的箭头
            ax.arrow(pos, beam_height + 1, 0, -0.6, head_width=0.3, head_length=0.15, 
                    fc='blue', ec='blue', linewidth=2)
            ax.text(pos, beam_height + 1.5, f'F={mag}kN', 
                   ha='center', fontsize=10, color='blue', fontweight='bold')
        
        elif force['type'] == 'distributed':
            start = force['start']
            end = force['end']
            mag = force['magnitude']
            
            # 绘制均布荷载
            num_arrows = int((end - start) / 1) + 1
            for i in range(num_arrows):
                pos = start + i * (end - start) / (num_arrows - 1)
                ax.arrow(pos, beam_height + 0.8, 0, -0.3, head_width=0.15, head_length=0.1, 
                        fc='green', ec='green', linewidth=1.5, alpha=0.7)
            
            ax.text((start + end) / 2, beam_height + 1.2, f'q={mag}kN/m', 
                   ha='center', fontsize=10, color='green', fontweight='bold')
        
        elif force['type'] == 'moment':
            pos = force['position']
            mag = force['magnitude']
            # 绘制力偶
            circle = plt.Circle((pos, beam_height/2), 0.4, fill=False, 
                               edgecolor='purple', linewidth=2)
            ax.add_patch(circle)
            ax.text(pos, beam_height/2, f'M={mag}', ha='center', va='center', 
                   fontsize=9, color='purple', fontweight='bold')
    
    # 设置坐标轴
    ax.set_xlim(-1, total_length + 1)
    ax.set_ylim(-2, beam_height + 2)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('桥梁结构受力分析图', fontsize=16, fontweight='bold', pad=20)
    
    # 添加尺寸标注
    for i, span in enumerate(spans):
        start_pos = support_positions[i]
        end_pos = support_positions[i + 1]
        mid = (start_pos + end_pos) / 2
        ax.annotate('', xy=(end_pos, -1.5), xytext=(start_pos, -1.5),
                   arrowprops=dict(arrowstyle='<->', color='black', lw=1.5))
        ax.text(mid, -1.7, f'L={span}m', ha='center', fontsize=9)
    
    plt.tight_layout()
    
    # 保存图片
    os.makedirs('static/images', exist_ok=True)
    import time
    timestamp = int(time.time() * 1000)  # 添加时间戳避免缓存
    fig_path = f'static/images/bridge_{len(spans)}_span_{timestamp}.png'
    plt.savefig(fig_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"图片已保存到: {fig_path}")  # 调试信息
    
    return fig_path