"""
主协调器 - 负责协调多个Agent的工作
"""

from typing import Dict, Any, Optional
from pathlib import Path
import yaml
import json
from datetime import datetime

from .code_analyzer import CodeAnalyzerAgent, AnalysisResult
from .refactor_strategist import RefactorStrategistAgent, RefactorPlan
from .executor import ExecutorAgent, ValidationReport


class Coordinator:
    """
    主协调器

    职责：
    1. 协调代码分析、重构策略、执行验证三个Agent
    2. 管理配置和资源
    3. 生成综合报告
    4. 处理异常和回滚
    """

    def __init__(self, config_path: str = "config/config.yaml"):
        """
        初始化协调器

        Args:
            config_path: 配置文件路径
        """
        self.config = self._load_config(config_path)

        # 初始化各个Agent
        self.code_analyzer = CodeAnalyzerAgent(self.config)
        self.refactor_strategist = RefactorStrategistAgent(self.config)
        self.executor = ExecutorAgent(self.config)

        # 存储结果
        self.analysis_result: Optional[AnalysisResult] = None
        self.refactor_plan: Optional[RefactorPlan] = None
        self.validation_report: Optional[ValidationReport] = None

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """加载配置文件"""
        config_path = Path(config_path)
        if not config_path.exists():
            print(f"配置文件不存在: {config_path}，使用默认配置")
            return self._get_default_config()

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
            return config if config else self._get_default_config()
        except Exception as e:
            print(f"加载配置文件失败: {e}，使用默认配置")
            return self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "ai": {
                "provider": "anthropic",
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 4096,
                "temperature": 0.3
            },
            "scanner": {
                "file_types": [".py"],
                "ignore_dirs": ["node_modules", "__pycache__", ".git"],
                "max_depth": 10
            },
            "quality_thresholds": {
                "cyclomatic_complexity": 10,
                "function_lines": 50,
                "file_lines": 500,
                "duplicate_lines": 6,
                "max_parameters": 5
            },
            "refactor": {
                "run_tests": True,
                "test_command": "pytest",
                "backup": True,
                "backup_dir": ".refactor_backup"
            }
        }

    def run_full_analysis(self, project_path: str) -> Dict[str, Any]:
        """
        运行完整的分析和重构流程

        Args:
            project_path: 项目路径

        Returns:
            Dict: 包含所有结果的字典
        """
        print(f"开始分析项目: {project_path}")
        print("=" * 60)

        # 第一步：代码分析
        print("\n[1/3] 代码分析Agent - 扫描代码库...")
        try:
            self.analysis_result = self.code_analyzer.analyze_project(project_path)
            print(f"[OK] 分析完成:")
            print(f"  - 扫描文件数: {self.analysis_result.total_files}")
            print(f"  - 代码总行数: {self.analysis_result.total_lines}")
            print(f"  - 发现问题数: {len(self.analysis_result.issues)}")
            print(f"  - 质量分数: {self.analysis_result.metrics.get('quality_score', 0)}")
        except Exception as e:
            print(f"[ERROR] 代码分析失败: {e}")
            return {"error": str(e)}

        # 第二步：生成重构计划
        print("\n[2/3] 重构策略Agent - 生成重构方案...")
        try:
            analysis_dict = {
                "project_path": self.analysis_result.project_path,
                "issues": [
                    {
                        "file_path": issue.file_path,
                        "line_number": issue.line_number,
                        "issue_type": issue.issue_type,
                        "severity": issue.severity,
                        "description": issue.description,
                        "suggestion": issue.suggestion,
                        "code_snippet": issue.code_snippet
                    }
                    for issue in self.analysis_result.issues
                ],
                "metrics": self.analysis_result.metrics
            }

            self.refactor_plan = self.refactor_strategist.generate_refactor_plan(analysis_dict)
            print(f"[OK] 重构计划生成完成:")
            print(f"  - 重构建议数: {len(self.refactor_plan.suggestions)}")
            print(f"  - 总工作量: {self.refactor_plan.total_effort}")
            print(f"  - 预期质量提升: {self.refactor_plan.expected_improvement.get('improvement', 0)}分")
        except Exception as e:
            print(f"[ERROR] 生成重构计划失败: {e}")
            return {"error": str(e)}

        # 第三步：执行重构（可选）
        print("\n[3/3] 执行验证Agent - 执行重构...")
        try:
            plan_dict = {
                "project_path": self.refactor_plan.project_path,
                "suggestions": [
                    {
                        "id": s.id,
                        "file_path": s.file_path,
                        "line_number": s.line_number,
                        "refactor_type": s.refactor_type.value,
                        "priority": s.priority.value,
                        "title": s.title,
                        "description": s.description
                    }
                    for s in self.refactor_plan.suggestions
                ],
                "execution_order": self.refactor_plan.execution_order
            }

            self.validation_report = self.executor.execute_refactor_plan(plan_dict)
            print(f"[OK] 执行完成:")
            print(f"  - 已执行: {self.validation_report.executed}")
            print(f"  - 成功: {self.validation_report.successful}")
            print(f"  - 失败: {self.validation_report.failed}")
            print(f"  - 跳过: {self.validation_report.skipped}")
        except Exception as e:
            print(f"[ERROR] 执行重构失败: {e}")
            return {"error": str(e)}

        # 生成综合报告
        print("\n" + "=" * 60)
        print("分析完成！正在生成报告...")

        report = self._generate_comprehensive_report()

        # 保存报告
        self._save_report(report, project_path)

        print("\n报告已保存到: reports/refactor_report.md")

        return report

    def _generate_comprehensive_report(self) -> Dict[str, Any]:
        """生成综合报告"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "project_path": self.analysis_result.project_path if self.analysis_result else "",
            "analysis": {
                "total_files": self.analysis_result.total_files if self.analysis_result else 0,
                "total_lines": self.analysis_result.total_lines if self.analysis_result else 0,
                "issues_count": len(self.analysis_result.issues) if self.analysis_result else 0,
                "quality_score": self.analysis_result.metrics.get("quality_score", 0) if self.analysis_result else 0,
                "issues_by_type": self.analysis_result.metrics.get("issues_by_type", {}) if self.analysis_result else {},
                "issues_by_severity": self.analysis_result.metrics.get("issues_by_severity", {}) if self.analysis_result else {}
            },
            "refactor_plan": {
                "total_suggestions": len(self.refactor_plan.suggestions) if self.refactor_plan else 0,
                "total_effort": self.refactor_plan.total_effort if self.refactor_plan else "unknown",
                "expected_improvement": self.refactor_plan.expected_improvement if self.refactor_plan else {},
                "suggestions": [
                    {
                        "id": s.id,
                        "title": s.title,
                        "priority": s.priority.value,
                        "file_path": s.file_path,
                        "line_number": s.line_number,
                        "benefits": s.benefits,
                        "risks": s.risks
                    }
                    for s in (self.refactor_plan.suggestions if self.refactor_plan else [])
                ]
            },
            "execution": {
                "total_executed": self.validation_report.executed if self.validation_report else 0,
                "successful": self.validation_report.successful if self.validation_report else 0,
                "failed": self.validation_report.failed if self.validation_report else 0,
                "skipped": self.validation_report.skipped if self.validation_report else 0,
                "success_rate": self.validation_report.overall_improvement.get("success_rate", 0) if self.validation_report else 0
            }
        }

        return report

    def _save_report(self, report: Dict[str, Any], project_path: str):
        """保存报告到文件"""
        report_dir = Path(project_path) / "reports"
        report_dir.mkdir(exist_ok=True)

        # 保存Markdown报告
        md_report = self._generate_markdown_report(report)
        md_path = report_dir / "refactor_report.md"
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(md_report)

        # 保存JSON报告
        json_path = report_dir / "refactor_report.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

    def _generate_markdown_report(self, report: Dict[str, Any]) -> str:
        """生成Markdown格式的报告"""
        lines = []
        lines.append("# AI智能重构Agent - 分析报告\n")
        lines.append(f"**生成时间**: {report.get('timestamp', '')}\n")
        lines.append(f"**项目路径**: {report.get('project_path', '')}\n")

        # 分析结果
        lines.append("## 1. 代码分析结果\n")
        analysis = report.get("analysis", {})
        lines.append(f"- **扫描文件数**: {analysis.get('total_files', 0)}")
        lines.append(f"- **代码总行数**: {analysis.get('total_lines', 0)}")
        lines.append(f"- **发现问题数**: {analysis.get('issues_count', 0)}")
        lines.append(f"- **质量分数**: {analysis.get('quality_score', 0)}/100\n")

        # 问题分布
        lines.append("### 问题类型分布\n")
        issues_by_type = analysis.get("issues_by_type", {})
        for issue_type, count in issues_by_type.items():
            lines.append(f"- {issue_type}: {count}")

        lines.append("\n### 问题严重程度分布\n")
        issues_by_severity = analysis.get("issues_by_severity", {})
        for severity, count in issues_by_severity.items():
            lines.append(f"- {severity}: {count}")

        # 重构计划
        lines.append("\n## 2. 重构计划\n")
        plan = report.get("refactor_plan", {})
        lines.append(f"- **重构建议数**: {plan.get('total_suggestions', 0)}")
        lines.append(f"- **总工作量**: {plan.get('total_effort', 'unknown')}")

        improvement = plan.get("expected_improvement", {})
        lines.append(f"- **预期质量提升**: {improvement.get('improvement', 0)}分")
        lines.append(f"- **预期质量分数**: {improvement.get('expected_score', 0)}/100\n")

        # 重构建议详情
        lines.append("### 重构建议详情\n")
        suggestions = plan.get("suggestions", [])
        for i, suggestion in enumerate(suggestions, 1):
            lines.append(f"#### {i}. {suggestion.get('title', '')}\n")
            lines.append(f"- **优先级**: {suggestion.get('priority', '')}")
            lines.append(f"- **文件**: {suggestion.get('file_path', '')}")
            lines.append(f"- **行号**: {suggestion.get('line_number', 0)}")
            lines.append(f"- **收益**: {', '.join(suggestion.get('benefits', []))}")
            lines.append(f"- **风险**: {', '.join(suggestion.get('risks', []))}\n")

        # 执行结果
        lines.append("## 3. 执行结果\n")
        execution = report.get("execution", {})
        lines.append(f"- **已执行**: {execution.get('total_executed', 0)}")
        lines.append(f"- **成功**: {execution.get('successful', 0)}")
        lines.append(f"- **失败**: {execution.get('failed', 0)}")
        lines.append(f"- **跳过**: {execution.get('skipped', 0)}")
        lines.append(f"- **成功率**: {execution.get('success_rate', 0):.1%}\n")

        # 总结
        lines.append("## 4. 总结\n")
        lines.append("本次分析使用多Agent协作的方式，完成了以下工作：")
        lines.append("1. **代码分析Agent**：扫描代码库，识别技术债和代码问题")
        lines.append("2. **重构策略Agent**：基于分析结果生成重构方案")
        lines.append("3. **执行验证Agent**：执行重构操作并验证结果\n")
        lines.append("通过这种长链推理和多Agent协作的方式，实现了从问题发现到解决方案的完整闭环。")

        return "\n".join(lines)

    def get_analysis_summary(self) -> Dict[str, Any]:
        """获取分析摘要"""
        if not self.analysis_result:
            return {}

        return {
            "total_files": self.analysis_result.total_files,
            "total_lines": self.analysis_result.total_lines,
            "issues_count": len(self.analysis_result.issues),
            "quality_score": self.analysis_result.metrics.get("quality_score", 0)
        }

    def get_refactor_plan_summary(self) -> Dict[str, Any]:
        """获取重构计划摘要"""
        if not self.refactor_plan:
            return {}

        return {
            "total_suggestions": len(self.refactor_plan.suggestions),
            "total_effort": self.refactor_plan.total_effort,
            "expected_improvement": self.refactor_plan.expected_improvement
        }

    def get_execution_summary(self) -> Dict[str, Any]:
        """获取执行摘要"""
        if not self.validation_report:
            return {}

        return {
            "executed": self.validation_report.executed,
            "successful": self.validation_report.successful,
            "failed": self.validation_report.failed,
            "skipped": self.validation_report.skipped,
            "success_rate": self.validation_report.overall_improvement.get("success_rate", 0)
        }