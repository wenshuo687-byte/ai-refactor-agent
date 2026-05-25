"""
使用示例 - 展示如何使用AI智能重构Agent
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.agents.coordinator import Coordinator
from src.agents.code_analyzer import CodeAnalyzerAgent
from src.agents.refactor_strategist import RefactorStrategistAgent
from src.core.code_parser import CodeParser
from src.core.metrics import CodeMetrics


def example_basic_usage():
    """基本使用示例"""
    print("=" * 60)
    print("示例1: 基本使用")
    print("=" * 60)

    # 初始化协调器
    coordinator = Coordinator()

    # 运行完整分析（需要提供实际的项目路径）
    # results = coordinator.run_full_analysis("/path/to/your/project")
    # print(f"分析结果: {results}")

    print("\n提示: 请提供实际的项目路径来运行分析")
    print("=" * 60)


def example_code_analysis():
    """代码分析示例"""
    print("\n" + "=" * 60)
    print("示例2: 代码分析")
    print("=" * 60)

    # 配置
    config = {
        "scanner": {
            "file_types": [".py"],
            "ignore_dirs": ["__pycache__", ".git"],
            "max_depth": 5
        },
        "quality_thresholds": {
            "cyclomatic_complexity": 10,
            "function_lines": 50,
            "max_parameters": 5
        }
    }

    # 初始化代码分析Agent
    analyzer = CodeAnalyzerAgent(config)

    # 分析当前目录（示例）
    # result = analyzer.analyze_project(".")
    # print(f"分析结果:")
    # print(f"  - 文件数: {result.total_files}")
    # print(f"  - 代码行数: {result.total_lines}")
    # print(f"  - 问题数: {len(result.issues)}")

    print("\n提示: 取消注释代码来运行实际分析")
    print("=" * 60)


def example_code_parser():
    """代码解析示例"""
    print("\n" + "=" * 60)
    print("示例3: 代码解析")
    print("=" * 60)

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

    print(f"解析结果:")
    print(f"  - 函数数: {len(structure.functions)}")
    print(f"  - 类数: {len(structure.classes)}")
    print(f"  - 导入数: {len(structure.imports)}")
    print(f"  - 总行数: {structure.total_lines}")
    print(f"  - 代码行数: {structure.code_lines}")

    print(f"\n函数详情:")
    for func in structure.functions:
        print(f"  - {func.name}: 行 {func.line_number}-{func.end_line}, "
              f"参数: {func.args}, 复杂度: {func.complexity}")

    print(f"\n类详情:")
    for cls in structure.classes:
        print(f"  - {cls.name}: 行 {cls.line_number}-{cls.end_line}, "
              f"方法数: {len(cls.methods)}")

    print("=" * 60)


def example_metrics():
    """代码指标示例"""
    print("\n" + "=" * 60)
    print("示例4: 代码指标计算")
    print("=" * 60)

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
        halstead_volume, cyclomatic_complexity, len(code.split("\n"))
    )

    print(f"代码指标:")
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

    print("=" * 60)


def example_refactor_plan():
    """重构计划示例"""
    print("\n" + "=" * 60)
    print("示例5: 重构计划生成")
    print("=" * 60)

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
            }
        ],
        "metrics": {
            "quality_score": 65
        }
    }

    # 生成重构计划
    plan = strategist.generate_refactor_plan(analysis_result)

    print(f"重构计划:")
    print(f"  - 建议数: {len(plan.suggestions)}")
    print(f"  - 总工作量: {plan.total_effort}")
    print(f"  - 预期质量提升: {plan.expected_improvement.get('improvement', 0)}分")

    print(f"\n重构建议:")
    for i, suggestion in enumerate(plan.suggestions, 1):
        print(f"  {i}. {suggestion.title}")
        print(f"     优先级: {suggestion.priority.value}")
        print(f"     文件: {suggestion.file_path}:{suggestion.line_number}")
        print(f"     收益: {', '.join(suggestion.benefits)}")

    print("=" * 60)


def main():
    """运行所有示例"""
    print("\n" + "=" * 60)
    print("AI智能重构Agent - 使用示例")
    print("=" * 60)

    # 运行示例
    example_basic_usage()
    example_code_analysis()
    example_code_parser()
    example_metrics()
    example_refactor_plan()

    print("\n" + "=" * 60)
    print("所有示例运行完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()