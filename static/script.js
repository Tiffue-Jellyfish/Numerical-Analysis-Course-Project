// 全局变量
let currentChart = null;

// 切换案例
function showCase(caseId) {
    // 隐藏所有案例
    document.querySelectorAll('.case-content').forEach(content => {
        content.classList.remove('active');
    });
    
    // 移除所有标签的active类
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // 显示选中的案例
    document.getElementById(caseId).classList.add('active');
    
    // 激活对应的标签
    event.target.classList.add('active');
}

// 显示/隐藏加载动画
function showLoading(show = true) {
    document.getElementById('loading').style.display = show ? 'flex' : 'none';
}

// ============ 案例1: 高斯消元法 ============
async function runCase1(method) {
    showLoading(true);
    
    try {
        const response = await fetch('/api/case1/gauss', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ method: method })
        });
        
        const data = await response.json();
        
        if (data.error) {
            alert('错误: ' + data.error);
            return;
        }
        
        displayCase1Result(data);
        
    } catch (error) {
        alert('请求失败: ' + error.message);
    } finally {
        showLoading(false);
    }
}

function displayCase1Result(data) {
    const resultDiv = document.getElementById('case1-result');
    const stepsDiv = document.getElementById('case1-steps');
    const solutionDiv = document.getElementById('case1-solution');
    
    resultDiv.style.display = 'block';
    
    // 显示步骤
    let stepsHTML = '<h3>求解步骤:</h3>';
    
    data.steps.forEach((step, index) => {
        stepsHTML += `
            <div class="step-item">
                <div class="step-header">
                    <div class="step-number">${step.step}</div>
                    <span>${step.description}</span>
                </div>
        `;
        
        if (step.matrix) {
            stepsHTML += '<div class="matrix-table"><table>';
            step.matrix.forEach(row => {
                stepsHTML += '<tr>';
                row.forEach(val => {
                    stepsHTML += `<td>${typeof val === 'number' ? val.toFixed(4) : val}</td>`;
                });
                stepsHTML += '</tr>';
            });
            stepsHTML += '</table></div>';
        }
        
        if (step.L) {
            stepsHTML += '<h4>矩阵 L:</h4><div class="matrix-table"><table>';
            step.L.forEach(row => {
                stepsHTML += '<tr>';
                row.forEach(val => {
                    stepsHTML += `<td>${val.toFixed(4)}</td>`;
                });
                stepsHTML += '</tr>';
            });
            stepsHTML += '</table></div>';
            
            stepsHTML += '<h4>矩阵 U:</h4><div class="matrix-table"><table>';
            step.U.forEach(row => {
                stepsHTML += '<tr>';
                row.forEach(val => {
                    stepsHTML += `<td>${val.toFixed(4)}</td>`;
                });
                stepsHTML += '</tr>';
            });
            stepsHTML += '</table></div>';
        }
        
        stepsHTML += '</div>';
    });
    
    stepsDiv.innerHTML = stepsHTML;
    
    // 显示解
    if (data.solution) {
        let solutionHTML = '<div class="solution-box"><h3>🎯 最终解:</h3>';
        data.solution.forEach((x, i) => {
            solutionHTML += `<div class="solution-item">x<sub>${i+1}</sub> = ${x.toFixed(8)}</div>`;
        });
        solutionHTML += `<p style="margin-top:15px;">方法: <strong>${data.method}</strong> | 总步数: ${data.num_steps}</p></div>`;
        solutionDiv.innerHTML = solutionHTML;
    }
}

// ============ 案例2: SOR迭代法 ============
async function runCase2() {
    showLoading(true);
    
    try {
        const response = await fetch('/api/case2/sor', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ omegas: [0.75, 1.0, 1.25, 1.5] })
        });
        
        const data = await response.json();
        
        if (data.error) {
            alert('错误: ' + data.error);
            return;
        }
        
        displayCase2Result(data.results);
        
    } catch (error) {
        alert('请求失败: ' + error.message);
    } finally {
        showLoading(false);
    }
}

