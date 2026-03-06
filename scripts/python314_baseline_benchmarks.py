#!/usr/bin/env python3
"""
Python 3.14 Baseline Benchmark Collection Script.

Collects performance baselines for comparing Python 3.12 vs 3.14.
Measures import times, object creation, async overhead, serialization,
and orchestration-related patterns used throughout TTA.

Usage:
    uv run python scripts/python314_baseline_benchmarks.py
    uv run python scripts/python314_baseline_benchmarks.py --output results.json
"""

import argparse
import asyncio
import gc
import json
import statistics
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class BenchmarkResult:
    """Result from a single benchmark."""

    name: str
    category: str
    iterations: int
    times: list[float] = field(default_factory=list)
    unit: str = "seconds"

    @property
    def mean(self) -> float:
        return statistics.mean(self.times) if self.times else 0.0

    @property
    def median(self) -> float:
        return statistics.median(self.times) if self.times else 0.0

    @property
    def stdev(self) -> float:
        return statistics.stdev(self.times) if len(self.times) > 1 else 0.0

    @property
    def p95(self) -> float:
        if not self.times:
            return 0.0
        sorted_times = sorted(self.times)
        idx = int(len(sorted_times) * 0.95)
        return sorted_times[min(idx, len(sorted_times) - 1)]

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "category": self.category,
            "iterations": self.iterations,
            "mean": self.mean,
            "median": self.median,
            "stdev": self.stdev,
            "p95": self.p95,
            "min": min(self.times) if self.times else 0.0,
            "max": max(self.times) if self.times else 0.0,
            "unit": self.unit,
        }


def benchmark_import_times() -> list[BenchmarkResult]:
    """Benchmark module import times for core TTA packages.

    Uses subprocess to get clean cold-import measurements, avoiding issues
    with removing modules from sys.modules (which corrupts stdlib internals).
    """
    import subprocess

    results = []
    modules = [
        ("src.common", "core"),
        ("src.agent_orchestration", "orchestration"),
        ("src.api_gateway", "api"),
        ("src.monitoring", "monitoring"),
        ("src.components", "components"),
        ("json", "stdlib"),
        ("asyncio", "stdlib"),
        ("dataclasses", "stdlib"),
        ("typing", "stdlib"),
        ("pathlib", "stdlib"),
    ]

    python_exe = sys.executable

    for module_name, category in modules:
        times = []
        for _ in range(5):
            # Use subprocess for clean import measurement
            # Module names are from the hardcoded list above; validated for safety
            if not module_name.replace(".", "_").replace("_", "").isalnum():
                times.append(0.0)
                continue
            try:
                proc = subprocess.run(
                    [
                        python_exe,
                        "-c",
                        "import time; s=time.perf_counter(); "
                        f"import {module_name}; "
                        "print(time.perf_counter()-s)",
                    ],
                    check=False,
                    capture_output=True,
                    text=True,
                    timeout=30,
                    cwd=str(Path(__file__).resolve().parent.parent),
                )
                if proc.returncode == 0 and proc.stdout.strip():
                    times.append(float(proc.stdout.strip()))
                else:
                    times.append(0.0)
            except (subprocess.TimeoutExpired, ValueError):
                times.append(0.0)

        results.append(
            BenchmarkResult(
                name=f"import_{module_name}",
                category=f"import_{category}",
                iterations=5,
                times=times,
            )
        )

    return results


def benchmark_object_creation() -> list[BenchmarkResult]:
    """Benchmark object creation patterns used in TTA."""
    results = []

    # Dataclass creation
    @dataclass
    class SampleMessage:
        sender: str
        recipient: str
        content: str
        timestamp: float
        metadata: dict

    times = []
    for _ in range(1000):
        start = time.perf_counter()
        for _ in range(100):
            SampleMessage(
                sender="agent_a",
                recipient="agent_b",
                content="test message",
                timestamp=time.time(),
                metadata={"key": "value"},
            )
        elapsed = time.perf_counter() - start
        times.append(elapsed)

    results.append(
        BenchmarkResult(
            name="dataclass_creation_100x",
            category="object_creation",
            iterations=1000,
            times=times,
        )
    )

    # Dict creation (message-like)
    times = []
    for _ in range(1000):
        start = time.perf_counter()
        for _ in range(100):
            {
                "sender": "agent_a",
                "recipient": "agent_b",
                "content": "test message",
                "timestamp": time.time(),
                "metadata": {"key": "value"},
            }
        elapsed = time.perf_counter() - start
        times.append(elapsed)

    results.append(
        BenchmarkResult(
            name="dict_creation_100x",
            category="object_creation",
            iterations=1000,
            times=times,
        )
    )

    return results


def benchmark_serialization() -> list[BenchmarkResult]:
    """Benchmark JSON serialization patterns used in agent messaging."""
    results = []

    sample_message = {
        "type": "agent_message",
        "sender": "input_processing_agent",
        "recipient": "narrative_generation_agent",
        "payload": {
            "user_input": "I want to explore the forest",
            "context": {
                "session_id": "sess_12345",
                "player_id": "player_67890",
                "world_state": {"location": "forest_entrance", "time": "dawn"},
                "history": [f"event_{i}" for i in range(20)],
            },
        },
        "metadata": {"timestamp": time.time(), "ttl": 300, "priority": "normal"},
    }

    # JSON serialize
    times = []
    for _ in range(1000):
        start = time.perf_counter()
        for _ in range(100):
            json.dumps(sample_message)
        elapsed = time.perf_counter() - start
        times.append(elapsed)

    results.append(
        BenchmarkResult(
            name="json_serialize_100x",
            category="serialization",
            iterations=1000,
            times=times,
        )
    )

    # JSON deserialize
    serialized = json.dumps(sample_message)
    times = []
    for _ in range(1000):
        start = time.perf_counter()
        for _ in range(100):
            json.loads(serialized)
        elapsed = time.perf_counter() - start
        times.append(elapsed)

    results.append(
        BenchmarkResult(
            name="json_deserialize_100x",
            category="serialization",
            iterations=1000,
            times=times,
        )
    )

    return results


