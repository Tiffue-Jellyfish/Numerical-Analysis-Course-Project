import numpy as np
import pandas as pd
from .gauss_methods import gauss_with_pivot_steps

def linear_regression_analysis(csv_path):
    """
    案例3: 用户画像特征分析
    使用最小二乘法求解线性回归模型
    """
    # 读取数据
    df = pd.read_csv(csv_path)
    
    # 特征列 (x1 到 x12)
    feature_cols = [
        'age', 'gender', 'city_level', 'monthly_consumption',
        'shopping_frequency', 'product_diversity', 'high_value_purchase_history',
        'average_browse_time', 'promotion_participation', 'favorites_count',
        'friends_count', 'sharing_times'
    ]
    
    # 目标列
    target_col = 'purchase_high_value_probability'
    
    # 构造设计矩阵 X (添加截距项)
    X = df[feature_cols].values
    m = X.shape[0]  # 样本数
    X = np.column_stack([np.ones(m), X])  # 添加全1列作为截距项
    
    # 目标向量 Y
    Y = df[target_col].values.reshape(-1, 1)
    
    # 使用正规方程求解: β = (X^T X)^(-1) X^T Y
    # 等价于求解线性方程组: (X^T X) β = X^T Y
    
    XTX = X.T @ X
    XTY = X.T @ Y
    
    # 使用数值方法求解 (这里用numpy求解，也可以调用自己实现的高斯消元)
    try:
        # 方法1: 使用numpy直接求解
        beta_numpy = np.linalg.solve(XTX, XTY).flatten()
        
        # 方法2: 使用自己的高斯消元法
        beta_gauss = solve_normal_equation(XTX.tolist(), XTY.flatten().tolist())
        
    except np.linalg.LinAlgError:
        return {'error': '矩阵奇异，无法求解'}
    
    # 计算预测值
    Y_pred = X @ beta_numpy.reshape(-1, 1)
    
    # 计算评估指标
    residuals = Y - Y_pred
    rss = np.sum(residuals ** 2)  # 残差平方和
    tss = np.sum((Y - np.mean(Y)) ** 2)  # 总平方和
    r_squared = 1 - (rss / tss)  # R²
    
    # 计算均方误差
    mse = rss / m
    rmse = np.sqrt(mse)
    
    # 特征重要性分析
    feature_names = ['截距'] + feature_cols
    coefficients = []
    
    for i, (name, coef) in enumerate(zip(feature_names, beta_numpy)):
        coefficients.append({
            'feature': name,
            'coefficient': float(coef),
            'abs_coefficient': float(abs(coef))
        })
    
    # 按绝对值排序
    coefficients_sorted = sorted(coefficients[1:], key=lambda x: x['abs_coefficient'], reverse=True)
    
    # 数据统计
    feature_stats = {}
    for col in feature_cols:
        feature_stats[col] = {
            'mean': float(df[col].mean()),
            'std': float(df[col].std()),
            'min': float(df[col].min()),
            'max': float(df[col].max())
        }
    
    return {
        'coefficients': coefficients,
        'coefficients_sorted': coefficients_sorted,
        'intercept': float(beta_numpy[0]),
        'r_squared': float(r_squared),
        'rmse': float(rmse),
        'mse': float(mse),
        'num_samples': int(m),
        'num_features': len(feature_cols),
        'feature_stats': feature_stats,
        'XTX_condition_number': float(np.linalg.cond(XTX)),
        'method_comparison': {
            'numpy': beta_numpy.tolist(),
            'gauss': beta_gauss
        }
    }

def solve_normal_equation(A, b):
    """使用高斯消元法求解正规方程"""
    n = len(A)
    augmented = [A[i] + [b[i]] for i in range(n)]
    
    # 列主元高斯消元
    for k in range(n):
        # 寻找列主元
        max_row = k
        for i in range(k + 1, n):
            if abs(augmented[i][k]) > abs(augmented[max_row][k]):
                max_row = i
        
        # 交换行
        augmented[k], augmented[max_row] = augmented[max_row], augmented[k]
        
        # 消元
        for i in range(k + 1, n):
            if abs(augmented[k][k]) > 1e-10:
                factor = augmented[i][k] / augmented[k][k]
                for j in range(k, n + 1):
                    augmented[i][j] -= factor * augmented[k][j]
    
    # 回代
    x = [0.0] * n
    for i in range(n - 1, -1, -1):
        x[i] = augmented[i][n]
        for j in range(i + 1, n):
            x[i] -= augmented[i][j] * x[j]
        if abs(augmented[i][i]) > 1e-10:
            x[i] /= augmented[i][i]
    
    return x

def predict_user(features, coefficients):
    """预测单个用户购买高价值商品的可能性"""
    # features: [age, gender, city_level, ...]
    # coefficients: [β0, β1, β2, ...]
    
    prediction = coefficients[0]  # 截距
    for i, feat in enumerate(features):
        prediction += coefficients[i + 1] * feat
    
    # 转换为概率 (使用sigmoid函数)
    probability = 1 / (1 + np.exp(-prediction))
    
    return {
        'raw_prediction': float(prediction),
        'probability': float(probability),
        'classification': 1 if probability > 0.5 else 0
    }