async function findOptimalOmega() {
    showLoading(true);
    
    try {
        const response = await fetch('/api/case2/find_optimal', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        
        const data = await response.json();
        
        if (data.error) {
            alert('错误: ' + data.error);
            return;
        }
        
        alert(`最优松弛因子: ω = ${data.optimal_omega.toFixed(4)}\n收敛步数: ${data.iterations}`);
        
        // 绘制搜索结果
        plotOptimalOmegaSearch(data.search_results);
        
    } catch (error) {
        alert('请求失败: ' + error.message);
    } finally {
        showLoading(false);
    }
}

function displayCase2Result(results) {
    const resultDiv = document.getElementById('case2-result');
    const summaryDiv = document.getElementById('case2-summary');
    
    resultDiv.style.display = 'block';
    
    // 确保results是数组
    if (!Array.isArray(results)) {
        summaryDiv.innerHTML = '<p style="color:red;">数据格式错误</p>';
        return;
    }
    
    // 摘要信息
    let summaryHTML = '<div class="stats-grid">';
    
    results.forEach(result => {
        summaryHTML += `
            <div class="stat-card">
                <div class="stat-label">ω = ${result.omega}</div>
                <div class="stat-value">${result.convergence_iter}</div>
                <div class="stat-label">迭代次数</div>
                <div style="margin-top:10px; font-size:0.9em; color:#666;">
                    最终解: [${result.final_solution.map(x => x.toFixed(4)).join(', ')}]
                </div>
            </div>
        `;
    });
    
    summaryHTML += '</div>';
    summaryDiv.innerHTML = summaryHTML;
    
    // 绘制收敛曲线
    plotConvergenceCurves(results);
}

function plotConvergenceCurves(results) {
    const ctx = document.getElementById('case2-chart');
    
    if (currentChart) {
        currentChart.destroy();
    }
    
    const datasets = results.map((result, index) => {
        const colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444'];
        return {
            label: `ω = ${result.omega}`,
            data: result.iterations.map(iter => ({
                x: iter.iteration,
                y: iter.exact_error
            })),
            borderColor: colors[index],
            backgroundColor: colors[index] + '33',
            borderWidth: 2,
            pointRadius: 3
        };
    });
    
    currentChart = new Chart(ctx, {
        type: 'line',
        data: { datasets: datasets },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                x: {
                    type: 'linear',
                    title: { display: true, text: '迭代次数' }
                },
                y: {
                    type: 'logarithmic',
                    title: { display: true, text: '误差 (对数尺度)' }
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: 'SOR迭代法收敛曲线对比',
                    font: { size: 16, weight: 'bold' }
                },
                legend: { position: 'top' }
            }
        }
    });
}

function plotOptimalOmegaSearch(searchResults) {
    const ctx = document.getElementById('case2-chart');
    
    if (currentChart) {
        currentChart.destroy();
    }
    
    currentChart = new Chart(ctx, {
        type: 'line',
        data: {
            datasets: [{
                label: '收敛步数',
                data: searchResults.map(r => ({ x: r.omega, y: r.iterations })),
                borderColor: '#667eea',
                backgroundColor: '#667eea33',
                borderWidth: 3,
                pointRadius: 4,
                pointHoverRadius: 6
            }]
        },
        options: {
            responsive: true,
            scales: {
                x: { title: { display: true, text: '松弛因子 ω' } },
                y: { title: { display: true, text: '收敛步数' } }
            },
            plugins: {
                title: {
                    display: true,
                    text: '最优松弛因子搜索',
                    font: { size: 16, weight: 'bold' }
                }
            }
        }
    });
}

// ============ 案例3: 用户画像 ============
async function runCase3() {
    showLoading(true);
    
    try {
        const response = await fetch('/api/case3/analyze', { method: 'POST' });
        const data = await response.json();
        
        if (data.error) {
            alert('错误: ' + data.error);
            return;
        }
        
        displayCase3Result(data);
        
    } catch (error) {
        alert('请求失败: ' + error.message);
    } finally {
        showLoading(false);
    }
}

