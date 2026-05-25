"""
重构策略Agent - 负责基于代码分析结果生成重构方案
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import json


class RefactorPriority(Enum):
    """重构优先级"""
    CRITICAL = "critical"  # 必须立即修复
    HIGH = "high"         # 高优先级
    MEDIUM = "medium"     # 中优先级
    LOW = "low"          # 低优先级


class RefactorType(Enum):
    """重构类型"""
    EXTRACT_METHOD = "extract_method"      # 提取方法
    EXTRACT_CLASS = "extract_class"        # 提取类
    RENAME = "rename"                      # 重命名
    INLINE = "inline"                      # 内联
    MOVE_METHOD = "move_method"            # 移动方法
    REPLACE_CONDITIONAL = "replace_conditional"  # 替换条件表达式
    INTRODUCE_PARAMETER_OBJECT = "introduce_parameter_object"  # 引入参数对象
    REMOVE_DUPLICATION = "remove_duplication"  # 消除重复


@dataclass
class RefactorSuggestion:
    """重构建议数据类"""
    id: str
    file_path: str
    line_number: int
    refactor_type: RefactorType
    priority: RefactorPriority
    title: str
    description: str
    current_code: str
    suggested_code: str
    benefits: List[str]
    risks: List[str]
    effort_estimate: str  # low, medium, high
    impact_estimate: str  # low, medium, high


@dataclass
class RefactorPlan:
    """重构计划数据类"""
    project_path: str
    suggestions: List[RefactorSuggestion]
    total_effort: str
    expected_improvement: Dict[str, Any]
    execution_order: List[str]  # suggestion IDs in order


class RefactorStrategistAgent:
    """
    重构策略Agent

    职责：
    1. 分析代码问题
    2. 生成重构方案
    3. 评估重构优先级
    4. 制定重构计划
    """

    def __init__(self, config: Dict[str, Any], ai_client=None):
        self.config = config
        self.ai_client = ai_client
        self.suggestions: List[RefactorSuggestion] = []

    def generate_refactor_plan(self, analysis_result: Dict[str, Any]) -> RefactorPlan:
        """
        生成重构计划

        Args:
            analysis_result: 代码分析结果

        Returns:
            RefactorPlan: 重构计划
        """
        project_path = analysis_result.get("project_path", "")
        issues = analysis_result.get("issues", [])

        # 为每个问题生成重构建议
        for issue in issues:
            suggestion = self._generate_suggestion(issue)
            if suggestion:
                self.suggestions.append(suggestion)

        # 按优先级排序
        self.suggestions = self._prioritize_suggestions(self.suggestions)

        # 生成执行顺序
        execution_order = [s.id for s in self.suggestions]

        # 计算总工作量
        total_effort = self._calculate_total_effort(self.suggestions)

        # 预估改进效果
        expected_improvement = self._estimate_improvement(analysis_result, self.suggestions)

        return RefactorPlan(
            project_path=project_path,
            suggestions=self.suggestions,
            total_effort=total_effort,
            expected_improvement=expected_improvement,
            execution_order=execution_order
        )

    def _generate_suggestion(self, issue: Dict[str, Any]) -> Optional[RefactorSuggestion]:
        """
        为单个问题生成重构建议

        Args:
            issue: 代码问题

        Returns:
            Optional[RefactorSuggestion]: 重构建议
        """
        issue_type = issue.get("issue_type", "")
        severity = issue.get("severity", "medium")

        # 根据问题类型生成不同的重构建议
        if issue_type == "complexity":
            return self._handle_complexity_issue(issue)
        elif issue_type == "duplication":
            return self._handle_duplication_issue(issue)
        elif issue_type == "style":
            return self._handle_style_issue(issue)
        elif issue_type == "syntax":
            return self._handle_syntax_issue(issue)
        else:
            return self._handle_generic_issue(issue)

    def _handle_complexity_issue(self, issue: Dict[str, Any]) -> RefactorSuggestion:
        """处理复杂度问题"""
        description = issue.get("description", "")

        # 判断是函数过长还是圈复杂度过高
        if "圈复杂度" in description:
            refactor_type = RefactorType.EXTRACT_METHOD
            title = "提取方法降低圈复杂度"
            suggested_code = self._generate_extract_method_template(issue)
            benefits = ["降低圈复杂度", "提高代码可读性", "便于测试"]
            risks = ["可能引入新的函数调用开销"]
        else:
            refactor_type = RefactorType.EXTRACT_METHOD
            title = "拆分过长函数"
            suggested_code = self._generate_split_function_template(issue)
            benefits = ["提高可维护性", "降低认知负荷", "便于复用"]
            risks = ["需要确保拆分后的函数接口清晰"]

        return RefactorSuggestion(
            id=self._generate_id(issue),
            file_path=issue.get("file_path", ""),
            line_number=issue.get("line_number", 0),
            refactor_type=refactor_type,
            priority=self._map_severity_to_priority(issue.get("severity", "medium")),
            title=title,
            description=description,
            current_code=issue.get("code_snippet", ""),
            suggested_code=suggested_code,
            benefits=benefits,
            risks=risks,
            effort_estimate="medium",
            impact_estimate="high"
        )

    def _handle_duplication_issue(self, issue: Dict[str, Any]) -> RefactorSuggestion:
        """处理重复代码问题"""
        return RefactorSuggestion(
            id=self._generate_id(issue),
            file_path=issue.get("file_path", ""),
            line_number=issue.get("line_number", 0),
            refactor_type=RefactorType.REMOVE_DUPLICATION,
            priority=RefactorPriority.MEDIUM,
            title="消除重复代码",
            description=issue.get("description", ""),
            current_code=issue.get("code_snippet", ""),
            suggested_code=self._generate_extract_function_template(issue),
            benefits=["减少代码冗余", "提高可维护性", "降低修改成本"],
            risks=["需要确保提取的函数具有通用性"],
            effort_estimate="medium",
            impact_estimate="medium"
        )

    def _handle_style_issue(self, issue: Dict[str, Any]) -> RefactorSuggestion:
        """处理代码风格问题"""
        description = issue.get("description", "")

        if "参数过多" in description:
            refactor_type = RefactorType.INTRODUCE_PARAMETER_OBJECT
            title = "引入参数对象封装参数"
            suggested_code = self._generate_parameter_object_template(issue)
            benefits = ["简化函数签名", "提高可读性", "便于扩展"]
            risks = ["需要创建新的数据类"]
        else:
            refactor_type = RefactorType.RENAME
            title = "改进代码命名"
            suggested_code = "// 重命名变量/函数以提高可读性"
            benefits = ["提高代码可读性", "降低理解成本"]
            risks = ["需要更新所有引用"]

        return RefactorSuggestion(
            id=self._generate_id(issue),
            file_path=issue.get("file_path", ""),
            line_number=issue.get("line_number", 0),
            refactor_type=refactor_type,
            priority=RefactorPriority.LOW,
            title=title,
            description=description,
            current_code=issue.get("code_snippet", ""),
            suggested_code=suggested_code,
            benefits=benefits,
            risks=risks,
            effort_estimate="low",
            impact_estimate="low"
        )

    def _handle_syntax_issue(self, issue: Dict[str, Any]) -> RefactorSuggestion:
        """处理语法问题"""
        return RefactorSuggestion(
            id=self._generate_id(issue),
            file_path=issue.get("file_path", ""),
            line_number=issue.get("line_number", 0),
            refactor_type=RefactorType.RENAME,
            priority=RefactorPriority.CRITICAL,
            title="修复语法错误",
            description=issue.get("description", ""),
            current_code=issue.get("code_snippet", ""),
            suggested_code="// 根据错误信息修复语法",
            benefits=["确保代码可运行", "避免运行时错误"],
            risks=["需要仔细验证修复后的逻辑"],
            effort_estimate="low",
            impact_estimate="high"
        )

    def _handle_generic_issue(self, issue: Dict[str, Any]) -> RefactorSuggestion:
        """处理通用问题"""
        return RefactorSuggestion(
            id=self._generate_id(issue),
            file_path=issue.get("file_path", ""),
            line_number=issue.get("line_number", 0),
            refactor_type=RefactorType.RENAME,
            priority=RefactorPriority.LOW,
            title="代码改进",
            description=issue.get("description", ""),
            current_code=issue.get("code_snippet", ""),
            suggested_code="// 根据具体问题进行改进",
            benefits=["提高代码质量"],
            risks=["需要评估改进的影响"],
            effort_estimate="low",
            impact_estimate="low"
        )

    def _generate_extract_method_template(self, issue: Dict[str, Any]) -> str:
        """生成提取方法的模板代码"""
        return '''# 建议：将复杂逻辑提取为独立方法
def extracted_method():
    """
    提取的方法，处理特定逻辑
    """
    # TODO: 实现具体逻辑
    pass

# 在原位置调用
result = extracted_method()'''

    def _generate_split_function_template(self, issue: Dict[str, Any]) -> str:
        """生成拆分函数的模板代码"""
        return '''# 建议：将长函数拆分为多个小函数
def part1():
    """处理第一部分逻辑"""
    pass

def part2():
    """处理第二部分逻辑"""
    pass

def main_function():
    """主函数，协调各部分"""
    result1 = part1()
    result2 = part2()
    return combine_results(result1, result2)'''

    def _generate_extract_function_template(self, issue: Dict[str, Any]) -> str:
        """生成提取重复代码为函数的模板"""
        return '''# 建议：提取重复代码为独立函数
def common_operation():
    """
    提取的公共操作
    """
    # TODO: 实现重复的代码逻辑
    pass

# 在原位置调用
common_operation()'''

    def _generate_parameter_object_template(self, issue: Dict[str, Any]) -> str:
        """生成参数对象的模板代码"""
        return '''# 建议：引入参数对象
from dataclasses import dataclass

@dataclass
class FunctionParams:
    """函数参数封装"""
    param1: str
    param2: int
    param3: bool
    # 添加其他参数

def improved_function(params: FunctionParams):
    """改进后的函数"""
    # 使用 params.param1, params.param2 等
    pass'''

    def _generate_id(self, issue: Dict[str, Any]) -> str:
        """生成建议ID"""
        import hashlib
        content = f"{issue.get('file_path', '')}:{issue.get('line_number', 0)}:{issue.get('issue_type', '')}"
        return hashlib.md5(content.encode()).hexdigest()[:8]

    def _map_severity_to_priority(self, severity: str) -> RefactorPriority:
        """将严重程度映射为优先级"""
        mapping = {
            "critical": RefactorPriority.CRITICAL,
            "high": RefactorPriority.HIGH,
            "medium": RefactorPriority.MEDIUM,
            "low": RefactorPriority.LOW
        }
        return mapping.get(severity, RefactorPriority.MEDIUM)

    def _prioritize_suggestions(self, suggestions: List[RefactorSuggestion]) -> List[RefactorSuggestion]:
        """按优先级排序建议"""
        priority_order = {
            RefactorPriority.CRITICAL: 0,
            RefactorPriority.HIGH: 1,
            RefactorPriority.MEDIUM: 2,
            RefactorPriority.LOW: 3
        }
        return sorted(suggestions, key=lambda x: priority_order.get(x.priority, 4))

    def _calculate_total_effort(self, suggestions: List[RefactorSuggestion]) -> str:
        """计算总工作量"""
        effort_scores = {"low": 1, "medium": 3, "high": 5}
        total_score = sum(effort_scores.get(s.effort_estimate, 1) for s in suggestions)

        if total_score <= 5:
            return "low"
        elif total_score <= 15:
            return "medium"
        else:
            return "high"

    def _estimate_improvement(self, analysis_result: Dict[str, Any], suggestions: List[RefactorSuggestion]) -> Dict[str, Any]:
        """预估改进效果"""
        current_score = analysis_result.get("metrics", {}).get("quality_score", 50)

        # 简单估算：每个建议提升2-5分
        improvement_per_suggestion = {
            RefactorPriority.CRITICAL: 5,
            RefactorPriority.HIGH: 4,
            RefactorPriority.MEDIUM: 3,
            RefactorPriority.LOW: 2
        }

        total_improvement = sum(
            improvement_per_suggestion.get(s.priority, 2) for s in suggestions
        )

        expected_score = min(100, current_score + total_improvement)

        return {
            "current_score": current_score,
            "expected_score": expected_score,
            "improvement": expected_score - current_score,
            "issues_to_fix": len(suggestions)
        }

    def get_suggestions_by_priority(self) -> List[RefactorSuggestion]:
        """按优先级获取建议"""
        return self.suggestions

    def get_suggestions_by_file(self) -> Dict[str, List[RefactorSuggestion]]:
        """按文件分组获取建议"""
        suggestions_by_file = {}
        for suggestion in self.suggestions:
            if suggestion.file_path not in suggestions_by_file:
                suggestions_by_file[suggestion.file_path] = []
            suggestions_by_file[suggestion.file_path].append(suggestion)
        return suggestions_by_file

    def export_plan_to_json(self, plan: RefactorPlan) -> str:
        """导出计划为JSON格式"""
        plan_dict = {
            "project_path": plan.project_path,
            "total_effort": plan.total_effort,
            "expected_improvement": plan.expected_improvement,
            "execution_order": plan.execution_order,
            "suggestions": [
                {
                    "id": s.id,
                    "file_path": s.file_path,
                    "line_number": s.line_number,
                    "refactor_type": s.refactor_type.value,
                    "priority": s.priority.value,
                    "title": s.title,
                    "description": s.description,
                    "benefits": s.benefits,
                    "risks": s.risks,
                    "effort_estimate": s.effort_estimate,
                    "impact_estimate": s.impact_estimate
                }
                for s in plan.suggestions
            ]
        }
        return json.dumps(plan_dict, indent=2, ensure_ascii=False)