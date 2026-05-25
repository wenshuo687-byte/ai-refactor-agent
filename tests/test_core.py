"""
核心模块测试
"""

import pytest
from src.core.code_parser import CodeParser
from src.core.metrics import CodeMetrics


class TestCodeParser:
    """代码解析器测试"""

    def setup_method(self):
        """测试前准备"""
        self.parser = CodeParser()

    def test_parse_content(self):
        """测试解析代码内容"""
        code = '''
def hello():
    """问候函数"""
    print("Hello, World!")

class MyClass:
    """示例类"""
    def __init__(self):
        self.value = 42

    def get_value(self):
        return self.value
'''
        structure = self.parser.parse_content(code)

        assert structure is not None
        assert len(structure.functions) == 1
        assert len(structure.classes) == 1
        assert structure.functions[0].name == "hello"
        assert structure.classes[0].name == "MyClass"

    def test_extract_functions(self):
        """测试提取函数信息"""
        import ast

        code = '''
def simple_func():
    pass

async def async_func(x, y):
    return x + y

@decorator
def decorated_func(a: int, b: str) -> bool:
    return True
'''
        tree = ast.parse(code)
        functions = self.parser._extract_functions(tree)

        assert len(functions) == 3
        assert functions[0].name == "simple_func"
        assert functions[1].name == "async_func"
        assert functions[1].is_async == True
        assert functions[2].name == "decorated_func"
        assert len(functions[2].args) == 2

    def test_extract_classes(self):
        """测试提取类信息"""
        import ast

        code = '''
class Base:
    pass

class Child(Base):
    def __init__(self):
        super().__init__()

    def method(self):
        pass
'''
        tree = ast.parse(code)
        classes = self.parser._extract_classes(tree)

        assert len(classes) == 2
        assert classes[0].name == "Base"
        assert classes[1].name == "Child"
        assert "Base" in classes[1].base_classes
        assert len(classes[1].methods) == 2

    def test_extract_imports(self):
        """测试提取导入信息"""
        import ast

        code = '''
import os
import sys
from pathlib import Path
from typing import List, Dict
'''
        tree = ast.parse(code)
        imports = self.parser._extract_imports(tree)

        assert len(imports) == 4
        assert imports[0].module == ""
        assert "os" in imports[0].names
        assert imports[2].is_from_import == True
        assert imports[2].module == "pathlib"

    def test_calculate_complexity(self):
        """测试复杂度计算"""
        import ast

        code = '''
def complex_func(x):
    if x > 0:
        for i in range(x):
            if i % 2 == 0:
                print(i)
    elif x < 0:
        while x < 0:
            x += 1
    return x
'''
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                complexity = self.parser._calculate_complexity(node)
                assert complexity > 1

    def test_count_lines(self):
        """测试行数统计"""
        lines = [
            "# 注释",
            "def func():",
            "    pass",
            "",
            "x = 1  # 行内注释",
        ]

        code_lines, comment_lines, blank_lines = self.parser._count_lines(lines)

        assert code_lines == 3  # def, pass, x = 1
        assert comment_lines == 1  # # 注释
        assert blank_lines == 1  # 空行

    def test_get_code_metrics(self):
        """测试获取代码指标"""
        from src.core.code_parser import CodeStructure, FunctionInfo, ClassInfo, ImportInfo

        structure = CodeStructure(
            file_path="test.py",
            functions=[
                FunctionInfo("func1", 1, 10, [], [], False, 5, 10),
                FunctionInfo("func2", 12, 20, [], [], False, 3, 8),
            ],
            classes=[
                ClassInfo("MyClass", 22, 50, [], [], [], 28),
            ],
            imports=[
                ImportInfo("os", ["path"], 1, True),
            ],
            total_lines=100,
            code_lines=80,
            comment_lines=10,
            blank_lines=10
        )

        metrics = self.parser.get_code_metrics(structure)

        assert metrics["total_functions"] == 2
        assert metrics["total_classes"] == 1
        assert metrics["avg_complexity"] == 4.0  # (5+3)/2
        assert metrics["max_complexity"] == 5


