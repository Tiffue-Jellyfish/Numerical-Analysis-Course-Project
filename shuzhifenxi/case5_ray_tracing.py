import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os

plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def ray_tracing_simulation(num_rays=50):
    """
    案例5: 光线追踪 - 计算光线反射与折射
    
    场景: 光线从光源发出，经过多个反射/折射表面
    需要求解线性方程组来确定光线与表面的交点
    """
    
    # 定义场景
    light_source = np.array([5, 10])
    
    # 定义多个反射面 (平面方程 ax + by + c = 0)
    surfaces = [
        {'type': 'mirror', 'coeffs': [0, 1, -5], 'name': '水平镜面'},  # y = 5
        {'type': 'mirror', 'coeffs': [1, 0, -10], 'name': '竖直镜面'},  # x = 10
        {'type': 'refraction', 'coeffs': [1, 1, -12], 'n1': 1.0, 'n2': 1.5, 'name': '折射面'}  # x + y = 12
    ]
    
    rays = []
    
    # 生成多条光线
    angles = np.linspace(0, 2*np.pi, num_rays)
    
    for angle in angles:
        # 光线初始方向
        direction = np.array([np.cos(angle), np.sin(angle)])
        
        # 追踪光线
        ray_path = trace_ray(light_source, direction, surfaces, max_bounces=5)
        rays.append(ray_path)
    
    # 绘制光线追踪结果
    fig_path = plot_ray_tracing(light_source, surfaces, rays)
    
    # 统计信息
    total_intersections = sum(len(ray['intersections']) for ray in rays)
    
    return {
        'num_rays': num_rays,
        'light_source': light_source.tolist(),
        'surfaces': surfaces,
        'total_intersections': total_intersections,
        'figure_path': fig_path,
        'sample_ray': rays[0] if rays else None
    }

def trace_ray(origin, direction, surfaces, max_bounces=5):
    """追踪单条光线"""
    current_pos = origin.copy()
    current_dir = direction / np.linalg.norm(direction)
    
    path = [current_pos.copy()]
    intersections = []
    
    for bounce in range(max_bounces):
        # 找到最近的交点
        min_t = float('inf')
        closest_surface = None
        closest_intersection = None
        
        for surface in surfaces:
            # 求光线与平面的交点
            # 光线: P = P0 + t*d
            # 平面: ax + by + c = 0
            a, b, c = surface['coeffs']
            
            # 代入得: a(x0 + t*dx) + b(y0 + t*dy) + c = 0
            # t = -(ax0 + by0 + c) / (a*dx + b*dy)
            
            denominator = a * current_dir[0] + b * current_dir[1]
            
            if abs(denominator) > 1e-6:  # 不平行
                numerator = -(a * current_pos[0] + b * current_pos[1] + c)
                t = numerator / denominator
                
                if t > 0.01 and t < min_t:  # 避免自交
                    intersection = current_pos + t * current_dir
                    min_t = t
                    closest_surface = surface
                    closest_intersection = intersection
        
        if closest_surface is None:
            break
        
        # 记录交点
        path.append(closest_intersection)
        intersections.append({
            'position': closest_intersection.tolist(),
            'surface': closest_surface['name'],
            'bounce': bounce + 1
        })
        
        # 计算反射/折射方向
        if closest_surface['type'] == 'mirror':
            # 反射
            a, b, c = closest_surface['coeffs']
            normal = np.array([a, b])
            normal = normal / np.linalg.norm(normal)
            
            # 反射公式: r = d - 2(d·n)n
            current_dir = current_dir - 2 * np.dot(current_dir, normal) * normal
        
        elif closest_surface['type'] == 'refraction':
            # 折射 (Snell定律)
            a, b, c = closest_surface['coeffs']
            normal = np.array([a, b])
            normal = normal / np.linalg.norm(normal)
            
            n1, n2 = closest_surface['n1'], closest_surface['n2']
            cos_i = -np.dot(current_dir, normal)
            
            # 确保normal指向入射侧
            if cos_i < 0:
                cos_i = -cos_i
                normal = -normal
                n1, n2 = n2, n1
            
            eta = n1 / n2
            k = 1 - eta * eta * (1 - cos_i * cos_i)
            
            if k < 0:
                # 全反射
                current_dir = current_dir - 2 * np.dot(current_dir, normal) * normal
            else:
                # 折射
                current_dir = eta * current_dir + (eta * cos_i - np.sqrt(k)) * normal
        
        current_pos = closest_intersection
    
    return {
        'path': [p.tolist() for p in path],
        'intersections': intersections,
        'num_bounces': len(intersections)
    }

def plot_ray_tracing(light_source, surfaces, rays):
    """绘制光线追踪图"""
    fig, ax = plt.subplots(figsize=(12, 10))
    
    # 绘制反射面
    for surface in surfaces:
        a, b, c = surface['coeffs']
        if abs(b) > 1e-6:
            # y = (-ax - c) / b
            x = np.linspace(0, 15, 100)
            y = (-a * x - c) / b
        else:
            # x = -c / a
            x = np.full(100, -c / a)
            y = np.linspace(0, 15, 100)
        
        color = 'silver' if surface['type'] == 'mirror' else 'lightblue'
        label = surface['name']
        ax.plot(x, y, color=color, linewidth=3, label=label, alpha=0.7)
    
    # 绘制光线
    for ray in rays:
        path = ray['path']
        if len(path) > 1:
            path_array = np.array(path)
            ax.plot(path_array[:, 0], path_array[:, 1], 
                   'yellow', linewidth=0.5, alpha=0.6)
    
    # 绘制光源
    ax.scatter(*light_source, color='red', s=200, marker='*', 
              edgecolors='orange', linewidths=2, label='光源', zorder=5)
    
    ax.set_xlim(0, 15)
    ax.set_ylim(0, 15)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper right', fontsize=10)
    ax.set_title('光线追踪模拟 - 反射与折射', fontsize=16, fontweight='bold', pad=15)
    ax.set_xlabel('X', fontsize=12)
    ax.set_ylabel('Y', fontsize=12)
    ax.set_facecolor('#1a1a1a')
    
    plt.tight_layout()
    
    os.makedirs('static/images', exist_ok=True)
    fig_path = 'static/images/ray_tracing.png'
    plt.savefig(fig_path, dpi=150, bbox_inches='tight', facecolor='#1a1a1a')
    plt.close()
    
    return fig_path