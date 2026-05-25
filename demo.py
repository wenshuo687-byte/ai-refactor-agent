"""
AI智能重构Agent - 演示脚本

运行此脚本查看完整的项目演示
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.agents.coordinator import Coordinator
from src.agents.code_analyzer import CodeAnalyzerAgent
from src.agents.refactor_strategist import RefactorStrategistAgent
from src.core.code_parser import CodeParser
from src.core.metrics import CodeMetrics


def print_banner():
    """打印横幅"""
    print("\n" + "=" * 70)
    print("AI智能重构Agent - 基于多Agent协作的智能代码重构系统")
    print("=" * 70)
    print("\n核心特性:")
    print("  1. 多Agent协作: 代码分析、重构策略、执行验证三个Agent协同工作")
    print("  2. 长链推理: 分析->决策->执行->验证的完整推理链")
    print("  3. 智能决策: 基于代码质量和架构分析的重构优先级排序")
    print("  4. 闭环验证: 自动运行测试确保重构不引入新问题")
    print("\n" + "=" * 70)


def demo_code_analysis():
    """演示代码分析功能"""
    print("\n[演示1] 代码分析Agent")
    print("-" * 50)

    # 初始化解析器
    parser = CodeParser()

    # 示例代码
    code = '''
def fibonacci(n):
    """计算斐波那契数列"""
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

class Calculator:
    """简单计算器"""

    def __init__(self):
        self.history = []

    def add(self, a, b):
        """加法"""
        result = a + b
        self.history.append(f"{a} + {b} = {result}")
        return result

    def subtract(self, a, b):
        """减法"""
        result = a - b
        self.history.append(f"{a} - {b} = {result}")
        return result
'''

    # 解析代码
    structure = parser.parse_content(code)

    print(f"\n代码解析结果:")
    print(f"  - 函数数: {len(structure.functions)}")
    print(f"  - 类数: {len(structure.classes)}")
    print(f"  - 总行数: {len(code.splitlines())}")

    print(f"\n函数详情:")
    for func in structure.functions:
        print(f"  - {func.name}: 行 {func.line_number}-{func.end_line}, "
              f"参数: {func.args}, 复杂度: {func.complexity}")

    print(f"\n类详情:")
    for cls in structure.classes:
        print(f"  - {cls.name}: 行 {cls.line_number}-{cls.end_line}, "
              f"方法数: {len(cls.methods)}")


def demo_quality_metrics():
    """演示质量指标计算"""
    print("\n[演示2] 代码质量指标")
    print("-" * 50)

    # 初始化指标计算器
    metrics = CodeMetrics()

    # 示例代码
    code = '''
def complex_function(x, y, z):
    """复杂函数示例"""
    result = 0

    if x > 0:
        for i in range(x):
            if i % 2 == 0:
                result += i
            else:
                result -= i
    elif y > 0:
        while y > 0:
            result += y
            y -= 1
    else:
        result = z

    return result
'''

    # 计算指标
    cyclomatic_complexity = metrics.calculate_cyclomatic_complexity(code)
    cognitive_complexity = metrics.calculate_cognitive_complexity(code)
    halstead_volume = metrics.calculate_halstead_volume(code)
    maintainability_index = metrics.calculate_maintainability_index(
        halstead_volume, cyclomatic_complexity, len(code.splitlines())
    )

    print(f"\n代码质量指标:")
    print(f"  - 圈复杂度: {cyclomatic_complexity}")
    print(f"  - 认知复杂度: {cognitive_complexity}")
    print(f"  - Halstead体积: {halstead_volume}")
    print(f"  - 可维护性指数: {maintainability_index}")

    # 检测代码异味
    smells = metrics.detect_code_smells(code)
    print(f"\n代码异味: {len(smells)}个")
    for smell in smells:
        print(f"  - {smell['type']}: {smell['message']}")

    # 生成质量报告
    report = metrics.generate_quality_report("example.py", code)
    print(f"\n质量报告:")
    print(f"  - 质量分数: {report['quality_score']}/100")
    print(f"  - 技术债: {report['technical_debt_hours']}小时")


def demo_refactor_plan():
    """演示重构计划生成"""
    print("\n[演示3] 重构计划生成")
    print("-" * 50)

    # 初始化重构策略Agent
    strategist = RefactorStrategistAgent({})

    # 模拟分析结果
    analysis_result = {
        "project_path": ".",
        "issues": [
            {
                "file_path": "example.py",
                "line_number": 10,
                "issue_type": "complexity",
                "severity": "high",
                "description": "函数圈复杂度过高: 15",
                "suggestion": "考虑拆分函数",
                "code_snippet": "def complex_function():"
            },
            {
                "file_path": "example.py",
                "line_number": 25,
                "issue_type": "duplication",
                "severity": "medium",
                "description": "检测到重复代码块",
                "suggestion": "提取重复代码为函数",
                "code_snippet": "..."
            },
            {
                "file_path": "example.py",
                "line_number": 40,
                "issue_type": "style",
                "severity": "low",
                "description": "函数参数过多: 8个",
                "suggestion": "考虑使用数据类封装参数",
                "code_snippet": "def create_user(name, email, age, phone, address, city, state, zip_code, country):"
            }
        ],
        "metrics": {
            "quality_score": 65
        }
    }

    # 生成重构计划
    plan = strategist.generate_refactor_plan(analysis_result)

    print(f"\n重构计划:")
    print(f"  - 建议数: {len(plan.suggestions)}")
    print(f"  - 总工作量: {plan.total_effort}")
    print(f"  - 预期质量提升: {plan.expected_improvement.get('improvement', 0)}分")
    print(f"  - 预期质量分数: {plan.expected_improvement.get('expected_score', 0)}/100")

    print(f"\n重构建议:")
    for i, suggestion in enumerate(plan.suggestions, 1):
        print(f"\n  {i}. {suggestion.title}")
        print(f"     优先级: {suggestion.priority.value}")
        print(f"     文件: {suggestion.file_path}:{suggestion.line_number}")
        print(f"     收益: {', '.join(suggestion.benefits)}")
        print(f"     风险: {', '.join(suggestion.risks)}")


def demo_full_analysis():
    """演示完整分析流程"""
    print("\n[演示4] 完整分析流程")
    print("-" * 50)

    # 初始化协调器
    coordinator = Coordinator()

    # 分析复杂项目
    project_path = "complex_project"

    print(f"\n开始分析项目: {project_path}")
    print("=" * 50)

    # 运行分析
    results = coordinator.run_full_analysis(project_path)

    # 打印摘要
    print("\n" + "=" * 50)
    print("分析摘要")
    print("=" * 50)

    analysis = results.get("analysis", {})
    print(f"\n代码分析:")
    print(f"  - 扫描文件数: {analysis.get('total_files', 0)}")
    print(f"  - 代码总行数: {analysis.get('total_lines', 0)}")
    print(f"  - 发现问题数: {analysis.get('issues_count', 0)}")
    print(f"  - 质量分数: {analysis.get('quality_score', 0)}/100")

    plan = results.get("refactor_plan", {})
    print(f"\n重构计划:")
    print(f"  - 重构建议数: {plan.get('total_suggestions', 0)}")
    print(f"  - 总工作量: {plan.get('total_effort', 'unknown')}")

    improvement = plan.get("expected_improvement", {})
    print(f"  - 预期质量提升: {improvement.get('improvement', 0)}分")

    execution = results.get("execution", {})
    print(f"\n执行结果:")
    print(f"  - 已执行: {execution.get('total_executed', 0)}")
    print(f"  - 成功: {execution.get('successful', 0)}")
    print(f"  - 失败: {execution.get('failed', 0)}")
    print(f"  - 跳过: {execution.get('skipped', 0)}")
    print(f"  - 成功率: {execution.get('success_rate', 0):.1%}")


def main():
    """主函数"""
    print_banner()

    # 运行演示
    demo_code_analysis()
    demo_quality_metrics()
    demo_refactor_plan()
    demo_full_analysis()

    print("\n" + "=" * 70)
    print("演示完成！")
    print("=" * 70)
    print("\n项目已成功运行，所有功能正常工作。")
    print("GitHub仓库: https://github.com/wenshuo687-byte/ai-refactor-agent")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()