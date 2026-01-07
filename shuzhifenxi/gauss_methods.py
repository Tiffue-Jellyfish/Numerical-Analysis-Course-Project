import numpy as np
import copy

def gauss_elimination_steps(A, b):
    """高斯消元法 - 返回详细步骤"""
    n = len(A)
    A = [row[:] for row in A]  # 深拷贝
    b = b[:]
    
    # 构造增广矩阵
    augmented = [A[i] + [b[i]] for i in range(n)]
    
    steps = []
    steps.append({
        'step': 0,
        'description': '初始增广矩阵',
        'matrix': copy.deepcopy(augmented),
        'type': 'init'
    })
    
    # 前向消元
    for k in range(n):
        # 检查主元是否为0
        if abs(augmented[k][k]) < 1e-10:
            steps.append({
                'step': len(steps),
                'description': f'警告: 第{k+1}行第{k+1}列主元接近0',
                'matrix': copy.deepcopy(augmented),
                'type': 'warning'
            })
            continue
        
        # 消元
        for i in range(k + 1, n):
            if abs(augmented[i][k]) > 1e-10:
                factor = augmented[i][k] / augmented[k][k]
                
                for j in range(k, n + 1):
                    augmented[i][j] -= factor * augmented[k][j]
                
                steps.append({
                    'step': len(steps),
                    'description': f'消去第{i+1}行第{k+1}列, 倍数={factor:.4f}',
                    'matrix': copy.deepcopy(augmented),
                    'type': 'elimination',
                    'pivot_row': k,
                    'target_row': i,
                    'factor': factor
                })
    
    steps.append({
        'step': len(steps),
        'description': '前向消元完成，得到上三角矩阵',
        'matrix': copy.deepcopy(augmented),
        'type': 'forward_complete'
    })
    
    # 回代求解
    x = [0.0] * n
    for i in range(n - 1, -1, -1):
        x[i] = augmented[i][n]
        for j in range(i + 1, n):
            x[i] -= augmented[i][j] * x[j]
        x[i] /= augmented[i][i]
        
        steps.append({
            'step': len(steps),
            'description': f'回代求解 x{i+1} = {x[i]:.6f}',
            'solution_partial': x[:],
            'type': 'backsubstitution'
        })
    
    return {
        'method': 'gauss_elimination',
        'steps': steps,
        'solution': x,
        'num_steps': len(steps)
    }

def gauss_with_pivot_steps(A, b):
    """列主元高斯消元法 - 返回详细步骤"""
    n = len(A)
    A = [row[:] for row in A]
    b = b[:]
    
    augmented = [A[i] + [b[i]] for i in range(n)]
    
    steps = []
    steps.append({
        'step': 0,
        'description': '初始增广矩阵',
        'matrix': copy.deepcopy(augmented),
        'type': 'init'
    })
    
    # 前向消元（带列主元）
    for k in range(n):
        # 寻找列主元
        max_row = k
        max_val = abs(augmented[k][k])
        
        for i in range(k + 1, n):
            if abs(augmented[i][k]) > max_val:
                max_val = abs(augmented[i][k])
                max_row = i
        
        # 交换行
        if max_row != k:
            augmented[k], augmented[max_row] = augmented[max_row], augmented[k]
            steps.append({
                'step': len(steps),
                'description': f'选择列主元: 交换第{k+1}行与第{max_row+1}行 (主元={max_val:.4f})',
                'matrix': copy.deepcopy(augmented),
                'type': 'pivot',
                'swap_rows': [k, max_row]
            })
        
        # 消元
        for i in range(k + 1, n):
            if abs(augmented[i][k]) > 1e-10:
                factor = augmented[i][k] / augmented[k][k]
                
                for j in range(k, n + 1):
                    augmented[i][j] -= factor * augmented[k][j]
                
                steps.append({
                    'step': len(steps),
                    'description': f'消去第{i+1}行第{k+1}列, 倍数={factor:.4f}',
                    'matrix': copy.deepcopy(augmented),
                    'type': 'elimination',
                    'factor': factor
                })
    
    # 回代求解
    x = [0.0] * n
    for i in range(n - 1, -1, -1):
        x[i] = augmented[i][n]
        for j in range(i + 1, n):
            x[i] -= augmented[i][j] * x[j]
        x[i] /= augmented[i][i]
    
    steps.append({
        'step': len(steps),
        'description': '回代求解完成',
        'solution': x,
        'type': 'complete'
    })
    
    return {
        'method': 'gauss_with_pivot',
        'steps': steps,
        'solution': x,
        'num_steps': len(steps)
    }

