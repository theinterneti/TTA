"""
Advanced Reporting Service for TTA Analytics

This service provides automated report generation, trend analysis, and
therapeutic outcome tracking with customizable dashboards.
"""

import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import uuid4

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from fastapi import BackgroundTasks, FastAPI, HTTPException
from jinja2 import Template
from plotly.utils import PlotlyJSONEncoder
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ReportType(str, Enum):
    """Types of reports that can be generated."""

    THERAPEUTIC_OUTCOMES = "therapeutic_outcomes"
    USER_ENGAGEMENT = "user_engagement"
    SYSTEM_PERFORMANCE = "system_performance"
    COHORT_ANALYSIS = "cohort_analysis"
    TREND_ANALYSIS = "trend_analysis"
    CUSTOM_DASHBOARD = "custom_dashboard"


class ReportFormat(str, Enum):
    """Output formats for reports."""

    JSON = "json"
    HTML = "html"
    PDF = "pdf"
    EXCEL = "excel"


@dataclass
class ReportConfiguration:
    """Configuration for report generation."""

    report_id: str
    report_type: ReportType
    report_format: ReportFormat
    title: str
    description: str
    date_range_start: datetime
    date_range_end: datetime
    filters: dict[str, Any]
    visualization_config: dict[str, Any]
    created_at: datetime

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        data["created_at"] = self.created_at.isoformat()
        data["date_range_start"] = self.date_range_start.isoformat()
        data["date_range_end"] = self.date_range_end.isoformat()
        return data


@dataclass
class GeneratedReport:
    """Represents a generated report."""

    report_id: str
    configuration: ReportConfiguration
    content: dict[str, Any]
    visualizations: list[dict[str, Any]]
    generated_at: datetime
    file_path: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "report_id": self.report_id,
            "configuration": self.configuration.to_dict(),
            "content": self.content,
            "visualizations": self.visualizations,
            "generated_at": self.generated_at.isoformat(),
            "file_path": self.file_path,
        }


