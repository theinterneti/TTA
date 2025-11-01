"""
Development Metrics Dashboard Generator

Generates HTML dashboard with visualizations for development metrics.

Usage:
    from observability.dashboard import generate_dashboard

    generate_dashboard(output_file="dev_metrics_dashboard.html")
"""

from datetime import datetime
from pathlib import Path
from typing import Any

try:
    import matplotlib

    matplotlib.use("Agg")  # Non-interactive backend
    import matplotlib.pyplot as plt

    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("WARNING: matplotlib not available, dashboard will have no charts")

from .dev_metrics import DevMetricsCollector


def generate_dashboard(
    output_file: str = "dev_metrics_dashboard.html",
    days: int = 30,
    metrics_dir: str = ".metrics",
) -> None:
    """
    Generate HTML dashboard for development metrics.

    Args:
        output_file: Path to output HTML file
        days: Number of days of metrics to include
        metrics_dir: Directory containing metrics files
    """
    collector = DevMetricsCollector(metrics_dir=metrics_dir)
    summary = collector.get_metrics_summary(days=days)

    if not summary:
        print(f"No metrics found in {metrics_dir}")
        _generate_empty_dashboard(output_file)
        return

    # Generate visualizations if matplotlib available
    chart_html = ""
    if MATPLOTLIB_AVAILABLE:
        chart_path = _generate_charts(summary, output_file)
        if chart_path:
            chart_html = f'<img src="{chart_path}" alt="Metrics Visualization" style="max-width: 100%;">'

    # Generate HTML
    html = _generate_html(summary, chart_html, days)

    # Write to file
    output_path = Path(output_file)
    output_path.write_text(html)

    print(f"Dashboard generated: {output_file}")


def _generate_charts(summary: dict[str, Any], output_file: str) -> str | None:
    """Generate matplotlib charts for metrics."""
    if not summary:
        return None

    try:
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))

        names = list(summary.keys())

        # 1. Success rates
        success_rates = [summary[n]["success_rate"] * 100 for n in names]
        axes[0, 0].barh(names, success_rates, color="#4CAF50")
        axes[0, 0].set_xlabel("Success Rate (%)")
        axes[0, 0].set_title("Success Rates by Operation")
        axes[0, 0].set_xlim(0, 100)

        # 2. Average durations
        avg_durations = [
            summary[n]["avg_duration_ms"] / 1000 for n in names
        ]  # Convert to seconds
        axes[0, 1].barh(names, avg_durations, color="#2196F3")
        axes[0, 1].set_xlabel("Duration (seconds)")
        axes[0, 1].set_title("Average Execution Times")

        # 3. Execution counts
        exec_counts = [summary[n]["total_executions"] for n in names]
        axes[1, 0].barh(names, exec_counts, color="#FF9800")
        axes[1, 0].set_xlabel("Count")
        axes[1, 0].set_title("Total Executions")

        # 4. Failure counts
        failure_counts = [summary[n]["failures"] for n in names]
        axes[1, 1].barh(names, failure_counts, color="#F44336")
        axes[1, 1].set_xlabel("Count")
        axes[1, 1].set_title("Failures")

        plt.tight_layout()

        # Save chart
        chart_path = Path(output_file).parent / "dev_metrics_chart.png"
        plt.savefig(chart_path, dpi=100, bbox_inches="tight")
        plt.close()

        return chart_path.name
    except Exception as e:
        print(f"Failed to generate charts: {e}")
        return None