function displayCase3Result(data) {
    const resultDiv = document.getElementById('case3-result');
    const coeffDiv = document.getElementById('case3-coefficients');
    const metricsDiv = document.getElementById('case3-metrics');
    
    resultDiv.style.display = 'block';
    
    // 显示评估指标
    metricsDiv.innerHTML = `
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">R² (决定系数)</div>
                <div class="stat-value">${data.r_squared.toFixed(4)}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">RMSE</div>
                <div class="stat-value">${data.rmse.toFixed(4)}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">样本数量</div>
                <div class="stat-value">${data.num_samples}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">特征数量</div>
                <div class="stat-value">${data.num_features}</div>
            </div>
        </div>
    `;
    
    // 显示系数
    let coeffHTML = '<h3>特征系数 (按重要性排序):</h3><div class="coefficient-list">';
    
    data.coefficients_sorted.forEach(coeff => {
        const barWidth = (Math.abs(coeff.coefficient) / Math.max(...data.coefficients_sorted.map(c => Math.abs(c.coefficient)))) * 100;
        coeffHTML += `
            <div class="coefficient-item">
                <div>
                    <div class="coefficient-name">${coeff.feature}</div>
                    <div class="coefficient-bar" style="width: ${barWidth}%"></div>
                </div>
                <div class="coefficient-value">${coeff.coefficient.toFixed(6)}</div>
            </div>
        `;
    });
    
    coeffHTML += '</div>';
    coeffDiv.innerHTML = coeffHTML;
    
    // 绘制特征重要性图表
    plotFeatureImportance(data.coefficients_sorted);
}

function plotFeatureImportance(coefficients) {
    const ctx = document.getElementById('case3-chart');
    
    if (currentChart) {
        currentChart.destroy();
    }
    
    currentChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: coefficients.map(c => c.feature),
            datasets: [{
                label: '系数绝对值',
                data: coefficients.map(c => Math.abs(c.coefficient)),
                backgroundColor: 'rgba(102, 126, 234, 0.7)',
                borderColor: 'rgb(102, 126, 234)',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            indexAxis: 'y',
            plugins: {
                title: {
                    display: true,
                    text: '特征重要性分析',
                    font: { size: 16, weight: 'bold' }
                }
            }
        }
    });
}

// ============ 案例4: 桥梁平衡 ============
async function runCase4Simple() {
    showLoading(true);
    
    try {
        const response = await fetch('/api/case4/simple_beam', { method: 'POST' });
        const data = await response.json();
        
        displayCase4Result(data);
        
    } catch (error) {
        alert('请求失败: ' + error.message);
    } finally {
        showLoading(false);
    }
}

async function runCase4(type) {
    showLoading(true);
    
    try {
        const response = await fetch('/api/case4/continuous_bridge', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ type: type })
        });
        
        const data = await response.json();
        displayCase4Result(data);
        
    } catch (error) {
        alert('请求失败: ' + error.message);
    } finally {
        showLoading(false);
    }
}

