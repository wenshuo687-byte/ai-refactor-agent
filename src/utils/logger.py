"""
日志工具 - 负责日志记录
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime


class Logger:
    """
    日志工具类

    职责：
    1. 配置日志记录
    2. 记录不同级别的日志
    3. 日志格式化
    4. 日志文件管理
    """

    def __init__(self, name: str = "ai_refactor_agent", log_file: Optional[str] = None, level: int = logging.INFO):
        """
        初始化日志工具

        Args:
            name: 日志名称
            log_file: 日志文件路径
            level: 日志级别
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        # 清除已有的处理器
        self.logger.handlers.clear()

        # 创建格式化器
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # 控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        # 文件处理器
        if log_file:
            self._setup_file_handler(log_file, formatter, level)

    def _setup_file_handler(self, log_file: str, formatter: logging.Formatter, level: int):
        """设置文件处理器"""
        try:
            # 确保日志目录存在
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)

            # 创建文件处理器
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

        except Exception as e:
            print(f"设置日志文件失败: {e}")

    def debug(self, message: str):
        """记录调试日志"""
        self.logger.debug(message)

    def info(self, message: str):
        """记录信息日志"""
        self.logger.info(message)

    def warning(self, message: str):
        """记录警告日志"""
        self.logger.warning(message)

    def error(self, message: str):
        """记录错误日志"""
        self.logger.error(message)

    def critical(self, message: str):
        """记录严重错误日志"""
        self.logger.critical(message)

    def exception(self, message: str):
        """记录异常日志（包含堆栈跟踪）"""
        self.logger.exception(message)

    def log_analysis_start(self, project_path: str):
        """记录分析开始"""
        self.info(f"开始分析项目: {project_path}")
        self.info("=" * 60)

    def log_analysis_complete(self, total_files: int, total_lines: int, issues_count: int):
        """记录分析完成"""
        self.info(f"分析完成:")
        self.info(f"  - 扫描文件数: {total_files}")
        self.info(f"  - 代码总行数: {total_lines}")
        self.info(f"  - 发现问题数: {issues_count}")

    def log_refactor_plan_generated(self, suggestions_count: int, total_effort: str):
        """记录重构计划生成"""
        self.info(f"重构计划生成完成:")
        self.info(f"  - 重构建议数: {suggestions_count}")
        self.info(f"  - 总工作量: {total_effort}")

    def log_execution_start(self, suggestion_id: str, refactor_type: str):
        """记录执行开始"""
        self.info(f"开始执行重构: {suggestion_id}")
        self.info(f"  - 重构类型: {refactor_type}")

    def log_execution_complete(self, suggestion_id: str, status: str, message: str):
        """记录执行完成"""
        self.info(f"重构执行完成: {suggestion_id}")
        self.info(f"  - 状态: {status}")
        self.info(f"  - 消息: {message}")

    def log_test_results(self, passed: int, failed: int, errors: int):
        """记录测试结果"""
        self.info(f"测试结果:")
        self.info(f"  - 通过: {passed}")
        self.info(f"  - 失败: {failed}")
        self.info(f"  - 错误: {errors}")

    def log_report_saved(self, report_path: str):
        """记录报告保存"""
        self.info(f"报告已保存: {report_path}")

    def log_error_with_context(self, error: Exception, context: str):
        """记录带上下文的错误"""
        self.error(f"{context}: {type(error).__name__}: {error}")

    def create_child_logger(self, name: str) -> 'Logger':
        """创建子日志器"""
        child_logger = Logger(f"{self.logger.name}.{name}")
        return child_logger