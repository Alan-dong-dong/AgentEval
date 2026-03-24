"""
基础测试
"""

import pytest
from agenteval.models.task import (
    TestCase,
    ToolDefinition,
    TaskType,
    TaskDifficulty,
    AgentConfig,
)
from agenteval.models.result import MetricScore, EvaluationResult, BenchmarkResult


class TestTestCase:
    """TestCase测试"""

    def test_create_test_case(self):
        """测试创建TestCase"""
        test_case = TestCase(
            name="test",
            input_message="What is 2+2?",
            expected_output="4",
        )

        assert test_case.name == "test"
        assert test_case.input_message == "What is 2+2?"
        assert test_case.expected_output == "4"
        assert test_case.task_type == TaskType.SINGLE_TURN

    def test_test_case_to_dict(self):
        """测试TestCase转字典"""
        test_case = TestCase(
            name="test",
            input_message="Hello",
            tags=["test", "simple"],
        )

        data = test_case.to_dict()
        assert data["name"] == "test"
        assert data["input_message"] == "Hello"
        assert data["tags"] == ["test", "simple"]

    def test_test_case_from_dict(self):
        """测试从字典创建TestCase"""
        data = {
            "name": "test",
            "input_message": "Hello",
            "expected_output": "Hi",
            "task_type": "single_turn",
            "difficulty": "easy",
        }

        test_case = TestCase.from_dict(data)
        assert test_case.name == "test"
        assert test_case.input_message == "Hello"
        assert test_case.task_type == TaskType.SINGLE_TURN
        assert test_case.difficulty == TaskDifficulty.EASY

    def test_tool_definition(self):
        """测试ToolDefinition"""
        tool = ToolDefinition(
            name="calculator",
            description="Perform calculations",
            parameters={"expression": {"type": "string"}},
        )

        assert tool.name == "calculator"
        assert tool.description == "Perform calculations"


class TestMetricScore:
    """MetricScore测试"""

    def test_create_metric_score(self):
        """测试创建MetricScore"""
        score = MetricScore(
            name="correctness",
            score=0.95,
            weight=1.0,
            details="Good response",
        )

        assert score.name == "correctness"
        assert score.score == 0.95
        assert score.weight == 1.0

    def test_metric_score_to_dict(self):
        """测试MetricScore转字典"""
        score = MetricScore(
            name="test",
            score=0.8,
            metadata={"key": "value"},
        )

        data = score.to_dict()
        assert data["name"] == "test"
        assert data["score"] == 0.8
        assert data["metadata"]["key"] == "value"


class TestEvaluationResult:
    """EvaluationResult测试"""

    def test_create_evaluation_result(self):
        """测试创建EvaluationResult"""
        result = EvaluationResult(
            test_case_id="test-001",
            agent_response="Hello",
            overall_score=0.9,
            success=True,
        )

        assert result.test_case_id == "test-001"
        assert result.agent_response == "Hello"
        assert result.overall_score == 0.9
        assert result.success is True

    def test_evaluation_result_to_dict(self):
        """测试EvaluationResult转字典"""
        result = EvaluationResult(
            test_case_id="test-001",
            success=True,
        )

        data = result.to_dict()
        assert data["test_case_id"] == "test-001"
        assert data["success"] is True


class TestBenchmarkResult:
    """BenchmarkResult测试"""

    def test_create_benchmark_result(self):
        """测试创建BenchmarkResult"""
        benchmark = BenchmarkResult(
            id="bench-001",
            name="Test Benchmark",
            total_tests=10,
            passed_tests=8,
            failed_tests=2,
            average_score=0.85,
        )

        assert benchmark.id == "bench-001"
        assert benchmark.total_tests == 10
        assert benchmark.passed_tests == 8
        assert benchmark.average_score == 0.85

    def test_benchmark_summary(self):
        """测试BenchmarkResult摘要"""
        benchmark = BenchmarkResult(
            id="bench-001",
            name="Test Benchmark",
            total_tests=10,
            passed_tests=8,
            failed_tests=2,
            average_score=0.85,
            dimension_scores={"correctness": 0.9, "efficiency": 0.8},
        )

        summary = benchmark.summary()
        assert "Test Benchmark" in summary
        assert "0.85" in summary
        assert "correctness" in summary


class TestAgentConfig:
    """AgentConfig测试"""

    def test_create_agent_config(self):
        """测试创建AgentConfig"""
        config = AgentConfig(
            framework="callable",
            agent_callable=lambda x: "response",
        )

        assert config.framework == "callable"
        assert callable(config.agent_callable)
