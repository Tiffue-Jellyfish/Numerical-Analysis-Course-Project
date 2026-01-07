from flask import Flask, render_template, jsonify, request, send_file
import os
import json

app = Flask(__name__)

# 配置静态文件
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # 禁用缓存，方便调试

# 导入所有案例模块
from shuzhifenxi.gauss_methods import (
    gauss_elimination_steps,
    gauss_with_pivot_steps,
    lu_decomposition_steps,
    lu_with_pivot_steps
)
from shuzhifenxi.iterative_methods import sor_iteration, jacobi_iteration, gauss_seidel_iteration
from shuzhifenxi.linear_regression import linear_regression_analysis
from shuzhifenxi.case4_bridge import solve_bridge_equilibrium
from shuzhifenxi.case5_ray_tracing import ray_tracing_simulation
from shuzhifenxi.case6_cg import conjugate_gradient_method

@app.route('/')
def index():
    return render_template('index.html')

# ============ 案例1: 高斯消元法 ============
@app.route('/api/case1/gauss', methods=['POST'])
def case1_gauss():
    try:
        data = request.json
        method = data.get('method', 'gauss')
        
        # 题目中的矩阵
        A = [
            [3, -2, 1, 4],
            [1, 3, 7, -7],
            [3, 6, 0, 3],
            [5, 5, -1, 8]
        ]
        b = [5, 2, -2, 5]
        
        if method == 'gauss':
            result = gauss_elimination_steps(A, b)
        elif method == 'pivot':
            result = gauss_with_pivot_steps(A, b)
        elif method == 'lu':
            result = lu_decomposition_steps(A, b)
        elif method == 'lu_pivot':
            result = lu_with_pivot_steps(A, b)
        else:
            return jsonify({'error': 'Unknown method'}), 400
            
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============ 案例2: SOR迭代法 ============
@app.route('/api/case2/sor', methods=['POST'])
def case2_sor():
    try:
        data = request.json
        omegas = data.get('omegas', [0.75, 1.0, 1.25, 1.5])
        
        A = [
            [-4, 1, 1, 1],
            [1, -4, 1, 1],
            [1, 1, -4, 1],
            [1, 1, 1, -4]
        ]
        b = [1, 1, 1, 1]
        exact_solution = [-1, -1, -1, -1]
        
        results = []
        for omega in omegas:
            result = sor_iteration(A, b, omega, exact_solution)
            results.append(result)
        
        # 确保所有布尔值都转换为Python bool
        for result in results:
            if 'converged' in result:
                result['converged'] = bool(result['converged'])
        
        return jsonify({'results': results})
    except Exception as e:
        import traceback
        print(f"Error in case2_sor: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@app.route('/api/case2/find_optimal', methods=['POST'])
def case2_find_optimal():
    try:
        A = [
            [-4, 1, 1, 1],
            [1, -4, 1, 1],
            [1, 1, -4, 1],
            [1, 1, 1, -4]
        ]
        b = [1, 1, 1, 1]
        exact_solution = [-1, -1, -1, -1]
        
        # 搜索最优omega
        best_omega = 1.0
        best_iterations = float('inf')
        
        omegas_test = [i * 0.05 for i in range(1, 40)]  # 0.05 到 1.95
        results = []
        
        for omega in omegas_test:
            result = sor_iteration(A, b, omega, exact_solution, max_iter=100)
            iterations = result['convergence_iter']
            results.append({'omega': omega, 'iterations': iterations})
            
            if iterations < best_iterations:
                best_iterations = iterations
                best_omega = omega
        
        return jsonify({
            'optimal_omega': best_omega,
            'iterations': best_iterations,
            'search_results': results
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============ 案例3: 用户画像分析 ============
@app.route('/api/case3/analyze', methods=['POST'])
def case3_analyze():
    try:
        result = linear_regression_analysis('data/user_data.csv')
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============ 案例4: 桥梁平衡 ============
@app.route('/api/case4/simple_beam', methods=['POST'])
def case4_simple_beam():
    try:
        # 简单简支梁示例
        result = solve_bridge_equilibrium(
            spans=[8],
            forces=[
                {'type': 'concentrated', 'magnitude': 15, 'position': 2},
                {'type': 'concentrated', 'magnitude': 25, 'position': 6}
            ]
        )
        return jsonify(result)
    except Exception as e:
        import traceback
        print(f"Error in case4_simple_beam: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@app.route('/api/case4/continuous_bridge', methods=['POST'])
def case4_continuous_bridge():
    try:
        data = request.json
        problem_type = data.get('type', '3_span')
        
        if problem_type == '3_span':
            result = solve_bridge_equilibrium(
                spans=[10, 12, 10],
                forces=[
                    {'type': 'concentrated', 'magnitude': 40, 'position': 3},
                    {'type': 'concentrated', 'magnitude': 50, 'position': 14},
                    {'type': 'moment', 'magnitude': 30, 'position': 27},
                    {'type': 'distributed', 'magnitude': 6, 'start': 0, 'end': 32}
                ]
            )
        elif problem_type == '10_span':
            # 10跨连续桥梁
            spans = [10] * 10
            forces = [
                {'type': 'distributed', 'magnitude': 5, 'start': 0, 'end': 100}
            ]
            result = solve_bridge_equilibrium(spans, forces)
        else:
            return jsonify({'error': 'Unknown bridge type'}), 400
            
        return jsonify(result)
    except Exception as e:
        import traceback
        print(f"Error in case4_continuous_bridge: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

# ============ 案例5: 光线追踪 ============
@app.route('/api/case5/ray_tracing', methods=['POST'])
def case5_ray_tracing():
    try:
        data = request.json
        num_rays = data.get('num_rays', 50)
        
        result = ray_tracing_simulation(num_rays)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============ 案例6: 共轭梯度法 ============
@app.route('/api/case6/conjugate_gradient', methods=['POST'])
def case6_cg():
    try:
        data = request.json
        size = data.get('size', 100)
        
        result = conjugate_gradient_method(size)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # 确保必要的目录存在
    os.makedirs('static/images', exist_ok=True)
    os.makedirs('data', exist_ok=True)
    
    app.run(debug=True, host='0.0.0.0', port=5000)