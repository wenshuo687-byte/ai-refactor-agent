"""
AI智能重构Agent - 主入口

使用示例：
    python src/main.py --project-path /path/to/your/project
    python src/main.py --project-path ./my_project --config config/config.yaml
    python src/main.py --project-path ./my_project --no-test
"""

import argparse
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.agents.coordinator import Coordinator
from src.utils.logger import Logger


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="AI智能重构Agent - 基于多Agent协作的智能代码重构系统",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s --project-path ./my_project
  %(prog)s --project-path /path/to/project --config config/config.yaml
  %(prog)s --project-path ./my_project --no-test --output reports/
        """
    )

    parser.add_argument(
        "--project-path",
        type=str,
        required=True,
        help="项目根目录路径"
    )

    parser.add_argument(
        "--config",
        type=str,
        default="config/config.yaml",
        help="配置文件路径 (默认: config/config.yaml)"
    )

    parser.add_argument(
        "--no-test",
        action="store_true",
        help="跳过测试运行"
    )

    parser.add_argument(
        "--output",
        type=str,
        default="reports",
        help="报告输出目录 (默认: reports)"
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="显示详细日志"
    )

    return parser.parse_args()


def main():
    """主函数"""
    args = parse_args()

    # 初始化日志
    log_level = "DEBUG" if args.verbose else "INFO"
    logger = Logger(level=getattr(__import__('logging'), log_level))

    # 验证项目路径
    project_path = Path(args.project_path)
    if not project_path.exists():
        logger.error(f"项目路径不存在: {project_path}")
        sys.exit(1)

    if not project_path.is_dir():
        logger.error(f"项目路径不是目录: {project_path}")
        sys.exit(1)

    # 验证配置文件
    config_path = Path(args.config)
    if not config_path.exists():
        logger.warning(f"配置文件不存在: {config_path}，将使用默认配置")

    # 更新配置
    config = {}
    if config_path.exists():
        import yaml
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f) or {}

    # 如果指定了跳过测试，更新配置
    if args.no_test:
        if "refactor" not in config:
            config["refactor"] = {}
        config["refactor"]["run_tests"] = False

    # 打印启动信息
    print("\n" + "=" * 60)
    print("AI智能重构Agent")
    print("基于多Agent协作的智能代码重构系统")
    print("=" * 60)
    print(f"\n项目路径: {project_path.absolute()}")
    print(f"配置文件: {config_path.absolute()}")
    print(f"报告目录: {args.output}")
    print(f"测试运行: {'是' if not args.no_test else '否'}")
    print(f"详细日志: {'是' if args.verbose else '否'}")
    print("\n" + "=" * 60 + "\n")

    try:
        # 初始化协调器
        coordinator = Coordinator(config_path=str(config_path))

        # 运行完整分析
        results = coordinator.run_full_analysis(str(project_path))

        # 检查是否有错误
        if "error" in results:
            logger.error(f"分析失败: {results['error']}")
            sys.exit(1)

        # 打印摘要
        print("\n" + "=" * 60)
        print("分析摘要")
        print("=" * 60)

        analysis = results.get("analysis", {})
        print(f"\n代码分析:")
        print(f"  - 扫描文件数: {analysis.get('total_files', 0)}")
        print(f"  - 代码总行数: {analysis.get('total_lines', 0)}")
        print(f"  - 发现问题数: {analysis.get('issues_count', 0)}")
        print(f"  - 质量分数: {analysis.get('quality_score', 0)}/100")

        plan = results.get("refactor_plan", {})
        print(f"\n重构计划:")
        print(f"  - 重构建议数: {plan.get('total_suggestions', 0)}")
        print(f"  - 总工作量: {plan.get('total_effort', 'unknown')}")

        improvement = plan.get("expected_improvement", {})
        print(f"  - 预期质量提升: {improvement.get('improvement', 0)}分")

        execution = results.get("execution", {})
        print(f"\n执行结果:")
        print(f"  - 已执行: {execution.get('total_executed', 0)}")
        print(f"  - 成功: {execution.get('successful', 0)}")
        print(f"  - 失败: {execution.get('failed', 0)}")
        print(f"  - 跳过: {execution.get('skipped', 0)}")
        print(f"  - 成功率: {execution.get('success_rate', 0):.1%}")

        print("\n" + "=" * 60)
        print("分析完成！报告已保存到 reports/ 目录")
        print("=" * 60 + "\n")

        return 0

    except KeyboardInterrupt:
        print("\n\n用户中断，正在退出...")
        return 130

    except Exception as e:
        logger.exception(f"程序异常: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())