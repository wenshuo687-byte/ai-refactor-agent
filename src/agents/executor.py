"""
执行验证Agent - 负责执行重构操作并验证结果
"""

import os
import shutil
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import json
import time


class ExecutionStatus(Enum):
    """执行状态"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class ExecutionResult:
    """执行结果数据类"""
    suggestion_id: str
    status: ExecutionStatus
    message: str
    changes_made: List[str]
    test_results: Optional[Dict[str, Any]]
    execution_time: float
    backup_path: Optional[str]


@dataclass
class ValidationReport:
    """验证报告数据类"""
    project_path: str
    total_suggestions: int
    executed: int
    successful: int
    failed: int
    skipped: int
    results: List[ExecutionResult]
    overall_improvement: Dict[str, Any]


class ExecutorAgent:
    """
    执行验证Agent

    职责：
    1. 执行重构操作
    2. 备份原始代码
    3. 运行测试验证
    4. 生成执行报告
    5. 回滚失败的操作
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.backup_dir = config.get("refactor", {}).get("backup_dir", ".refactor_backup")
        self.run_tests = config.get("refactor", {}).get("run_tests", True)
        self.test_command = config.get("refactor", {}).get("test_command", "pytest")
        self.results: List[ExecutionResult] = []

    def execute_refactor_plan(self, refactor_plan: Dict[str, Any]) -> ValidationReport:
        """
        执行重构计划

        Args:
            refactor_plan: 重构计划

        Returns:
            ValidationReport: 验证报告
        """
        project_path = refactor_plan.get("project_path", "")
        suggestions = refactor_plan.get("suggestions", [])
        execution_order = refactor_plan.get("execution_order", [])

        # 创建备份目录
        backup_path = self._create_backup(project_path)

        # 按顺序执行重构
        executed = 0
        successful = 0
        failed = 0
        skipped = 0

        for suggestion_id in execution_order:
            suggestion = self._find_suggestion(suggestions, suggestion_id)
            if not suggestion:
                continue

            # 执行单个重构
            result = self._execute_single_refactor(suggestion, project_path, backup_path)
            self.results.append(result)

            executed += 1
            if result.status == ExecutionStatus.SUCCESS:
                successful += 1
            elif result.status == ExecutionStatus.FAILED:
                failed += 1
            else:
                skipped += 1

        # 运行测试验证
        test_results = None
        if self.run_tests and successful > 0:
            test_results = self._run_tests(project_path)

        # 计算整体改进
        overall_improvement = self._calculate_overall_improvement()

        return ValidationReport(
            project_path=project_path,
            total_suggestions=len(suggestions),
            executed=executed,
            successful=successful,
            failed=failed,
            skipped=skipped,
            results=self.results,
            overall_improvement=overall_improvement
        )

    def _create_backup(self, project_path: str) -> str:
        """创建项目备份"""
        project_path = Path(project_path)
        backup_dir = Path(self.backup_dir)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        backup_path = backup_dir / f"backup_{timestamp}"

        try:
            # 创建备份目录
            backup_path.mkdir(parents=True, exist_ok=True)

            # 复制项目文件（排除备份目录本身）
            for item in project_path.iterdir():
                if item.name == self.backup_dir:
                    continue

                if item.is_dir():
                    shutil.copytree(item, backup_path / item.name, dirs_exist_ok=True)
                else:
                    shutil.copy2(item, backup_path / item.name)

            print(f"备份已创建: {backup_path}")
            return str(backup_path)

        except Exception as e:
            print(f"创建备份失败: {e}")
            return ""

    def _execute_single_refactor(self, suggestion: Dict[str, Any], project_path: str, backup_path: str) -> ExecutionResult:
        """执行单个重构操作"""
        suggestion_id = suggestion.get("id", "")
        file_path = suggestion.get("file_path", "")
        refactor_type = suggestion.get("refactor_type", "")
        line_number = suggestion.get("line_number", 0)

        start_time = time.time()
        changes_made = []

        try:
            # 读取原文件
            full_path = Path(project_path) / file_path
            if not full_path.exists():
                return ExecutionResult(
                    suggestion_id=suggestion_id,
                    status=ExecutionStatus.SKIPPED,
                    message=f"文件不存在: {file_path}",
                    changes_made=[],
                    test_results=None,
                    execution_time=time.time() - start_time,
                    backup_path=backup_path
                )

            with open(full_path, "r", encoding="utf-8") as f:
                original_content = f.read()

            # 根据重构类型执行不同的操作
            if refactor_type == "extract_method":
                new_content = self._apply_extract_method(original_content, suggestion)
            elif refactor_type == "remove_duplication":
                new_content = self._apply_remove_duplication(original_content, suggestion)
            elif refactor_type == "introduce_parameter_object":
                new_content = self._apply_parameter_object(original_content, suggestion)
            else:
                # 对于其他类型，记录建议但不自动执行
                return ExecutionResult(
                    suggestion_id=suggestion_id,
                    status=ExecutionStatus.SKIPPED,
                    message=f"重构类型 {refactor_type} 需要手动执行",
                    changes_made=[],
                    test_results=None,
                    execution_time=time.time() - start_time,
                    backup_path=backup_path
                )

            # 写入新内容
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(new_content)

            changes_made.append(f"修改文件: {file_path}")
            changes_made.append(f"重构类型: {refactor_type}")

            return ExecutionResult(
                suggestion_id=suggestion_id,
                status=ExecutionStatus.SUCCESS,
                message="重构执行成功",
                changes_made=changes_made,
                test_results=None,
                execution_time=time.time() - start_time,
                backup_path=backup_path
            )

        except Exception as e:
            return ExecutionResult(
                suggestion_id=suggestion_id,
                status=ExecutionStatus.FAILED,
                message=f"执行失败: {str(e)}",
                changes_made=changes_made,
                test_results=None,
                execution_time=time.time() - start_time,
                backup_path=backup_path
            )

    def _apply_extract_method(self, content: str, suggestion: Dict[str, Any]) -> str:
        """应用提取方法重构"""
        # 这里是一个简化的实现
        # 实际应用中需要使用AST进行更精确的代码转换
        lines = content.split("\n")
        line_number = suggestion.get("line_number", 1) - 1

        # 在指定行后添加新方法
        new_method = '''
def extracted_method():
    """
    提取的方法
    """
    # TODO: 实现具体逻辑
    pass

'''

        # 插入新方法
        if line_number < len(lines):
            lines.insert(line_number + 1, new_method)

        return "\n".join(lines)

    def _apply_remove_duplication(self, content: str, suggestion: Dict[str, Any]) -> str:
        """应用消除重复代码重构"""
        # 简化实现：添加注释标记重复代码
        lines = content.split("\n")
        line_number = suggestion.get("line_number", 1) - 1

        if line_number < len(lines):
            lines.insert(line_number, "# TODO: 重复代码 - 需要提取为公共函数")

        return "\n".join(lines)

    def _apply_parameter_object(self, content: str, suggestion: Dict[str, Any]) -> str:
        """应用引入参数对象重构"""
        # 简化实现：添加参数对象定义
        lines = content.split("\n")
        line_number = suggestion.get("line_number", 1) - 1

        param_object = '''
from dataclasses import dataclass

@dataclass
class FunctionParams:
    """函数参数封装"""
    # TODO: 添加参数定义
    pass

'''

        if line_number < len(lines):
            lines.insert(0, param_object)

        return "\n".join(lines)

    def _run_tests(self, project_path: str) -> Dict[str, Any]:
        """运行测试验证"""
        try:
            # 切换到项目目录
            original_dir = os.getcwd()
            os.chdir(project_path)

            # 运行测试命令
            result = subprocess.run(
                self.test_command.split(),
                capture_output=True,
                text=True,
                timeout=300  # 5分钟超时
            )

            os.chdir(original_dir)

            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode
            }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "stdout": "",
                "stderr": "测试执行超时",
                "return_code": -1
            }
        except Exception as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "return_code": -1
            }

    def _find_suggestion(self, suggestions: List[Dict[str, Any]], suggestion_id: str) -> Optional[Dict[str, Any]]:
        """查找指定ID的建议"""
        for suggestion in suggestions:
            if suggestion.get("id") == suggestion_id:
                return suggestion
        return None

    def _calculate_overall_improvement(self) -> Dict[str, Any]:
        """计算整体改进情况"""
        successful = sum(1 for r in self.results if r.status == ExecutionStatus.SUCCESS)
        failed = sum(1 for r in self.results if r.status == ExecutionStatus.FAILED)

        return {
            "total_executed": len(self.results),
            "successful": successful,
            "failed": failed,
            "success_rate": successful / len(self.results) if self.results else 0,
            "total_changes": sum(len(r.changes_made) for r in self.results)
        }

    def rollback_changes(self, backup_path: str, project_path: str) -> bool:
        """回滚所有更改"""
        try:
            backup_path = Path(backup_path)
            project_path = Path(project_path)

            if not backup_path.exists():
                print(f"备份目录不存在: {backup_path}")
                return False

            # 删除当前项目文件（排除备份目录）
            for item in project_path.iterdir():
                if item.name == self.backup_dir:
                    continue

                if item.is_dir():
                    shutil.rmtree(item)
                else:
                    item.unlink()

            # 从备份恢复
            for item in backup_path.iterdir():
                if item.is_dir():
                    shutil.copytree(item, project_path / item.name)
                else:
                    shutil.copy2(item, project_path / item.name)

            print(f"已回滚到备份: {backup_path}")
            return True

        except Exception as e:
            print(f"回滚失败: {e}")
            return False

    def generate_report(self, validation_report: ValidationReport) -> str:
        """生成执行报告"""
        report_lines = []
        report_lines.append("# 重构执行报告\n")
        report_lines.append(f"## 项目路径: {validation_report.project_path}\n")
        report_lines.append("## 执行统计\n")
        report_lines.append(f"- 总建议数: {validation_report.total_suggestions}")
        report_lines.append(f"- 已执行: {validation_report.executed}")
        report_lines.append(f"- 成功: {validation_report.successful}")
        report_lines.append(f"- 失败: {validation_report.failed}")
        report_lines.append(f"- 跳过: {validation_report.skipped}")
        report_lines.append(f"- 成功率: {validation_report.overall_improvement.get('success_rate', 0):.1%}\n")

        report_lines.append("## 执行详情\n")
        for result in validation_report.results:
            report_lines.append(f"### 建议 {result.suggestion_id}")
            report_lines.append(f"- 状态: {result.status.value}")
            report_lines.append(f"- 消息: {result.message}")
            report_lines.append(f"- 耗时: {result.execution_time:.2f}秒")
            if result.changes_made:
                report_lines.append("- 变更:")
                for change in result.changes_made:
                    report_lines.append(f"  - {change}")
            report_lines.append("")

        if validation_report.overall_improvement:
            report_lines.append("## 整体改进\n")
            improvement = validation_report.overall_improvement
            report_lines.append(f"- 总变更数: {improvement.get('total_changes', 0)}")
            report_lines.append(f"- 成功率: {improvement.get('success_rate', 0):.1%}")

        return "\n".join(report_lines)