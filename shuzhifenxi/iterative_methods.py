import numpy as np
import math

def sor_iteration(A, b, omega, exact_solution=None, max_iter=100, tol=1e-6):
    """SOR (逐次超松弛) 迭代法"""
    n = len(A)
    x = np.zeros(n)
    
    iterations = []
    
    for iter_count in range(max_iter):
        x_old = x.copy()
        
        # SOR迭代
        for i in range(n):
            sum1 = sum(A[i][j] * x[j] for j in range(i))
            sum2 = sum(A[i][j] * x_old[j] for j in range(i + 1, n))
            
            x[i] = (1 - omega) * x_old[i] + (omega / A[i][i]) * (b[i] - sum1 - sum2)
        
        # 计算残差
        residual = np.linalg.norm(x - x_old)
        
        # 计算与精确解的误差
        exact_error = None
        if exact_solution is not None:
            exact_error = np.linalg.norm(x - np.array(exact_solution))
        
        iterations.append({
            'iteration': iter_count + 1,
            'x': x.tolist(),
            'residual': float(residual),
            'exact_error': float(exact_error) if exact_error is not None else None
        })
        
        # 检查收敛
        if residual < tol:
            break
    
    return {
        'omega': omega,
        'iterations': iterations,
        'final_solution': x.tolist(),
        'convergence_iter': len(iterations),
        'converged': bool(residual < tol)
    }

def jacobi_iteration(A, b, x0=None, max_iter=100, tol=1e-6):
    """Jacobi迭代法"""
    n = len(A)
    x = np.zeros(n) if x0 is None else np.array(x0)
    
    iterations = []
    
    for iter_count in range(max_iter):
        x_new = np.zeros(n)
        
        for i in range(n):
            sum_val = sum(A[i][j] * x[j] for j in range(n) if j != i)
            x_new[i] = (b[i] - sum_val) / A[i][i]
        
        residual = np.linalg.norm(x_new - x)
        
        iterations.append({
            'iteration': iter_count + 1,
            'x': x_new.tolist(),
            'residual': float(residual)
        })
        
        x = x_new
        
        if residual < tol:
            break
    
    return {
        'method': 'jacobi',
        'iterations': iterations,
        'final_solution': x.tolist(),
        'convergence_iter': len(iterations)
    }

def gauss_seidel_iteration(A, b, x0=None, max_iter=100, tol=1e-6):
    """Gauss-Seidel迭代法"""
    n = len(A)
    x = np.zeros(n) if x0 is None else np.array(x0)
    
    iterations = []
    
    for iter_count in range(max_iter):
        x_old = x.copy()
        
        for i in range(n):
            sum1 = sum(A[i][j] * x[j] for j in range(i))
            sum2 = sum(A[i][j] * x_old[j] for j in range(i + 1, n))
            x[i] = (b[i] - sum1 - sum2) / A[i][i]
        
        residual = np.linalg.norm(x - x_old)
        
        iterations.append({
            'iteration': iter_count + 1,
            'x': x.tolist(),
            'residual': float(residual)
        })
        
        if residual < tol:
            break
    
    return {
        'method': 'gauss_seidel',
        'iterations': iterations,
        'final_solution': x.tolist(),
        'convergence_iter': len(iterations)
    }

def compare_iterative_methods(A, b, exact_solution=None):
    """比较不同迭代方法"""
    jacobi_result = jacobi_iteration(A, b)
    gs_result = gauss_seidel_iteration(A, b)
    sor_results = []
    
    for omega in [0.5, 1.0, 1.25, 1.5, 1.75]:
        sor_result = sor_iteration(A, b, omega, exact_solution)
        sor_results.append(sor_result)
    
    return {
        'jacobi': jacobi_result,
        'gauss_seidel': gs_result,
        'sor': sor_results
    }