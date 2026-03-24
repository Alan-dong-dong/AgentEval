"""
CLI命令行工具
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path
from typing import List, Optional

from agenteval.core.engine import EvaluationEngine
from agenteval.models.task import TestCase
from agenteval.evaluators.correctness import CorrectnessEvaluator
from agenteval.evaluators.tool_usage import ToolUsageEvaluator
from agenteval.evaluators.efficiency import EfficiencyEvaluator
from agenteval.simple.presets import PresetDatasets


def create_parser() -> argparse.ArgumentParser:
    """创建CLI解析器

    Returns:
        argparse.ArgumentParser: 命令行解析器
    """
    parser = argparse.ArgumentParser(
        prog="agenteval",
        description="AgentEval - 专为AI Agent设计的开源评估框架",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  agenteval quick mymodule.my_agent "What is 2+2?" --expected "4"
  agenteval run eval_config.yaml --output results.json
  agenteval preset mymodule.my_agent --dataset basic_qa
  agenteval list --type evaluators
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # quick命令 - 快速评估
    quick_parser = subparsers.add_parser("quick", help="快速评估Agent")
    quick_parser.add_argument("agent", help="Agent模块路径，如 mymodule.my_agent")
    quick_parser.add_argument("prompt", help="测试提示词")
    quick_parser.add_argument("--expected", help="期望输出")
    quick_parser.add_argument("--model", default="gpt-4", help="评估模型")
    quick_parser.add_argument("--timeout", type=int, default=30, help="超时秒数")

    # run命令 - 运行评估套件
    run_parser = subparsers.add_parser("run", help="运行评估套件")
    run_parser.add_argument("config", help="配置文件路径")
    run_parser.add_argument("--output", "-o", help="结果输出路径")
    run_parser.add_argument(
        "--format",
        choices=["json", "csv", "html"],
        default="json",
        help="输出格式",
    )
    run_parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")

    # preset命令 - 使用预设数据集
    preset_parser = subparsers.add_parser("preset", help="使用预设数据集评估")
    preset_parser.add_argument("agent", help="Agent模块路径")
    preset_parser.add_argument(
        "--dataset",
        choices=["basic_qa", "tool_use", "safety", "conversation"],
        default="basic_qa",
        help="数据集名称",
    )
    preset_parser.add_argument("--output", "-o", help="结果输出路径")
    preset_parser.add_argument(
        "--format",
        choices=["json", "csv", "html"],
        default="json",
        help="输出格式",
    )

    # list命令 - 列出可用组件
    list_parser = subparsers.add_parser("list", help="列出可用组件")
    list_parser.add_argument(
        "--type",
        choices=["evaluators", "datasets", "adapters", "all"],
        default="all",
        help="列出类型",
    )

    # version命令
    subparsers.add_parser("version", help="显示版本信息")

    return parser


def load_agent(module_path: str):
    """加载Agent

    Args:
        module_path: Agent模块路径

    Returns:
        Agent实例
    """
    parts = module_path.rsplit(".", 1)
    if len(parts) != 2:
        raise ValueError(f"Invalid module path: {module_path}")

    module_name, attr_name = parts
    import importlib

    module = importlib.import_module(module_name)
    return getattr(module, attr_name)


async def run_quick_eval(args):
    """运行快速评估

    Args:
        args: 命令行参数
    """
    try:
        agent = load_agent(args.agent)
    except Exception as e:
        print(f"Error loading agent: {e}", file=sys.stderr)
        sys.exit(1)

    from agenteval import quick_eval

    result = quick_eval(agent, args.prompt, expected=args.expected)

    print(f"Score: {result['score']:.2f}")
    print(f"Response: {result['response']}")
    print(f"Latency: {result['latency_ms']:.2f}ms")

    if not result["success"]:
        print(f"Error: {result['error']}", file=sys.stderr)
        sys.exit(1)


async def run_evaluation(args):
    """运行评估套件

    Args:
        args: 命令行参数
    """
    import yaml

    # 加载配置
    config_path = Path(args.config)
    if not config_path.exists():
        print(f"Config file not found: {args.config}", file=sys.stderr)
        sys.exit(1)

    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # 加载Agent
    try:
        agent = load_agent(config["agent"]["module"])
    except Exception as e:
        print(f"Error loading agent: {e}", file=sys.stderr)
        sys.exit(1)

    # 创建引擎
    engine = EvaluationEngine()

    # 添加评估器
    evaluator_configs = config.get("evaluators", [])
    for eval_config in evaluator_configs:
        name = eval_config.get("name", "correctness")
        if name == "correctness":
            engine.add_evaluator(CorrectnessEvaluator(eval_config))
        elif name == "tool_usage":
            engine.add_evaluator(ToolUsageEvaluator(eval_config))
        elif name == "efficiency":
            engine.add_evaluator(EfficiencyEvaluator(eval_config))

    # 加载数据集
    dataset_config = config.get("dataset", {})
    if dataset_config.get("type") == "preset":
        test_cases = PresetDatasets.get_dataset_by_name(dataset_config["name"])
    else:
        # 从文件加载
        dataset_path = dataset_config.get("path", "")
        with open(dataset_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            test_cases = [TestCase.from_dict(tc) for tc in data]

    # 创建适配器
    from agenteval.adapters.base import CallableAdapter, AgentConfig

    agent_config = AgentConfig(
        framework="callable",
        agent_callable=agent if callable(agent) else None,
        agent_instance=agent if not callable(agent) else None,
    )
    adapter = CallableAdapter(agent_config)
    engine.set_adapter(adapter)

    # 运行评估
    if args.verbose:
        print(f"Running evaluation with {len(test_cases)} test cases...")

    result = await engine.evaluate_batch(test_cases)

    # 输出结果
    print(result.summary())

    # 保存结果
    if args.output:
        output_path = Path(args.output)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result.to_dict(), f, indent=2, ensure_ascii=False)
        print(f"\nResults saved to: {args.output}")


async def run_preset(args):
    """运行预设数据集评估

    Args:
        args: 命令行参数
    """
    try:
        agent = load_agent(args.agent)
    except Exception as e:
        print(f"Error loading agent: {e}", file=sys.stderr)
        sys.exit(1)

    # 获取预设数据集
    test_cases = PresetDatasets.get_dataset_by_name(args.dataset)

    # 创建引擎
    engine = EvaluationEngine()
    engine.add_evaluators(
        [
            CorrectnessEvaluator(),
            EfficiencyEvaluator(),
        ]
    )

    # 创建适配器
    from agenteval.adapters.base import CallableAdapter, AgentConfig

    agent_config = AgentConfig(
        framework="callable",
        agent_callable=agent if callable(agent) else None,
        agent_instance=agent if not callable(agent) else None,
    )
    adapter = CallableAdapter(agent_config)
    engine.set_adapter(adapter)

    # 运行评估
    print(
        f"Running evaluation with {args.dataset} dataset ({len(test_cases)} cases)..."
    )
    result = await engine.evaluate_batch(test_cases)

    # 输出结果
    print(result.summary())

    # 保存结果
    if args.output:
        output_path = Path(args.output)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result.to_dict(), f, indent=2, ensure_ascii=False)
        print(f"\nResults saved to: {args.output}")


def run_list(args):
    """列出可用组件

    Args:
        args: 命令行参数
    """
    show_type = args.type

    if show_type in ("evaluators", "all"):
        print("Available Evaluators:")
        print("  - CorrectnessEvaluator: 功能正确性评估")
        print("  - ToolUsageEvaluator: 工具使用评估")
        print("  - EfficiencyEvaluator: 响应效率评估")
        print()

    if show_type in ("datasets", "all"):
        print("Available Datasets:")
        print("  - basic_qa: 基础问答测试集")
        print("  - tool_use: 工具使用测试集")
        print("  - safety: 安全测试集")
        print("  - conversation: 对话测试集")
        print()

    if show_type in ("adapters", "all"):
        print("Available Adapters:")
        print("  - callable: 通用Callable适配器")
        print("  - langchain: LangChain适配器")
        print()


def run_version():
    """显示版本信息"""
    from agenteval import __version__

    print(f"AgentEval v{__version__}")
    print("专为AI Agent设计的开源评估框架")


def main():
    """CLI主入口"""
    parser = create_parser()
    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    if args.command == "quick":
        asyncio.run(run_quick_eval(args))
    elif args.command == "run":
        asyncio.run(run_evaluation(args))
    elif args.command == "preset":
        asyncio.run(run_preset(args))
    elif args.command == "list":
        run_list(args)
    elif args.command == "version":
        run_version()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
