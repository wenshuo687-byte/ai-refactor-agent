"""
代码质量指标 - 负责计算各种代码质量指标
"""

from typing import List, Dict, Any
from dataclasses import dataclass


@dataclass
class QualityMetrics:
    """代码质量指标"""
    cyclomatic_complexity: int
    cognitive_complexity: int
    lines_of_code: int
    maintainability_index: float
    code_coverage: float
    duplicate_lines: int
    code_smells: int
    technical_debt: float  # 小时


class CodeMetrics:
    """
    代码质量指标计算器

    职责：
    1. 计算圈复杂度
    2. 计算认知复杂度
    3. 计算可维护性指数
    4. 检测代码异味
    5. 评估技术债
    """

    def __init__(self):
        pass

    def calculate_cyclomatic_complexity(self, code: str) -> int:
        """
        计算圈复杂度

        Args:
            code: 代码内容

        Returns:
            int: 圈复杂度
        """
        import ast

        try:
            tree = ast.parse(code)
        except SyntaxError:
            return 0

        complexity = 1  # 基础复杂度

        for node in ast.walk(tree):
            # 条件语句
            if isinstance(node, ast.If):
                complexity += 1
            # 循环语句
            elif isinstance(node, (ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            # 异常处理
            elif isinstance(node, ast.Try):
                complexity += len(node.handlers)
            elif isinstance(node, ast.ExceptHandler):
                complexity += 1
            # 逻辑运算符
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
            # 列表推导式
            elif isinstance(node, (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)):
                complexity += 1

        return complexity

    def calculate_cognitive_complexity(self, code: str) -> int:
        """
        计算认知复杂度

        认知复杂度考虑了：
        1. 控制流结构的嵌套
        2. 逻辑运算符的连续使用
        3. 递归调用

        Args:
            code: 代码内容

        Returns:
            int: 认知复杂度
        """
        import ast

        try:
            tree = ast.parse(code)
        except SyntaxError:
            return 0

        complexity = 0
        nesting_level = 0

        def _calculate_node_complexity(node: ast.AST, level: int) -> int:
            """计算单个节点的复杂度"""
            node_complexity = 0

            # 控制流结构增加复杂度
            if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                node_complexity += 1 + level  # 嵌套越深，复杂度越高
            elif isinstance(node, ast.Try):
                node_complexity += 1 + level
            elif isinstance(node, ast.ExceptHandler):
                node_complexity += 1
            elif isinstance(node, ast.BoolOp):
                # 连续的逻辑运算符增加复杂度
                node_complexity += len(node.values) - 1

            return node_complexity

        def _walk_with_nesting(node: ast.AST, level: int):
            """遍历AST并计算嵌套层级"""
            nonlocal complexity

            complexity += _calculate_node_complexity(node, level)

            # 增加嵌套层级的节点
            increase_nesting = isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor, ast.Try, ast.With, ast.AsyncWith))

            for child in ast.iter_child_nodes(node):
                new_level = level + 1 if increase_nesting else level
                _walk_with_nesting(child, new_level)

        _walk_with_nesting(tree, 0)
        return complexity

    def calculate_maintainability_index(self, halstead_volume: float, cyclomatic_complexity: int, lines_of_code: int) -> float:
        """
        计算可维护性指数

        公式：MI = 171 - 5.2 * ln(HV) - 0.23 * CC - 16.2 * ln(LOC)

        Args:
            halstead_volume: Halstead体积
            cyclomatic_complexity: 圈复杂度
            lines_of_code: 代码行数

        Returns:
            float: 可维护性指数 (0-100)
        """
        import math

        if lines_of_code == 0:
            return 100.0

        # 避免log(0)
        hv = max(halstead_volume, 1)
        loc = max(lines_of_code, 1)

        mi = 171 - 5.2 * math.log(hv) - 0.23 * cyclomatic_complexity - 16.2 * math.log(loc)

        # 归一化到0-100
        mi = max(0, min(100, mi))

        return round(mi, 2)

    def calculate_halstead_volume(self, code: str) -> float:
        """
        计算Halstead体积

        Args:
            code: 代码内容

        Returns:
            float: Halstead体积
        """
        import math
        import ast

        try:
            tree = ast.parse(code)
        except SyntaxError:
            return 0.0

        # 统计操作符和操作数
        operators = set()
        operands = set()
        operator_count = 0
        operand_count = 0

        for node in ast.walk(tree):
            # 操作符
            if isinstance(node, ast.Add):
                operators.add("+")
                operator_count += 1
            elif isinstance(node, ast.Sub):
                operators.add("-")
                operator_count += 1
            elif isinstance(node, ast.Mult):
                operators.add("*")
                operator_count += 1
            elif isinstance(node, ast.Div):
                operators.add("/")
                operator_count += 1
            elif isinstance(node, ast.Mod):
                operators.add("%")
                operator_count += 1
            elif isinstance(node, ast.Pow):
                operators.add("**")
                operator_count += 1
            elif isinstance(node, ast.LShift):
                operators.add("<<")
                operator_count += 1
            elif isinstance(node, ast.RShift):
                operators.add(">>")
                operator_count += 1
            elif isinstance(node, ast.BitOr):
                operators.add("|")
                operator_count += 1
            elif isinstance(node, ast.BitXor):
                operators.add("^")
                operator_count += 1
            elif isinstance(node, ast.BitAnd):
                operators.add("&")
                operator_count += 1
            elif isinstance(node, ast.FloorDiv):
                operators.add("//")
                operator_count += 1
            elif isinstance(node, ast.Eq):
                operators.add("==")
                operator_count += 1
            elif isinstance(node, ast.NotEq):
                operators.add("!=")
                operator_count += 1
            elif isinstance(node, ast.Lt):
                operators.add("<")
                operator_count += 1
            elif isinstance(node, ast.LtE):
                operators.add("<=")
                operator_count += 1
            elif isinstance(node, ast.Gt):
                operators.add(">")
                operator_count += 1
            elif isinstance(node, ast.GtE):
                operators.add(">=")
                operator_count += 1
            elif isinstance(node, ast.And):
                operators.add("and")
                operator_count += 1
            elif isinstance(node, ast.Or):
                operators.add("or")
                operator_count += 1
            elif isinstance(node, ast.Not):
                operators.add("not")
                operator_count += 1
            elif isinstance(node, ast.Is):
                operators.add("is")
                operator_count += 1
            elif isinstance(node, ast.IsNot):
                operators.add("is not")
                operator_count += 1
            elif isinstance(node, ast.In):
                operators.add("in")
                operator_count += 1
            elif isinstance(node, ast.NotIn):
                operators.add("not in")
                operator_count += 1

            # 操作数
            elif isinstance(node, ast.Name):
                operands.add(node.id)
                operand_count += 1
            elif isinstance(node, ast.Constant):
                operands.add(str(node.value))
                operand_count += 1

        # 计算Halstead体积
        n1 = len(operators)  # 不同操作符数量
        n2 = len(operands)   # 不同操作数数量
        N1 = operator_count  # 操作符总数
        N2 = operand_count   # 操作数总数

        # 程序词汇量
        vocabulary = n1 + n2
        # 程序长度
        length = N1 + N2

        if vocabulary == 0:
            return 0.0

        # Halstead体积 = N * log2(n)
        volume = length * math.log2(vocabulary)

        return round(volume, 2)

    def detect_code_smells(self, code: str) -> List[Dict[str, Any]]:
        """
        检测代码异味

        Args:
            code: 代码内容

        Returns:
            List[Dict]: 代码异味列表
        """
        import ast

        smells = []

        try:
            tree = ast.parse(code)
        except SyntaxError:
            return smells

        lines = code.split("\n")

        for node in ast.walk(tree):
            # 检测过长函数
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if hasattr(node, "end_lineno") and node.end_lineno:
                    func_lines = node.end_lineno - node.lineno + 1
                    if func_lines > 50:
                        smells.append({
                            "type": "long_method",
                            "message": f"函数 '{node.name}' 过长 ({func_lines}行)",
                            "line": node.lineno,
                            "severity": "medium"
                        })

                # 检测参数过多
                args = node.args
                total_params = len(args.args) + len(args.posonlyargs) + len(args.kwonlyargs)
                if total_params > 5:
                    smells.append({
                        "type": "long_parameter_list",
                        "message": f"函数 '{node.name}' 参数过多 ({total_params}个)",
                        "line": node.lineno,
                        "severity": "medium"
                    })

            # 检测过大的类
            elif isinstance(node, ast.ClassDef):
                if hasattr(node, "end_lineno") and node.end_lineno:
                    class_lines = node.end_lineno - node.lineno + 1
                    if class_lines > 300:
                        smells.append({
                            "type": "large_class",
                            "message": f"类 '{node.name}' 过大 ({class_lines}行)",
                            "line": node.lineno,
                            "severity": "high"
                        })

            # 检测魔法数字
            elif isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
                # 排除常见的常量
                if node.value not in (0, 1, 2, -1, 100, 0.0, 1.0):
                    # 检查是否在赋值语句中
                    parent = getattr(node, "_parent", None)
                    if not isinstance(parent, ast.Assign):
                        smells.append({
                            "type": "magic_number",
                            "message": f"魔法数字: {node.value}",
                            "line": node.lineno,
                            "severity": "low"
                        })

        return smells

    def estimate_technical_debt(self, code_smells: List[Dict[str, Any]], complexity: int, duplicate_lines: int) -> float:
        """
        估算技术债（小时）

        Args:
            code_smells: 代码异味列表
            complexity: 圈复杂度
            duplicate_lines: 重复行数

        Returns:
            float: 技术债（小时）
        """
        debt = 0.0

        # 基于代码异味估算
        smell_weights = {
            "long_method": 2.0,
            "long_parameter_list": 1.0,
            "large_class": 4.0,
            "magic_number": 0.5,
            "duplicate_code": 1.5
        }

        for smell in code_smells:
            smell_type = smell.get("type", "")
            debt += smell_weights.get(smell_type, 1.0)

        # 基于复杂度估算
        if complexity > 10:
            debt += (complexity - 10) * 0.5

        # 基于重复代码估算
        debt += duplicate_lines * 0.1

        return round(debt, 2)

    def calculate_code_quality_score(self, metrics: Dict[str, Any]) -> int:
        """
        计算代码质量分数 (0-100)

        Args:
            metrics: 各种指标

        Returns:
            int: 质量分数
        """
        score = 100

        # 复杂度扣分
        complexity = metrics.get("cyclomatic_complexity", 0)
        if complexity > 10:
            score -= min(30, (complexity - 10) * 2)

        # 可维护性指数扣分
        maintainability = metrics.get("maintainability_index", 100)
        score -= max(0, (100 - maintainability) * 0.3)

        # 重复代码扣分
        duplicate_ratio = metrics.get("duplicate_ratio", 0)
        score -= duplicate_ratio * 20

        # 代码异味扣分
        code_smells_count = metrics.get("code_smells_count", 0)
        score -= min(20, code_smells_count * 2)

        return max(0, min(100, int(score)))

    def generate_quality_report(self, file_path: str, code: str) -> Dict[str, Any]:
        """
        生成质量报告

        Args:
            file_path: 文件路径
            code: 代码内容

        Returns:
            Dict: 质量报告
        """
        lines = code.split("\n")

        # 计算各种指标
        cyclomatic_complexity = self.calculate_cyclomatic_complexity(code)
        cognitive_complexity = self.calculate_cognitive_complexity(code)
        halstead_volume = self.calculate_halstead_volume(code)
        maintainability_index = self.calculate_maintainability_index(halstead_volume, cyclomatic_complexity, len(lines))
        code_smells = self.detect_code_smells(code)
        technical_debt = self.estimate_technical_debt(code_smells, cyclomatic_complexity, 0)

        # 计算质量分数
        quality_score = self.calculate_code_quality_score({
            "cyclomatic_complexity": cyclomatic_complexity,
            "maintainability_index": maintainability_index,
            "duplicate_ratio": 0,
            "code_smells_count": len(code_smells)
        })

        return {
            "file_path": file_path,
            "lines_of_code": len(lines),
            "cyclomatic_complexity": cyclomatic_complexity,
            "cognitive_complexity": cognitive_complexity,
            "halstead_volume": halstead_volume,
            "maintainability_index": maintainability_index,
            "code_smells": code_smells,
            "technical_debt_hours": technical_debt,
            "quality_score": quality_score
        }