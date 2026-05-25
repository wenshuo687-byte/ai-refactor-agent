"""
代码解析器 - 负责解析代码文件，提取结构信息
"""

import ast
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class FunctionInfo:
    """函数信息"""
    name: str
    line_number: int
    end_line: int
    args: List[str]
    decorators: List[str]
    is_async: bool
    complexity: int
    lines_of_code: int


@dataclass
class ClassInfo:
    """类信息"""
    name: str
    line_number: int
    end_line: int
    methods: List[FunctionInfo]
    base_classes: List[str]
    decorators: List[str]
    lines_of_code: int


@dataclass
class ImportInfo:
    """导入信息"""
    module: str
    names: List[str]
    line_number: int
    is_from_import: bool


@dataclass
class CodeStructure:
    """代码结构信息"""
    file_path: str
    functions: List[FunctionInfo]
    classes: List[ClassInfo]
    imports: List[ImportInfo]
    total_lines: int
    code_lines: int
    comment_lines: int
    blank_lines: int


class CodeParser:
    """
    代码解析器

    职责：
    1. 解析Python代码文件
    2. 提取函数、类、导入等结构信息
    3. 计算代码行数统计
    4. 分析代码复杂度
    """

    def __init__(self):
        pass

    def parse_file(self, file_path: str) -> Optional[CodeStructure]:
        """
        解析代码文件

        Args:
            file_path: 文件路径

        Returns:
            Optional[CodeStructure]: 代码结构信息
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            return self.parse_content(content, file_path)

        except Exception as e:
            print(f"解析文件失败 {file_path}: {e}")
            return None

    def parse_content(self, content: str, file_path: str = "") -> CodeStructure:
        """
        解析代码内容

        Args:
            content: 代码内容
            file_path: 文件路径（可选）

        Returns:
            CodeStructure: 代码结构信息
        """
        lines = content.split("\n")

        # 解析AST
        try:
            tree = ast.parse(content)
        except SyntaxError:
            # 如果语法错误，返回基本信息
            return CodeStructure(
                file_path=file_path,
                functions=[],
                classes=[],
                imports=[],
                total_lines=len(lines),
                code_lines=0,
                comment_lines=0,
                blank_lines=0
            )

        # 提取结构信息
        functions = self._extract_functions(tree)
        classes = self._extract_classes(tree)
        imports = self._extract_imports(tree)

        # 统计行数
        code_lines, comment_lines, blank_lines = self._count_lines(lines)

        return CodeStructure(
            file_path=file_path,
            functions=functions,
            classes=classes,
            imports=imports,
            total_lines=len(lines),
            code_lines=code_lines,
            comment_lines=comment_lines,
            blank_lines=blank_lines
        )

    def _extract_functions(self, tree: ast.AST) -> List[FunctionInfo]:
        """提取函数信息"""
        functions = []

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # 提取参数
                args = []
                for arg in node.args.args:
                    args.append(arg.arg)

                # 提取装饰器
                decorators = []
                for decorator in node.decorator_list:
                    if isinstance(decorator, ast.Name):
                        decorators.append(decorator.id)
                    elif isinstance(decorator, ast.Attribute):
                        decorators.append(f"{decorator.value.id}.{decorator.attr}" if hasattr(decorator.value, 'id') else decorator.attr)

                # 计算复杂度
                complexity = self._calculate_complexity(node)

                # 计算行数
                end_line = getattr(node, "end_lineno", node.lineno)
                lines_of_code = end_line - node.lineno + 1

                functions.append(FunctionInfo(
                    name=node.name,
                    line_number=node.lineno,
                    end_line=end_line,
                    args=args,
                    decorators=decorators,
                    is_async=isinstance(node, ast.AsyncFunctionDef),
                    complexity=complexity,
                    lines_of_code=lines_of_code
                ))

        return functions

    def _extract_classes(self, tree: ast.AST) -> List[ClassInfo]:
        """提取类信息"""
        classes = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # 提取基类
                base_classes = []
                for base in node.bases:
                    if isinstance(base, ast.Name):
                        base_classes.append(base.id)
                    elif isinstance(base, ast.Attribute):
                        base_classes.append(f"{base.value.id}.{base.attr}" if hasattr(base.value, 'id') else base.attr)

                # 提取装饰器
                decorators = []
                for decorator in node.decorator_list:
                    if isinstance(decorator, ast.Name):
                        decorators.append(decorator.id)

                # 提取方法
                methods = []
                for child in node.body:
                    if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        args = [arg.arg for arg in child.args.args]
                        complexity = self._calculate_complexity(child)
                        end_line = getattr(child, "end_lineno", child.lineno)

                        methods.append(FunctionInfo(
                            name=child.name,
                            line_number=child.lineno,
                            end_line=end_line,
                            args=args,
                            decorators=[],
                            is_async=isinstance(child, ast.AsyncFunctionDef),
                            complexity=complexity,
                            lines_of_code=end_line - child.lineno + 1
                        ))

                # 计算类的总行数
                end_line = getattr(node, "end_lineno", node.lineno)
                lines_of_code = end_line - node.lineno + 1

                classes.append(ClassInfo(
                    name=node.name,
                    line_number=node.lineno,
                    end_line=end_line,
                    methods=methods,
                    base_classes=base_classes,
                    decorators=decorators,
                    lines_of_code=lines_of_code
                ))

        return classes

    def _extract_imports(self, tree: ast.AST) -> List[ImportInfo]:
        """提取导入信息"""
        imports = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
                imports.append(ImportInfo(
                    module="",
                    names=names,
                    line_number=node.lineno,
                    is_from_import=False
                ))
            elif isinstance(node, ast.ImportFrom):
                names = [alias.name for alias in node.names]
                imports.append(ImportInfo(
                    module=node.module or "",
                    names=names,
                    line_number=node.lineno,
                    is_from_import=True
                ))

        return imports

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

    def _count_lines(self, lines: List[str]) -> tuple:
        """统计代码行数、注释行数、空行数"""
        code_lines = 0
        comment_lines = 0
        blank_lines = 0

        for line in lines:
            stripped = line.strip()
            if not stripped:
                blank_lines += 1
            elif stripped.startswith("#"):
                comment_lines += 1
            else:
                code_lines += 1

        return code_lines, comment_lines, blank_lines

    def get_function_at_line(self, structure: CodeStructure, line_number: int) -> Optional[FunctionInfo]:
        """获取指定行所在的函数"""
        for func in structure.functions:
            if func.line_number <= line_number <= func.end_line:
                return func
        return None

    def get_class_at_line(self, structure: CodeStructure, line_number: int) -> Optional[ClassInfo]:
        """获取指定行所在的类"""
        for cls in structure.classes:
            if cls.line_number <= line_number <= cls.end_line:
                return cls
        return None

    def get_code_metrics(self, structure: CodeStructure) -> Dict[str, Any]:
        """获取代码质量指标"""
        # 计算平均函数复杂度
        if structure.functions:
            avg_complexity = sum(f.complexity for f in structure.functions) / len(structure.functions)
            max_complexity = max(f.complexity for f in structure.functions)
        else:
            avg_complexity = 0
            max_complexity = 0

        # 计算平均函数长度
        if structure.functions:
            avg_function_length = sum(f.lines_of_code for f in structure.functions) / len(structure.functions)
            max_function_length = max(f.lines_of_code for f in structure.functions)
        else:
            avg_function_length = 0
            max_function_length = 0

        # 计算代码密度
        code_density = structure.code_lines / structure.total_lines if structure.total_lines > 0 else 0

        return {
            "total_functions": len(structure.functions),
            "total_classes": len(structure.classes),
            "total_imports": len(structure.imports),
            "avg_complexity": round(avg_complexity, 2),
            "max_complexity": max_complexity,
            "avg_function_length": round(avg_function_length, 2),
            "max_function_length": max_function_length,
            "code_density": round(code_density, 2),
            "total_lines": structure.total_lines,
            "code_lines": structure.code_lines,
            "comment_lines": structure.comment_lines,
            "blank_lines": structure.blank_lines
        }