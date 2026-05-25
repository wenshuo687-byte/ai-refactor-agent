"""
代码分析Agent - 负责扫描代码库、识别技术债、分析代码质量
"""

import ast
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from ..core.code_parser import CodeParser
from ..core.metrics import CodeMetrics


@dataclass
class CodeIssue:
    """代码问题数据类"""
    file_path: str
    line_number: int
    issue_type: str  # complexity, duplication, style, security, performance
    severity: str  # low, medium, high, critical
    description: str
    suggestion: str
    code_snippet: str


@dataclass
class AnalysisResult:
    """分析结果数据类"""
    project_path: str
    total_files: int
    total_lines: int
    issues: List[CodeIssue]
    metrics: Dict[str, Any]
    summary: Dict[str, int]


class CodeAnalyzerAgent:
    """
    代码分析Agent

    职责：
    1. 扫描项目代码库
    2. 识别技术债和代码问题
    3. 计算代码质量指标
    4. 生成分析报告
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.parser = CodeParser()
        self.metrics = CodeMetrics()
        self.issues: List[CodeIssue] = []

    def analyze_project(self, project_path: str) -> AnalysisResult:
        """
        分析整个项目

        Args:
            project_path: 项目根目录路径

        Returns:
            AnalysisResult: 分析结果
        """
        project_path = Path(project_path)
        if not project_path.exists():
            raise FileNotFoundError(f"项目路径不存在: {project_path}")

        # 收集所有代码文件
        code_files = self._collect_code_files(project_path)

        # 分析每个文件
        total_lines = 0
        for file_path in code_files:
            try:
                file_lines = self._analyze_file(file_path)
                total_lines += file_lines
            except Exception as e:
                print(f"分析文件失败 {file_path}: {e}")

        # 计算汇总指标
        metrics = self._calculate_metrics()
        summary = self._generate_summary()

        return AnalysisResult(
            project_path=str(project_path),
            total_files=len(code_files),
            total_lines=total_lines,
            issues=self.issues,
            metrics=metrics,
            summary=summary
        )

    def _collect_code_files(self, project_path: Path) -> List[Path]:
        """收集项目中的所有代码文件"""
        code_files = []
        file_types = self.config.get("scanner", {}).get("file_types", [".py"])
        ignore_dirs = set(self.config.get("scanner", {}).get("ignore_dirs", []))
        max_depth = self.config.get("scanner", {}).get("max_depth", 10)

        def _scan_directory(current_path: Path, depth: int):
            if depth > max_depth:
                return

            try:
                for item in current_path.iterdir():
                    if item.is_dir():
                        if item.name not in ignore_dirs:
                            _scan_directory(item, depth + 1)
                    elif item.is_file():
                        if item.suffix in file_types:
                            code_files.append(item)
            except PermissionError:
                pass

        _scan_directory(project_path, 0)
        return code_files

    def _analyze_file(self, file_path: Path) -> int:
        """
        分析单个文件

        Args:
            file_path: 文件路径

        Returns:
            int: 文件行数
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                lines = content.split("\n")

            # 解析AST
            try:
                tree = ast.parse(content)
            except SyntaxError as e:
                self.issues.append(CodeIssue(
                    file_path=str(file_path),
                    line_number=e.lineno or 0,
                    issue_type="syntax",
                    severity="critical",
                    description=f"语法错误: {e.msg}",
                    suggestion="修复语法错误",
                    code_snippet=""
                ))
                return len(lines)

            # 检测各种问题
            self._detect_complexity_issues(file_path, tree, lines)
            self._detect_style_issues(file_path, tree, lines)
            self._detect_duplication_issues(file_path, lines)

            return len(lines)

        except Exception as e:
            print(f"读取文件失败 {file_path}: {e}")
            return 0

    def _detect_complexity_issues(self, file_path: Path, tree: ast.AST, lines: List[str]):
        """检测复杂度问题"""
        complexity_threshold = self.config.get("quality_thresholds", {}).get("cyclomatic_complexity", 10)
        function_lines_threshold = self.config.get("quality_thresholds", {}).get("function_lines", 50)

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # 计算圈复杂度
                complexity = self._calculate_complexity(node)
                if complexity > complexity_threshold:
                    self.issues.append(CodeIssue(
                        file_path=str(file_path),
                        line_number=node.lineno,
                        issue_type="complexity",
                        severity="high" if complexity > complexity_threshold * 2 else "medium",
                        description=f"函数 '{node.name}' 圈复杂度过高: {complexity}",
                        suggestion="考虑拆分函数或减少条件分支",
                        code_snippet=self._get_code_snippet(lines, node.lineno)
                    ))

                # 检查函数长度
                if hasattr(node, "end_lineno") and node.end_lineno:
                    function_lines = node.end_lineno - node.lineno + 1
                    if function_lines > function_lines_threshold:
                        self.issues.append(CodeIssue(
                            file_path=str(file_path),
                            line_number=node.lineno,
                            issue_type="complexity",
                            severity="medium",
                            description=f"函数 '{node.name}' 过长: {function_lines}行",
                            suggestion="考虑将函数拆分为更小的函数",
                            code_snippet=self._get_code_snippet(lines, node.lineno)
                        ))

    def _calculate_complexity(self, node: ast.AST) -> int:
        """计算圈复杂度"""
        complexity = 1

        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
            elif isinstance(child, ast.Try):
                complexity += len(child.handlers)
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1

        return complexity

    def _detect_style_issues(self, file_path: Path, tree: ast.AST, lines: List[str]):
        """检测代码风格问题"""
        max_params = self.config.get("quality_thresholds", {}).get("max_parameters", 5)

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # 检查参数数量
                args = node.args
                total_params = len(args.args) + len(args.posonlyargs) + len(args.kwonlyargs)
                if args.vararg:
                    total_params += 1
                if args.kwarg:
                    total_params += 1

                if total_params > max_params:
                    self.issues.append(CodeIssue(
                        file_path=str(file_path),
                        line_number=node.lineno,
                        issue_type="style",
                        severity="medium",
                        description=f"函数 '{node.name}' 参数过多: {total_params}个",
                        suggestion="考虑使用数据类或配置对象封装参数",
                        code_snippet=self._get_code_snippet(lines, node.lineno)
                    ))

    def _detect_duplication_issues(self, file_path: Path, lines: List[str]):
        """检测重复代码"""
        duplicate_threshold = self.config.get("quality_thresholds", {}).get("duplicate_lines", 6)

        # 简单的重复代码检测（基于行匹配）
        for i in range(len(lines) - duplicate_threshold):
            chunk = "\n".join(lines[i:i + duplicate_threshold]).strip()
            if not chunk or len(chunk) < 20:
                continue

            # 向后搜索重复
            for j in range(i + duplicate_threshold, len(lines) - duplicate_threshold):
                other_chunk = "\n".join(lines[j:j + duplicate_threshold]).strip()
                if chunk == other_chunk:
                    self.issues.append(CodeIssue(
                        file_path=str(file_path),
                        line_number=i + 1,
                        issue_type="duplication",
                        severity="medium",
                        description=f"检测到重复代码块 (行 {i+1}-{i+duplicate_threshold} 和 {j+1}-{j+duplicate_threshold})",
                        suggestion="提取重复代码为独立函数",
                        code_snippet=self._get_code_snippet(lines, i + 1)
                    ))
                    break  # 只报告第一次出现

    def _get_code_snippet(self, lines: List[str], line_number: int, context: int = 3) -> str:
        """获取代码片段"""
        start = max(0, line_number - context - 1)
        end = min(len(lines), line_number + context)
        snippet_lines = lines[start:end]

        # 添加行号
        numbered_lines = []
        for i, line in enumerate(snippet_lines, start=start + 1):
            prefix = ">>> " if i == line_number else "    "
            numbered_lines.append(f"{prefix}{i}: {line}")

        return "\n".join(numbered_lines)

    def _calculate_metrics(self) -> Dict[str, Any]:
        """计算汇总指标"""
        if not self.issues:
            return {
                "total_issues": 0,
                "issues_by_type": {},
                "issues_by_severity": {},
                "quality_score": 100
            }

        # 按类型统计
        issues_by_type = {}
        for issue in self.issues:
            issues_by_type[issue.issue_type] = issues_by_type.get(issue.issue_type, 0) + 1

        # 按严重程度统计
        issues_by_severity = {}
        for issue in self.issues:
            issues_by_severity[issue.severity] = issues_by_severity.get(issue.severity, 0) + 1

        # 计算质量分数 (简单算法)
        severity_weights = {"low": 1, "medium": 3, "high": 5, "critical": 10}
        total_weight = sum(
            severity_weights.get(issue.severity, 1) for issue in self.issues
        )
        quality_score = max(0, 100 - total_weight)

        return {
            "total_issues": len(self.issues),
            "issues_by_type": issues_by_type,
            "issues_by_severity": issues_by_severity,
            "quality_score": quality_score
        }

    def _generate_summary(self) -> Dict[str, int]:
        """生成摘要统计"""
        return {
            "total_issues": len(self.issues),
            "critical_issues": sum(1 for i in self.issues if i.severity == "critical"),
            "high_issues": sum(1 for i in self.issues if i.severity == "high"),
            "medium_issues": sum(1 for i in self.issues if i.severity == "medium"),
            "low_issues": sum(1 for i in self.issues if i.severity == "low")
        }

    def get_issues_by_priority(self) -> List[CodeIssue]:
        """按优先级排序获取问题列表"""
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        return sorted(self.issues, key=lambda x: severity_order.get(x.severity, 4))

    def get_issues_by_file(self) -> Dict[str, List[CodeIssue]]:
        """按文件分组获取问题"""
        issues_by_file = {}
        for issue in self.issues:
            if issue.file_path not in issues_by_file:
                issues_by_file[issue.file_path] = []
            issues_by_file[issue.file_path].append(issue)
        return issues_by_file