def _generate_html(summary: dict[str, Any], chart_html: str, days: int) -> str:
    """Generate HTML content for dashboard."""

    # Generate metrics cards
    metrics_html = ""
    for name, metrics in sorted(summary.items()):
        status_color = (
            "#4CAF50"
            if metrics["success_rate"] > 0.9
            else "#FF9800"
            if metrics["success_rate"] > 0.7
            else "#F44336"
        )

        metrics_html += f"""
        <div class="metric-card">
            <h3>{name}</h3>
            <div class="metric-grid">
                <div class="metric-item">
                    <div class="metric-label">Total Executions</div>
                    <div class="metric-value">{metrics["total_executions"]}</div>
                </div>
                <div class="metric-item">
                    <div class="metric-label">Success Rate</div>
                    <div class="metric-value" style="color: {status_color}">
                        {metrics["success_rate"]:.1%}
                    </div>
                </div>
                <div class="metric-item">
                    <div class="metric-label">Avg Duration</div>
                    <div class="metric-value">{metrics["avg_duration_ms"]:.0f}ms</div>
                </div>
                <div class="metric-item">
                    <div class="metric-label">Min / Max Duration</div>
                    <div class="metric-value">{metrics["min_duration_ms"]:.0f}ms / {metrics["max_duration_ms"]:.0f}ms</div>
                </div>
                <div class="metric-item">
                    <div class="metric-label">Successes</div>
                    <div class="metric-value" style="color: #4CAF50">{metrics["successes"]}</div>
                </div>
                <div class="metric-item">
                    <div class="metric-label">Failures</div>
                    <div class="metric-value" style="color: #F44336">{metrics["failures"]}</div>
                </div>
            </div>
        </div>
        """

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>TTA Development Metrics Dashboard</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                background: #f5f5f5;
                padding: 20px;
                line-height: 1.6;
            }}
            .container {{
                max-width: 1400px;
                margin: 0 auto;
                background: white;
                padding: 30px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            h1 {{
                color: #333;
                margin-bottom: 10px;
                font-size: 2em;
            }}
            .timestamp {{
                color: #666;
                font-size: 0.9em;
                margin-bottom: 30px;
            }}
            .chart-container {{
                margin: 30px 0;
                text-align: center;
            }}
            .metrics-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
                gap: 20px;
                margin-top: 30px;
            }}
            .metric-card {{
                background: #fafafa;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 20px;
            }}
            .metric-card h3 {{
                color: #333;
                margin-bottom: 15px;
                font-size: 1.2em;
                border-bottom: 2px solid #2196F3;
                padding-bottom: 10px;
            }}
            .metric-grid {{
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 15px;
            }}
            .metric-item {{
                background: white;
                padding: 12px;
                border-radius: 4px;
                border: 1px solid #e0e0e0;
            }}
            .metric-label {{
                font-size: 0.85em;
                color: #666;
                margin-bottom: 5px;
            }}
            .metric-value {{
                font-size: 1.5em;
                font-weight: bold;
                color: #333;
            }}
            .footer {{
                margin-top: 40px;
                padding-top: 20px;
                border-top: 1px solid #e0e0e0;
                text-align: center;
                color: #666;
                font-size: 0.9em;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 TTA Development Metrics Dashboard</h1>
            <div class="timestamp">
                Generated: {datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")} |
                Period: Last {days} days
            </div>

            {f'<div class="chart-container">{chart_html}</div>' if chart_html else ""}

            <h2 style="margin-top: 30px; color: #333;">Detailed Metrics</h2>
            <div class="metrics-grid">
                {metrics_html}
            </div>

            <div class="footer">
                TTA Development Metrics Dashboard |
                Auto-generated from .metrics/ directory
            </div>
        </div>
    </body>
    </html>
    """

    return html


def _generate_empty_dashboard(output_file: str) -> None:
    """Generate empty dashboard when no metrics available."""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>TTA Development Metrics Dashboard</title>
        <style>
            body { font-family: Arial, sans-serif; padding: 40px; text-align: center; }
            .empty-state { color: #666; }
        </style>
    </head>
    <body>
        <h1>TTA Development Metrics Dashboard</h1>
        <div class="empty-state">
            <p>No metrics available yet.</p>
            <p>Run development operations with @track_execution decorator to collect metrics.</p>
        </div>
    </body>
    </html>
    """

    Path(output_file).write_text(html)
    print(f"Empty dashboard generated: {output_file}")


if __name__ == "__main__":
    generate_dashboard()