def benchmark_async_overhead() -> list[BenchmarkResult]:
    """Benchmark asyncio overhead patterns used in agent orchestration."""
    results = []

    async def _run_single():
        """Single coroutine for overhead measurement."""
        pass

    async def _run_gather(n: int):
        """Gather n coroutines."""

        async def _noop():
            pass

        await asyncio.gather(*[_noop() for _ in range(n)])

    # Single coroutine creation + execution
    times = []
    loop = asyncio.new_event_loop()
    try:
        for _ in range(500):
            start = time.perf_counter()
            loop.run_until_complete(_run_single())
            elapsed = time.perf_counter() - start
            times.append(elapsed)
    finally:
        loop.close()

    results.append(
        BenchmarkResult(
            name="asyncio_run_single",
            category="async_overhead",
            iterations=500,
            times=times,
        )
    )

    # Gather 50 coroutines (simulates concurrent agent calls)
    times = []
    loop = asyncio.new_event_loop()
    try:
        for _ in range(100):
            start = time.perf_counter()
            loop.run_until_complete(_run_gather(50))
            elapsed = time.perf_counter() - start
            times.append(elapsed)
    finally:
        loop.close()

    results.append(
        BenchmarkResult(
            name="asyncio_gather_50",
            category="async_overhead",
            iterations=100,
            times=times,
        )
    )

    return results


def benchmark_memory_usage() -> list[BenchmarkResult]:
    """Benchmark memory allocation patterns."""
    import resource

    results = []

    # Measure RSS before and after allocating many objects
    gc.collect()
    rss_before = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss

    # Simulate agent message queue (10k messages)
    messages = []
    start = time.perf_counter()
    for i in range(10000):
        messages.append(
            {
                "id": i,
                "sender": f"agent_{i % 3}",
                "content": f"message content {i}",
                "metadata": {"timestamp": time.time()},
            }
        )
    elapsed = time.perf_counter() - start

    rss_after = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    memory_delta_kb = rss_after - rss_before

    results.append(
        BenchmarkResult(
            name="allocate_10k_messages",
            category="memory",
            iterations=1,
            times=[elapsed],
        )
    )

    results.append(
        BenchmarkResult(
            name="memory_delta_10k_messages_kb",
            category="memory",
            iterations=1,
            times=[float(memory_delta_kb)],
            unit="kilobytes",
        )
    )

    # Cleanup
    del messages
    gc.collect()

    return results


def benchmark_string_processing() -> list[BenchmarkResult]:
    """Benchmark string operations common in narrative processing."""
    results = []

    # Simulate narrative text processing
    narrative_text = (
        "The ancient forest stretched before you, its towering trees "
        "casting long shadows across the moss-covered path. "
    ) * 50  # ~8KB of text

    # String concatenation
    times = []
    for _ in range(500):
        start = time.perf_counter()
        parts = narrative_text.split(" ")
        result = " ".join(parts)
        _ = result.lower()
        _ = result.upper()
        _ = result.replace("forest", "woodland")
        elapsed = time.perf_counter() - start
        times.append(elapsed)

    results.append(
        BenchmarkResult(
            name="narrative_text_processing",
            category="string_ops",
            iterations=500,
            times=times,
        )
    )

    # f-string formatting (common in prompts)
    times = []
    for _ in range(1000):
        start = time.perf_counter()
        for _ in range(100):
            f"Player {42} is at location {'forest'} with health {100}"
        elapsed = time.perf_counter() - start
        times.append(elapsed)

    results.append(
        BenchmarkResult(
            name="fstring_formatting_100x",
            category="string_ops",
            iterations=1000,
            times=times,
        )
    )

    return results


def run_all_benchmarks() -> dict:
    """Run all benchmark suites and return results."""
    print(f"Python {sys.version}")
    print(f"Platform: {sys.platform}")
    print("=" * 60)
    print("Running TTA Python 3.14 Baseline Benchmarks")
    print("=" * 60)

    all_results = []

    suites = [
        ("Import Times", benchmark_import_times),
        ("Object Creation", benchmark_object_creation),
        ("Serialization", benchmark_serialization),
        ("Async Overhead", benchmark_async_overhead),
        ("Memory Usage", benchmark_memory_usage),
        ("String Processing", benchmark_string_processing),
    ]

    for suite_name, suite_func in suites:
        print(f"\n▶ {suite_name}...")
        try:
            results = suite_func()
            all_results.extend(results)
            for r in results:
                if r.unit == "kilobytes":
                    print(f"  {r.name}: {r.mean:.1f} KB")
                else:
                    print(f"  {r.name}: mean={r.mean:.6f}s p95={r.p95:.6f}s")
        except Exception as e:
            print(f"  ⚠ {suite_name} failed: {e}")

    # Summary
    report = {
        "python_version": sys.version,
        "platform": sys.platform,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "benchmarks": [r.to_dict() for r in all_results],
    }

    print("\n" + "=" * 60)
    print(f"Completed {len(all_results)} benchmarks")
    print("=" * 60)

    return report


def main():
    parser = argparse.ArgumentParser(
        description="TTA Python 3.14 Baseline Benchmark Collection"
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output JSON file path (default: print to stdout)",
    )
    args = parser.parse_args()

    report = run_all_benchmarks()

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(report, f, indent=2)
        print(f"\nResults saved to {output_path}")
    else:
        print("\n--- JSON Report ---")
        print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