function displayCase4Result(data) {
    const resultDiv = document.getElementById('case4-result');
    const imageDiv = document.getElementById('case4-image');
    const reactionsDiv = document.getElementById('case4-reactions');
    const verificationDiv = document.getElementById('case4-verification');
    
    resultDiv.style.display = 'block';
    
    console.log('Case4 data:', data);  // 调试信息
    
    // 显示图片
    if (data.figure_path) {
        const imgPath = data.figure_path.startsWith('/') ? data.figure_path : '/' + data.figure_path;
        imageDiv.innerHTML = `
            <div class="image-display">
                <img src="${imgPath}?t=${Date.now()}" alt="桥梁结构图" onerror="this.onerror=null; this.src='data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' width=\'400\' height=\'200\'%3E%3Ctext x=\'50%25\' y=\'50%25\' text-anchor=\'middle\' fill=\'red\'%3E图片加载失败%3C/text%3E%3C/svg%3E';" />
                <p style="text-align:center; color:#666; margin-top:10px;">图片路径: ${data.figure_path}</p>
            </div>
        `;
    } else {
        imageDiv.innerHTML = '<p style="color:red;">图片生成失败</p>';
    }
    
    // 显示支座反力
    let reactionsHTML = '<h3>支座反力:</h3><table class="data-table"><thead><tr><th>支座</th><th>位置 (m)</th><th>反力 (kN)</th></tr></thead><tbody>';
    
    // 确保数据是数组
    const reactions = Array.isArray(data.support_reactions) ? data.support_reactions : [];
    const positions = Array.isArray(data.support_positions) ? data.support_positions : [];
    
    if (reactions.length === 0) {
        reactionsHTML += '<tr><td colspan="3" style="text-align:center; color:red;">无数据</td></tr>';
    } else {
        reactions.forEach((R, i) => {
            reactionsHTML += `
                <tr>
                    <td>支座 ${i+1}</td>
                    <td>${positions[i] ? positions[i].toFixed(2) : '0.00'}</td>
                    <td>${R.toFixed(4)}</td>
                </tr>
            `;
        });
    }
    
    reactionsHTML += '</tbody></table>';
    reactionsDiv.innerHTML = reactionsHTML;
    
    // 显示验证结果
    const verification = data.verification || {};
    const isBalanced = verification.is_balanced || false;
    
    verificationDiv.innerHTML = `
        <div class="${isBalanced ? 'solution-box' : 'problem-box'}" style="margin-top:20px;">
            <h3>平衡验证:</h3>
            <p>力平衡误差: ${verification.force_balance_error !== undefined ? verification.force_balance_error.toExponential(4) : 'N/A'}</p>
            <p>力矩平衡误差: ${verification.moment_balance_error !== undefined ? verification.moment_balance_error.toExponential(4) : 'N/A'}</p>
            ${verification.total_reaction !== undefined ? `<p>支座反力总和: ${verification.total_reaction.toFixed(4)} kN</p>` : ''}
            ${verification.total_external !== undefined ? `<p>外力总和: ${verification.total_external.toFixed(4)} kN</p>` : ''}
            <p><strong>${isBalanced ? '✅ 方程组求解正确，满足平衡条件' : '⚠️ 请检查数据'}</strong></p>
        </div>
    `;
}

// ============ 案例5: 光线追踪 ============
async function runCase5() {
    showLoading(true);
    
    const numRays = document.getElementById('num-rays').value;
    
    try {
        const response = await fetch('/api/case5/ray_tracing', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ num_rays: parseInt(numRays) })
        });
        
        const data = await response.json();
        displayCase5Result(data);
        
    } catch (error) {
        alert('请求失败: ' + error.message);
    } finally {
        showLoading(false);
    }
}

function displayCase5Result(data) {
    const resultDiv = document.getElementById('case5-result');
    const imageDiv = document.getElementById('case5-image');
    const statsDiv = document.getElementById('case5-stats');
    
    resultDiv.style.display = 'block';
    
    imageDiv.innerHTML = `
        <div class="image-display">
            <img src="/${data.figure_path}" alt="光线追踪" />
        </div>
    `;
    
    statsDiv.innerHTML = `
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">光线数量</div>
                <div class="stat-value">${data.num_rays}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">交点总数</div>
                <div class="stat-value">${data.total_intersections}</div>
            </div>
        </div>
    `;
}

// ============ 案例6: 共轭梯度法 ============
async function runCase6() {
    showLoading(true);
    
    const size = document.getElementById('matrix-size').value;
    
    try {
        const response = await fetch('/api/case6/conjugate_gradient', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ size: parseInt(size) })
        });
        
        const data = await response.json();
        displayCase6Result(data);
        
    } catch (error) {
        alert('请求失败: ' + error.message);
    } finally {
        showLoading(false);
    }
}

function displayCase6Result(data) {
    const resultDiv = document.getElementById('case6-result');
    const imageDiv = document.getElementById('case6-image');
    const statsDiv = document.getElementById('case6-stats');
    
    resultDiv.style.display = 'block';
    
    imageDiv.innerHTML = `
        <div class="image-display">
            <img src="/${data.figure_path}" alt="共轭梯度法" />
        </div>
    `;
    
    statsDiv.innerHTML = `
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">矩阵规模</div>
                <div class="stat-value">${data.matrix_size}×${data.matrix_size}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">迭代次数</div>
                <div class="stat-value">${data.iterations}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">最终残差</div>
                <div class="stat-value">${data.final_residual.toExponential(2)}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">相对误差</div>
                <div class="stat-value">${data.relative_error.toExponential(2)}</div>
            </div>
        </div>
    `;
}

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    console.log('数值方法演示系统已加载');
});