class TestCodeMetrics:
    """代码质量指标测试"""

    def setup_method(self):
        """测试前准备"""
        self.metrics = CodeMetrics()

    def test_calculate_cyclomatic_complexity(self):
        """测试圈复杂度计算"""
        code = '''
def simple():
    return 42

def complex(x):
    if x > 0:
        if x > 10:
            return x * 2
        else:
            return x + 1
    else:
        return 0
'''
        complexity = self.metrics.calculate_cyclomatic_complexity(code)

        # simple函数复杂度为1，complex函数复杂度至少为3
        assert complexity >= 4

    def test_calculate_cognitive_complexity(self):
        """测试认知复杂度计算"""
        code = '''
def nested(x):
    if x > 0:
        for i in range(x):
            if i % 2 == 0:
                print(i)
'''
        complexity = self.metrics.calculate_cognitive_complexity(code)

        # 嵌套结构应该增加复杂度
        assert complexity > 0

    def test_calculate_halstead_volume(self):
        """测试Halstead体积计算"""
        code = '''
x = 1
y = 2
z = x + y
'''
        volume = self.metrics.calculate_halstead_volume(code)

        # 应该有正的体积
        assert volume > 0

    def test_calculate_maintainability_index(self):
        """测试可维护性指数计算"""
        # 简单代码应该有高可维护性
        mi = self.metrics.calculate_maintainability_index(100, 5, 50)
        assert mi > 50

        # 复杂代码应该有低可维护性
        mi_complex = self.metrics.calculate_maintainability_index(10000, 50, 500)
        assert mi_complex < mi

    def test_detect_code_smells(self):
        """测试代码异味检测"""
        # 创建一个有代码异味的代码
        code = '''
def very_long_function():
    """这是一个非常长的函数"""
    x = 1
    y = 2
    z = 3
    a = 4
    b = 5
    c = 6
    d = 7
    e = 8
    f = 9
    g = 10
    h = 11
    i = 12
    j = 13
    k = 14
    l = 15
    m = 16
    n = 17
    o = 18
    p = 19
    q = 20
    r = 21
    s = 22
    t = 23
    u = 24
    v = 25
    w = 26
    x2 = 27
    y2 = 28
    z2 = 29
    return x + y + z + a + b + c + d + e + f + g + h + i + j + k + l + m + n + o + p + q + r + s + t + u + v + w + x2 + y2 + z2
'''
        smells = self.metrics.detect_code_smells(code)

        # 应该检测到过长函数
        assert any(s["type"] == "long_method" for s in smells)

    def test_estimate_technical_debt(self):
        """测试技术债估算"""
        code_smells = [
            {"type": "long_method", "severity": "medium"},
            {"type": "magic_number", "severity": "low"},
        ]

        debt = self.metrics.estimate_technical_debt(code_smells, 15, 10)

        # 应该有正的技术债
        assert debt > 0

    def test_calculate_code_quality_score(self):
        """测试代码质量分数计算"""
        # 好的代码应该有高分
        good_metrics = {
            "cyclomatic_complexity": 3,
            "maintainability_index": 90,
            "duplicate_ratio": 0.05,
            "code_smells_count": 1
        }
        good_score = self.metrics.calculate_code_quality_score(good_metrics)
        assert good_score > 80

        # 差的代码应该有低分
        bad_metrics = {
            "cyclomatic_complexity": 30,
            "maintainability_index": 30,
            "duplicate_ratio": 0.5,
            "code_smells_count": 10
        }
        bad_score = self.metrics.calculate_code_quality_score(bad_metrics)
        assert bad_score < good_score

    def test_generate_quality_report(self):
        """测试生成质量报告"""
        code = '''
def hello():
    print("Hello, World!")

def add(a, b):
    return a + b
'''
        report = self.metrics.generate_quality_report("test.py", code)

        assert "file_path" in report
        assert "lines_of_code" in report
        assert "cyclomatic_complexity" in report
        assert "quality_score" in report
        assert report["file_path"] == "test.py"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])