class TrendAnalyzer:
    """Analyzes trends in therapeutic and system data."""

    def __init__(self):
        self.trend_cache = {}

    def analyze_engagement_trends(
        self, engagement_data: list[dict[str, Any]], time_period: str = "daily"
    ) -> dict[str, Any]:
        """Analyze user engagement trends over time."""
        if not engagement_data:
            return {
                "trend": "no_data",
                "analysis": "Insufficient data for trend analysis",
            }

        # Convert to DataFrame for easier analysis
        df = pd.DataFrame(engagement_data)
        df["date"] = pd.to_datetime(df["created_at"])

        # Group by time period
        if time_period == "daily":
            df_grouped = (
                df.groupby(df["date"].dt.date)
                .agg(
                    {
                        "engagement_score": ["mean", "count"],
                        "session_duration": "mean",
                        "interaction_count": "mean",
                    }
                )
                .reset_index()
            )
        elif time_period == "weekly":
            df_grouped = (
                df.groupby(df["date"].dt.to_period("W"))
                .agg(
                    {
                        "engagement_score": ["mean", "count"],
                        "session_duration": "mean",
                        "interaction_count": "mean",
                    }
                )
                .reset_index()
            )
        else:  # monthly
            df_grouped = (
                df.groupby(df["date"].dt.to_period("M"))
                .agg(
                    {
                        "engagement_score": ["mean", "count"],
                        "session_duration": "mean",
                        "interaction_count": "mean",
                    }
                )
                .reset_index()
            )

        # Calculate trend direction
        engagement_scores = df_grouped[("engagement_score", "mean")].values
        if len(engagement_scores) < 2:
            trend_direction = "insufficient_data"
        else:
            # Simple linear trend calculation
            x = np.arange(len(engagement_scores))
            slope = np.polyfit(x, engagement_scores, 1)[0]

            if slope > 0.01:
                trend_direction = "increasing"
            elif slope < -0.01:
                trend_direction = "decreasing"
            else:
                trend_direction = "stable"

        return {
            "trend": trend_direction,
            "slope": float(slope) if len(engagement_scores) >= 2 else 0.0,
            "avg_engagement": float(np.mean(engagement_scores)),
            "data_points": len(engagement_scores),
            "analysis": f"Engagement trend is {trend_direction} over {time_period} periods",
            "time_series_data": df_grouped.to_dict("records"),
        }

    def analyze_therapeutic_outcome_trends(
        self, outcome_data: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Analyze therapeutic outcome trends."""
        if not outcome_data:
            return {
                "trend": "no_data",
                "analysis": "No therapeutic outcome data available",
            }

        df = pd.DataFrame(outcome_data)
        df["date"] = pd.to_datetime(df["created_at"])

        # Analyze success rates over time
        df["success"] = df["outcome_category"].isin(["positive", "excellent", "good"])

        # Group by week for trend analysis
        weekly_outcomes = (
            df.groupby(df["date"].dt.to_period("W"))
            .agg(
                {
                    "success": ["mean", "count"],
                    "engagement_score": "mean",
                    "therapeutic_goals_achieved": "mean",
                }
            )
            .reset_index()
        )

        success_rates = weekly_outcomes[("success", "mean")].values

        if len(success_rates) < 2:
            trend_direction = "insufficient_data"
            slope = 0.0
        else:
            x = np.arange(len(success_rates))
            slope = np.polyfit(x, success_rates, 1)[0]

            if slope > 0.05:
                trend_direction = "improving"
            elif slope < -0.05:
                trend_direction = "declining"
            else:
                trend_direction = "stable"

        return {
            "trend": trend_direction,
            "slope": float(slope),
            "avg_success_rate": float(np.mean(success_rates)),
            "total_outcomes": len(outcome_data),
            "analysis": f"Therapeutic outcomes are {trend_direction}",
            "weekly_data": weekly_outcomes.to_dict("records"),
        }


class VisualizationGenerator:
    """Generates visualizations for reports."""

    def create_engagement_chart(
        self, engagement_data: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Create engagement trend chart."""
        if not engagement_data:
            return {"error": "No data available for visualization"}

        df = pd.DataFrame(engagement_data)
        df["date"] = pd.to_datetime(df["created_at"])

        # Create time series chart
        fig = px.line(
            df,
            x="date",
            y="engagement_score",
            title="User Engagement Trends Over Time",
            labels={"engagement_score": "Engagement Score", "date": "Date"},
        )

        fig.update_layout(
            xaxis_title="Date", yaxis_title="Engagement Score", hovermode="x unified"
        )

        return {
            "chart_type": "line",
            "title": "User Engagement Trends",
            "plotly_json": json.loads(json.dumps(fig, cls=PlotlyJSONEncoder)),
        }

    def create_outcome_distribution_chart(
        self, outcome_data: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Create therapeutic outcome distribution chart."""
        if not outcome_data:
            return {"error": "No outcome data available"}

        df = pd.DataFrame(outcome_data)
        outcome_counts = df["outcome_category"].value_counts()

        fig = px.pie(
            values=outcome_counts.values,
            names=outcome_counts.index,
            title="Therapeutic Outcome Distribution",
        )

        return {
            "chart_type": "pie",
            "title": "Therapeutic Outcome Distribution",
            "plotly_json": json.loads(json.dumps(fig, cls=PlotlyJSONEncoder)),
        }

    def create_cohort_comparison_chart(
        self, cohort_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Create cohort comparison chart."""
        if not cohort_data:
            return {"error": "No cohort data available"}

        cohorts = list(cohort_data.keys())
        success_rates = [cohort_data[c].get("success_rate", 0) for c in cohorts]
        engagement_scores = [cohort_data[c].get("avg_engagement", 0) for c in cohorts]

        fig = go.Figure()

        fig.add_trace(
            go.Bar(name="Success Rate", x=cohorts, y=success_rates, yaxis="y")
        )

        fig.add_trace(
            go.Scatter(
                name="Avg Engagement",
                x=cohorts,
                y=engagement_scores,
                yaxis="y2",
                mode="lines+markers",
            )
        )

        fig.update_layout(
            title="Cohort Performance Comparison",
            xaxis_title="Cohorts",
            yaxis={"title": "Success Rate", "side": "left"},
            yaxis2={"title": "Engagement Score", "side": "right", "overlaying": "y"},
            hovermode="x unified",
        )

        return {
            "chart_type": "combo",
            "title": "Cohort Performance Comparison",
            "plotly_json": json.loads(json.dumps(fig, cls=PlotlyJSONEncoder)),
        }


class ReportGenerator:
    """Main report generation service."""

    def __init__(self):
        self.trend_analyzer = TrendAnalyzer()
        self.viz_generator = VisualizationGenerator()
        self.generated_reports: dict[str, GeneratedReport] = {}

        # HTML template for reports
        self.html_template = Template(
            """
        <!DOCTYPE html>
        <html>
        <head>
            <title>{{ title }}</title>
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .header { border-bottom: 2px solid #333; padding-bottom: 20px; }
                .section { margin: 30px 0; }
                .metric { display: inline-block; margin: 10px 20px; padding: 15px;
                         border: 1px solid #ddd; border-radius: 5px; }
                .chart { margin: 20px 0; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{{ title }}</h1>
                <p>{{ description }}</p>
                <p><strong>Generated:</strong> {{ generated_at }}</p>
                <p><strong>Period:</strong> {{ date_range_start }} to {{ date_range_end }}</p>
            </div>

            <div class="section">
                <h2>Key Metrics</h2>
                {% for metric in key_metrics %}
                <div class="metric">
                    <h3>{{ metric.name }}</h3>
                    <p><strong>{{ metric.value }}</strong></p>
                    <p>{{ metric.description }}</p>
                </div>
                {% endfor %}
            </div>

            <div class="section">
                <h2>Trend Analysis</h2>
                <p>{{ trend_analysis.analysis }}</p>
            </div>

            <div class="section">
                <h2>Visualizations</h2>
                {% for viz in visualizations %}
                <div class="chart">
                    <h3>{{ viz.title }}</h3>
                    <div id="chart-{{ loop.index }}"></div>
                    <script>
                        Plotly.newPlot('chart-{{ loop.index }}', {{ viz.plotly_json | safe }});
                    </script>
                </div>
                {% endfor %}
            </div>
        </body>
        </html>
        """
        )

    async def generate_therapeutic_outcomes_report(
        self, config: ReportConfiguration, data: dict[str, Any]
    ) -> GeneratedReport:
        """Generate therapeutic outcomes report."""
        outcome_data = data.get("outcomes", [])

        # Analyze trends
        trend_analysis = self.trend_analyzer.analyze_therapeutic_outcome_trends(
            outcome_data
        )

        # Generate visualizations
        visualizations = []
        if outcome_data:
            outcome_chart = self.viz_generator.create_outcome_distribution_chart(
                outcome_data
            )
            visualizations.append(outcome_chart)

        # Calculate key metrics
        total_outcomes = len(outcome_data)
        success_count = sum(
            1
            for o in outcome_data
            if o.get("outcome_category") in ["positive", "excellent", "good"]
        )
        success_rate = success_count / total_outcomes if total_outcomes > 0 else 0
        avg_engagement = (
            np.mean([o.get("engagement_score", 0) for o in outcome_data])
            if outcome_data
            else 0
        )

        key_metrics = [
            {
                "name": "Total Outcomes",
                "value": total_outcomes,
                "description": "Total therapeutic outcomes analyzed",
            },
            {
                "name": "Success Rate",
                "value": f"{success_rate:.1%}",
                "description": "Percentage of positive outcomes",
            },
            {
                "name": "Avg Engagement",
                "value": f"{avg_engagement:.2f}",
                "description": "Average user engagement score",
            },
        ]

        content = {
            "key_metrics": key_metrics,
            "trend_analysis": trend_analysis,
            "total_outcomes": total_outcomes,
            "success_rate": success_rate,
            "avg_engagement": avg_engagement,
        }

        return GeneratedReport(
            report_id=config.report_id,
            configuration=config,
            content=content,
            visualizations=visualizations,
            generated_at=datetime.utcnow(),
        )

    async def generate_user_engagement_report(
        self, config: ReportConfiguration, data: dict[str, Any]
    ) -> GeneratedReport:
        """Generate user engagement report."""
        engagement_data = data.get("engagement", [])

        # Analyze trends
        trend_analysis = self.trend_analyzer.analyze_engagement_trends(engagement_data)

        # Generate visualizations
        visualizations = []
        if engagement_data:
            engagement_chart = self.viz_generator.create_engagement_chart(
                engagement_data
            )
            visualizations.append(engagement_chart)

        # Calculate key metrics
        total_sessions = len(engagement_data)
        avg_engagement = (
            np.mean([e.get("engagement_score", 0) for e in engagement_data])
            if engagement_data
            else 0
        )
        avg_duration = (
            np.mean([e.get("session_duration", 0) for e in engagement_data])
            if engagement_data
            else 0
        )

        key_metrics = [
            {
                "name": "Total Sessions",
                "value": total_sessions,
                "description": "Total user sessions analyzed",
            },
            {
                "name": "Avg Engagement",
                "value": f"{avg_engagement:.2f}",
                "description": "Average engagement score",
            },
            {
                "name": "Avg Duration",
                "value": f"{avg_duration:.1f} min",
                "description": "Average session duration",
            },
        ]

        content = {
            "key_metrics": key_metrics,
            "trend_analysis": trend_analysis,
            "total_sessions": total_sessions,
            "avg_engagement": avg_engagement,
            "avg_duration": avg_duration,
        }

        return GeneratedReport(
            report_id=config.report_id,
            configuration=config,
            content=content,
            visualizations=visualizations,
            generated_at=datetime.utcnow(),
        )

    async def generate_cohort_analysis_report(
        self, config: ReportConfiguration, data: dict[str, Any]
    ) -> GeneratedReport:
        """Generate cohort analysis report."""
        cohort_data = data.get("cohorts", {})

        # Generate visualizations
        visualizations = []
        if cohort_data:
            cohort_chart = self.viz_generator.create_cohort_comparison_chart(
                cohort_data
            )
            visualizations.append(cohort_chart)

        # Calculate key metrics
        total_cohorts = len(cohort_data)
        best_cohort = (
            max(cohort_data.keys(), key=lambda k: cohort_data[k].get("success_rate", 0))
            if cohort_data
            else "N/A"
        )
        avg_success_rate = (
            np.mean([c.get("success_rate", 0) for c in cohort_data.values()])
            if cohort_data
            else 0
        )

        key_metrics = [
            {
                "name": "Total Cohorts",
                "value": total_cohorts,
                "description": "Number of user cohorts analyzed",
            },
            {
                "name": "Best Performing",
                "value": best_cohort,
                "description": "Highest success rate cohort",
            },
            {
                "name": "Avg Success Rate",
                "value": f"{avg_success_rate:.1%}",
                "description": "Average success rate across cohorts",
            },
        ]

        content = {
            "key_metrics": key_metrics,
            "cohort_data": cohort_data,
            "total_cohorts": total_cohorts,
            "best_cohort": best_cohort,
            "avg_success_rate": avg_success_rate,
        }

        return GeneratedReport(
            report_id=config.report_id,
            configuration=config,
            content=content,
            visualizations=visualizations,
            generated_at=datetime.utcnow(),
        )

    async def generate_report(
        self, config: ReportConfiguration, data: dict[str, Any]
    ) -> GeneratedReport:
        """Generate report based on configuration."""
        try:
            if config.report_type == ReportType.THERAPEUTIC_OUTCOMES:
                report = await self.generate_therapeutic_outcomes_report(config, data)
            elif config.report_type == ReportType.USER_ENGAGEMENT:
                report = await self.generate_user_engagement_report(config, data)
            elif config.report_type == ReportType.COHORT_ANALYSIS:
                report = await self.generate_cohort_analysis_report(config, data)
            else:
                raise ValueError(f"Unsupported report type: {config.report_type}")

            # Store generated report
            self.generated_reports[report.report_id] = report

            return report

        except Exception as e:
            logger.error(f"Error generating report {config.report_id}: {e}")
            raise

    def render_html_report(self, report: GeneratedReport) -> str:
        """Render report as HTML."""
        return self.html_template.render(
            title=report.configuration.title,
            description=report.configuration.description,
            generated_at=report.generated_at.strftime("%Y-%m-%d %H:%M:%S"),
            date_range_start=report.configuration.date_range_start.strftime("%Y-%m-%d"),
            date_range_end=report.configuration.date_range_end.strftime("%Y-%m-%d"),
            key_metrics=report.content.get("key_metrics", []),
            trend_analysis=report.content.get("trend_analysis", {}),
            visualizations=report.visualizations,
        )


# FastAPI app for the reporting service
app = FastAPI(title="TTA Advanced Reporting Service", version="1.0.0")

# Global service instance
report_generator = ReportGenerator()


# API Models
class ReportRequest(BaseModel):
    """Request model for report generation."""

    report_type: ReportType
    report_format: ReportFormat = ReportFormat.JSON
    title: str
    description: str = ""
    date_range_start: datetime
    date_range_end: datetime
    filters: dict[str, Any] = Field(default_factory=dict)
    visualization_config: dict[str, Any] = Field(default_factory=dict)


class ReportResponse(BaseModel):
    """Response model for generated reports."""

    report_id: str
    status: str
    message: str
    report_url: str | None = None


@app.post("/reports/generate", response_model=ReportResponse)
async def generate_report(request: ReportRequest, background_tasks: BackgroundTasks):
    """Generate a new report."""
    try:
        report_id = str(uuid4())

        config = ReportConfiguration(
            report_id=report_id,
            report_type=request.report_type,
            report_format=request.report_format,
            title=request.title,
            description=request.description,
            date_range_start=request.date_range_start,
            date_range_end=request.date_range_end,
            filters=request.filters,
            visualization_config=request.visualization_config,
            created_at=datetime.utcnow(),
        )

        # Mock data for demonstration - in production, this would fetch from database
        mock_data = {
            "outcomes": [
                {
                    "outcome_category": "positive",
                    "engagement_score": 0.8,
                    "created_at": "2024-01-01",
                },
                {
                    "outcome_category": "excellent",
                    "engagement_score": 0.9,
                    "created_at": "2024-01-02",
                },
            ],
            "engagement": [
                {
                    "engagement_score": 0.75,
                    "session_duration": 25,
                    "created_at": "2024-01-01",
                },
                {
                    "engagement_score": 0.82,
                    "session_duration": 30,
                    "created_at": "2024-01-02",
                },
            ],
            "cohorts": {
                "high_engagement": {"success_rate": 0.85, "avg_engagement": 0.8},
                "medium_engagement": {"success_rate": 0.65, "avg_engagement": 0.6},
            },
        }

        # Generate report in background
        background_tasks.add_task(report_generator.generate_report, config, mock_data)

        return ReportResponse(
            report_id=report_id,
            status="generating",
            message="Report generation started",
            report_url=f"/reports/{report_id}",
        )

    except Exception as e:
        logger.error(f"Error starting report generation: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/reports/{report_id}")
async def get_report(report_id: str, format: str = "json"):
    """Get generated report."""
    if report_id not in report_generator.generated_reports:
        raise HTTPException(status_code=404, detail="Report not found")

    report = report_generator.generated_reports[report_id]

    if format.lower() == "html":
        html_content = report_generator.render_html_report(report)
        return {"content": html_content, "content_type": "text/html"}
    return report.to_dict()


@app.get("/reports")
async def list_reports():
    """List all generated reports."""
    reports = []
    for report in report_generator.generated_reports.values():
        reports.append(
            {
                "report_id": report.report_id,
                "title": report.configuration.title,
                "type": report.configuration.report_type,
                "generated_at": report.generated_at.isoformat(),
            }
        )

    return {"reports": reports, "total_count": len(reports)}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "advanced-reporting",
        "reports_generated": len(report_generator.generated_reports),
        "timestamp": datetime.utcnow().isoformat(),
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8096)