def lu_decomposition_steps(A, b):
    """LU分解法"""
    n = len(A)
    A = np.array(A, dtype=float)
    b = np.array(b, dtype=float)
    
    L = np.eye(n)
    U = np.zeros((n, n))
    
    steps = []
    steps.append({
        'step': 0,
        'description': '开始LU分解',
        'L': L.tolist(),
        'U': U.tolist(),
        'type': 'init'
    })
    
    # Doolittle分解
    for i in range(n):
        # 计算U的第i行
        for j in range(i, n):
            sum_val = sum(L[i][k] * U[k][j] for k in range(i))
            U[i][j] = A[i][j] - sum_val
        
        # 计算L的第i列
        for j in range(i + 1, n):
            sum_val = sum(L[j][k] * U[k][i] for k in range(i))
            L[j][i] = (A[j][i] - sum_val) / U[i][i]
        
        steps.append({
            'step': len(steps),
            'description': f'完成第{i+1}行U和第{i+1}列L的计算',
            'L': L.tolist(),
            'U': U.tolist(),
            'type': 'decomposition'
        })
    
    # 求解Ly = b
    y = np.zeros(n)
    for i in range(n):
        y[i] = b[i] - sum(L[i][j] * y[j] for j in range(i))
    
    steps.append({
        'step': len(steps),
        'description': '求解Ly = b',
        'y': y.tolist(),
        'type': 'forward_sub'
    })
    
    # 求解Ux = y
    x = np.zeros(n)
    for i in range(n - 1, -1, -1):
        x[i] = (y[i] - sum(U[i][j] * x[j] for j in range(i + 1, n))) / U[i][i]
    
    steps.append({
        'step': len(steps),
        'description': '求解Ux = y',
        'solution': x.tolist(),
        'type': 'backward_sub'
    })
    
    return {
        'method': 'lu_decomposition',
        'steps': steps,
        'L': L.tolist(),
        'U': U.tolist(),
        'solution': x.tolist()
    }

def lu_with_pivot_steps(A, b):
    """带列主元的LU分解"""
    n = len(A)
    A = np.array(A, dtype=float)
    b = np.array(b, dtype=float)
    
    P = np.eye(n)  # 置换矩阵
    L = np.eye(n)
    U = A.copy()
    
    steps = []
    steps.append({
        'step': 0,
        'description': '开始带列主元的LU分解',
        'P': P.tolist(),
        'L': L.tolist(),
        'U': U.tolist(),
        'type': 'init'
    })
    
    for k in range(n - 1):
        # 寻找列主元
        max_row = k + np.argmax(np.abs(U[k:, k]))
        
        if max_row != k:
            # 交换U的行
            U[[k, max_row]] = U[[max_row, k]]
            # 交换P的行
            P[[k, max_row]] = P[[max_row, k]]
            # 交换L的行（仅前k列）
            if k > 0:
                L[[k, max_row], :k] = L[[max_row, k], :k]
            
            steps.append({
                'step': len(steps),
                'description': f'列主元: 交换第{k+1}行和第{max_row+1}行',
                'P': P.tolist(),
                'type': 'pivot'
            })
        
        # 消元
        for i in range(k + 1, n):
            L[i][k] = U[i][k] / U[k][k]
            U[i, k:] -= L[i][k] * U[k, k:]
        
        steps.append({
            'step': len(steps),
            'description': f'完成第{k+1}列的消元',
            'L': L.tolist(),
            'U': U.tolist(),
            'type': 'elimination'
        })
    
    # 求解
    Pb = P @ b
    
    # Ly = Pb
    y = np.zeros(n)
    for i in range(n):
        y[i] = Pb[i] - sum(L[i][j] * y[j] for j in range(i))
    
    # Ux = y
    x = np.zeros(n)
    for i in range(n - 1, -1, -1):
        x[i] = (y[i] - sum(U[i][j] * x[j] for j in range(i + 1, n))) / U[i][i]
    
    steps.append({
        'step': len(steps),
        'description': '求解完成',
        'solution': x.tolist(),
        'type': 'complete'
    })
    
    return {
        'method': 'lu_with_pivot',
        'steps': steps,
        'P': P.tolist(),
        'L': L.tolist(),
        'U': U.tolist(),
        'solution': x.tolist()
    }



