# AI智能重构Agent

基于多Agent协作的智能代码重构系统，能够自动识别技术债、生成重构方案并执行验证。

## 核心特性

- **多Agent协作**：代码分析Agent、重构策略Agent、执行验证Agent协同工作
- **长链推理**：分析→决策→执行→验证的完整推理链
- **智能决策**：基于代码质量和架构分析的重构优先级排序
- **闭环验证**：自动运行测试确保重构不引入新问题

## 架构设计

```
┌─────────────────────────────────────────────────────────┐
│                    主协调器 (Coordinator)                  │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │ 代码分析Agent │  │ 重构策略Agent │  │ 执行验证Agent │    │
│  └─────────────┘  └─────────────┘  └─────────────┘    │
│         │                │                │            │
│         ▼                ▼                ▼            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │  技术债识别   │  │  重构方案生成  │  │  测试验证    │    │
│  │  代码质量分析 │  │  优先级排序   │  │  质量评估    │    │
│  │  架构评估    │  │  风险评估    │  │  报告生成    │    │
│  └─────────────┘  └─────────────┘  └─────────────┘    │
└─────────────────────────────────────────────────────────┘
```

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置

编辑 `config/config.yaml` 配置AI模型和扫描参数。

### 运行

```bash
python src/main.py --project-path /path/to/your/project
```

## 使用示例

```python
from src.main import RefactorAgent

# 初始化Agent
agent = RefactorAgent(project_path="./my_project")

# 运行完整重构流程
results = agent.run_full_analysis()

# 查看重构建议
for suggestion in results.suggestions:
    print(f"文件: {suggestion.file}")
    print(f"问题: {suggestion.issue}")
    print(f"建议: {suggestion.refactor_method}")
    print(f"优先级: {suggestion.priority}")
```

## 技术栈

- Python 3.9+
- Claude API / OpenAI API
- AST解析 (ast, libcst)
- 代码分析 (pylint, flake8)
- 测试框架 (pytest)

## 项目结构

```
ai-refactor-agent/
├── src/
│   ├── agents/          # Agent实现
│   ├── core/            # 核心功能
│   ├── utils/           # 工具函数
│   └── main.py          # 主入口
├── tests/               # 测试代码
├── examples/            # 使用示例
├── config/              # 配置文件
└── requirements.txt     # 依赖列表
```

## 贡献指南

欢迎提交Issue和Pull Request！

## 许可证

MIT License