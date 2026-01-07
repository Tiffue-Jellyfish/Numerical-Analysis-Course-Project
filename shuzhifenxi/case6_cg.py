import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import os

plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def conjugate_gradient_method(size=100):
    """
    案例6: 共轭梯度法求解大型稀疏线性方程组
    
    适用于求解正定对称矩阵的线性方程组 Ax = b
    特别适合大规模稀疏系统
    """
    
    # 生成一个正定对称矩阵 (使用拉普拉斯矩阵)
    A = generate_laplacian_matrix(size)
    
    # 生成随机右端向量
    np.random.seed(42)
    b = np.random.randn(size)
    
    # 共轭梯度法求解
    x_cg, history_cg = conjugate_gradient(A, b)
    
    # 使用numpy直接求解作为对比
    x_exact = np.linalg.solve(A.toarray(), b)
    
    # 计算误差
    error = np.linalg.norm(x_cg - x_exact) / np.linalg.norm(x_exact)
    
    # 绘制收敛曲线
    fig_path = plot_convergence(history_cg, size)
    
    return {
        'method': 'conjugate_gradient',
        'matrix_size': size,
        'iterations': len(history_cg),
        'final_residual': history_cg[-1]['residual'],
        'relative_error': float(error),
        'convergence_history': history_cg,
        'figure_path': fig_path,
        'solution_norm': float(np.linalg.norm(x_cg)),
        'comparison': {
            'cg_solution_sample': x_cg[:10].tolist(),
            'exact_solution_sample': x_exact[:10].tolist()
        }
    }

def generate_laplacian_matrix(n):
    """生成拉普拉斯矩阵 (正定对称稀疏矩阵)"""
    from scipy.sparse import diags
    
    # 1D拉普拉斯矩阵: 对角线为2, 上下对角线为-1
    diagonals = [np.full(n, 2.0), np.full(n-1, -1.0), np.full(n-1, -1.0)]
    A = diags(diagonals, [0, -1, 1], format='csr')
    
    return A

def conjugate_gradient(A, b, x0=None, max_iter=None, tol=1e-6):
    """
    共轭梯度法实现
    
    A: 正定对称矩阵
    b: 右端向量
    x0: 初始猜测
    """
    n = len(b)
    
    if x0 is None:
        x = np.zeros(n)
    else:
        x = x0.copy()
    
    if max_iter is None:
        max_iter = n
    
    # 初始残差 r = b - Ax
    r = b - A @ x
    
    # 初始搜索方向
    p = r.copy()
    
    # 初始残差范数
    rs_old = np.dot(r, r)
    
    history = []
    
    for iteration in range(max_iter):
        # 计算步长 α
        Ap = A @ p
        alpha = rs_old / np.dot(p, Ap)
        
        # 更新解 x
        x = x + alpha * p
        
        # 更新残差 r
        r = r - alpha * Ap
        
        # 计算新的残差范数
        rs_new = np.dot(r, r)
        residual_norm = np.sqrt(rs_new)
        
        history.append({
            'iteration': iteration + 1,
            'residual': float(residual_norm),
            'x_norm': float(np.linalg.norm(x))
        })
        
        # 检查收敛
        if residual_norm < tol:
            break
        
        # 计算新的搜索方向
        beta = rs_new / rs_old
        p = r + beta * p
        
        rs_old = rs_new
    
    return x, history

def plot_convergence(history, size):
    """绘制收敛曲线"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    iterations = [h['iteration'] for h in history]
    residuals = [h['residual'] for h in history]
    
    # 残差曲线
    ax1.semilogy(iterations, residuals, 'b-', linewidth=2, marker='o', markersize=4)
    ax1.set_xlabel('迭代次数', fontsize=12)
    ax1.set_ylabel('残差范数 (对数尺度)', fontsize=12)
    ax1.set_title('共轭梯度法收敛曲线', fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    
    # 在图上标注关键点
    if len(iterations) > 0:
        ax1.annotate(f'初始: {residuals[0]:.2e}', 
                    xy=(iterations[0], residuals[0]),
                    xytext=(10, 20), textcoords='offset points',
                    bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.7),
                    arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))
        
        ax1.annotate(f'最终: {residuals[-1]:.2e}', 
                    xy=(iterations[-1], residuals[-1]),
                    xytext=(-50, 20), textcoords='offset points',
                    bbox=dict(boxstyle='round,pad=0.5', facecolor='lightgreen', alpha=0.7),
                    arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))
    
    # 收敛率分析
    if len(residuals) > 1:
        convergence_rates = []
        for i in range(1, len(residuals)):
            if residuals[i-1] > 0:
                rate = residuals[i] / residuals[i-1]
                convergence_rates.append(rate)
        
        ax2.plot(range(1, len(convergence_rates)+1), convergence_rates, 
                'r-', linewidth=2, marker='s', markersize=4)
        ax2.axhline(y=1, color='gray', linestyle='--', alpha=0.5, label='收敛阈值')
        ax2.set_xlabel('迭代次数', fontsize=12)
        ax2.set_ylabel('收敛率 (r_k / r_{k-1})', fontsize=12)
        ax2.set_title('收敛率变化', fontsize=14, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        ax2.legend()
        
        # 计算平均收敛率
        avg_rate = np.mean(convergence_rates) if convergence_rates else 0
        ax2.text(0.5, 0.95, f'平均收敛率: {avg_rate:.4f}', 
                transform=ax2.transAxes, fontsize=11,
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8),
                verticalalignment='top', horizontalalignment='center')
    
    plt.suptitle(f'共轭梯度法求解 {size}×{size} 线性方程组', 
                fontsize=16, fontweight='bold', y=1.02)
    plt.tight_layout()
    
    os.makedirs('static/images', exist_ok=True)
    fig_path = 'static/images/conjugate_gradient.png'
    plt.savefig(fig_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    return fig_path

def compare_methods(size=50):
    """比较不同方法的性能"""
    A = generate_laplacian_matrix(size)
    b = np.random.randn(size)
    
    # 共轭梯度法
    import time
    start = time.time()
    x_cg, history_cg = conjugate_gradient(A, b)
    time_cg = time.time() - start
    
    # 直接求解
    start = time.time()
    x_direct = np.linalg.solve(A.toarray(), b)
    time_direct = time.time() - start
    
    return {
        'conjugate_gradient': {
            'time': time_cg,
            'iterations': len(history_cg),
            'error': float(np.linalg.norm(x_cg - x_direct))
        },
        'direct_solve': {
            'time': time_direct
        },
        'speedup': time_direct / time_cg
    }
