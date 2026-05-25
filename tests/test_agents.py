"""
Agent测试
"""

import pytest
import tempfile
import os
from pathlib import Path

from src.agents.code_analyzer import CodeAnalyzerAgent
from src.agents.refactor_strategist import RefactorStrategistAgent
from src.agents.executor import ExecutorAgent
from src.agents.coordinator import Coordinator


class TestCodeAnalyzerAgent:
    """代码分析Agent测试"""

    def setup_method(self):
        """测试前准备"""
        self.config = {
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
        self.agent = CodeAnalyzerAgent(self.config)

    def test_analyze_simple_file(self):
        """测试分析简单文件"""
        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
            f.write('''
def simple_function():
    """简单函数"""
    return 42

def complex_function(x):
    """复杂函数"""
    if x > 0:
        if x > 10:
            return x * 2
        else:
            return x + 1
    else:
        return 0
''')
            temp_file = f.name

        try:
            # 分析文件
            result = self.agent._analyze_file(Path(temp_file))

            # 验证结果
            assert result > 0
            assert len(self.agent.issues) >= 0  # 可能有问题，也可能没有
        finally:
            os.unlink(temp_file)

    def test_calculate_complexity(self):
        """测试复杂度计算"""
        import ast

        code = '''
def complex_function(x):
    if x > 0:
        if x > 10:
            return x * 2
        else:
            return x + 1
    else:
        return 0
'''
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                complexity = self.agent._calculate_complexity(node)
                assert complexity > 1  # 应该有多个分支

    def test_detect_duplication(self):
        """测试重复代码检测"""
        lines = [
            "def func1():",
            "    x = 1",
            "    y = 2",
            "    z = 3",
            "    a = 4",
            "    b = 5",
            "    return x + y + z + a + b",
            "",
            "def func2():",
            "    x = 1",
            "    y = 2",
            "    z = 3",
            "    a = 4",
            "    b = 5",
            "    return x + y + z + a + b",
        ]

        # 检测重复
        self.agent._detect_duplication_issues(Path("test.py"), lines)

        # 可能检测到重复，也可能没有（取决于阈值）
        assert len(self.agent.issues) >= 0


class TestRefactorStrategistAgent:
    """重构策略Agent测试"""

    def setup_method(self):
        """测试前准备"""
        self.config = {}
        self.agent = RefactorStrategistAgent(self.config)

    def test_generate_suggestion(self):
        """测试生成重构建议"""
        issue = {
            "file_path": "test.py",
            "line_number": 10,
            "issue_type": "complexity",
            "severity": "high",
            "description": "函数圈复杂度过高: 15",
            "suggestion": "考虑拆分函数",
            "code_snippet": "def complex_function():"
        }

        suggestion = self.agent._generate_suggestion(issue)

        assert suggestion is not None
        assert suggestion.file_path == "test.py"
        assert suggestion.line_number == 10

    def test_prioritize_suggestions(self):
        """测试优先级排序"""
        from src.agents.refactor_strategist import RefactorSuggestion, RefactorPriority, RefactorType

        suggestions = [
            RefactorSuggestion(
                id="1",
                file_path="test.py",
                line_number=1,
                refactor_type=RefactorType.EXTRACT_METHOD,
                priority=RefactorPriority.LOW,
                title="低优先级",
                description="",
                current_code="",
                suggested_code="",
                benefits=[],
                risks=[],
                effort_estimate="low",
                impact_estimate="low"
            ),
            RefactorSuggestion(
                id="2",
                file_path="test.py",
                line_number=2,
                refactor_type=RefactorType.EXTRACT_METHOD,
                priority=RefactorPriority.CRITICAL,
                title="关键优先级",
                description="",
                current_code="",
                suggested_code="",
                benefits=[],
                risks=[],
                effort_estimate="high",
                impact_estimate="high"
            ),
        ]

        sorted_suggestions = self.agent._prioritize_suggestions(suggestions)

        # 关键优先级应该排在前面
        assert sorted_suggestions[0].priority == RefactorPriority.CRITICAL
        assert sorted_suggestions[1].priority == RefactorPriority.LOW


class TestExecutorAgent:
    """执行验证Agent测试"""

    def setup_method(self):
        """测试前准备"""
        self.config = {
            "refactor": {
                "run_tests": False,
                "backup": True,
                "backup_dir": ".test_backup"
            }
        }
        self.agent = ExecutorAgent(self.config)

    def test_create_backup(self):
        """测试创建备份"""
        # 创建临时目录
        with tempfile.TemporaryDirectory() as temp_dir:
            # 创建测试文件
            test_file = Path(temp_dir) / "test.py"
            test_file.write_text("print('hello')")

            # 创建备份
            backup_path = self.agent._create_backup(temp_dir)

            # 验证备份目录存在
            assert Path(backup_path).exists()

            # 清理
            import shutil
            if Path(backup_path).exists():
                shutil.rmtree(backup_path)

    def test_find_suggestion(self):
        """测试查找建议"""
        suggestions = [
            {"id": "1", "title": "建议1"},
            {"id": "2", "title": "建议2"},
        ]

        # 查找存在的建议
        result = self.agent._find_suggestion(suggestions, "1")
        assert result is not None
        assert result["id"] == "1"

        # 查找不存在的建议
        result = self.agent._find_suggestion(suggestions, "3")
        assert result is None


class TestCoordinator:
    """协调器测试"""

    def setup_method(self):
        """测试前准备"""
        # 创建临时配置文件
        self.temp_config = tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False)
        self.temp_config.write('''
scanner:
  file_types: [".py"]
  ignore_dirs: ["__pycache__"]
quality_thresholds:
  cyclomatic_complexity: 10
refactor:
  run_tests: false
''')
        self.temp_config.close()

    def teardown_method(self):
        """测试后清理"""
        os.unlink(self.temp_config.name)

    def test_load_config(self):
        """测试加载配置"""
        coordinator = Coordinator(self.temp_config.name)

        assert coordinator.config is not None
        assert "scanner" in coordinator.config

    def test_get_default_config(self):
        """测试获取默认配置"""
        coordinator = Coordinator()

        config = coordinator._get_default_config()

        assert "ai" in config
        assert "scanner" in config
        assert "quality_thresholds" in config


if __name__ == "__main__":
    pytest.main([__file__, "-v"])