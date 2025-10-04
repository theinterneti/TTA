#!/usr/bin/env python3
"""
TTA Analytics Demonstration Script
Shows current data visualization and analytics capabilities
"""

import asyncio
import json
import os
import requests
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any
import seaborn as sns

class TTAAnalyticsDemo:
    """Demonstrate TTA's current analytics capabilities"""
    
    def __init__(self):
        self.api_url = "http://localhost:3004"
        self.prometheus_url = "http://localhost:9091"
        self.grafana_url = "http://localhost:3003"
        
    def get_system_metrics(self) -> Dict:
        """Get system-level metrics from Prometheus"""
        try:
            # Query Prometheus for system metrics
            queries = {
                "service_health": "up",
                "http_requests": "tta_http_requests_total",
                "response_times": "tta_http_request_duration_seconds",
                "user_sessions": "tta_user_sessions_total"
            }
            
            metrics = {}
            for metric_name, query in queries.items():
                response = requests.get(
                    f"{self.prometheus_url}/api/v1/query",
                    params={"query": query},
                    timeout=5
                )
                if response.status_code == 200:
                    data = response.json()
                    metrics[metric_name] = data.get("data", {}).get("result", [])
                else:
                    metrics[metric_name] = []
                    
            return metrics
        except Exception as e:
            print(f"Error getting system metrics: {e}")
            return {}
    
    def get_user_progress_data(self, user_id: str, token: str) -> Dict:
        """Get user progress data from API"""
        try:
            headers = {"Authorization": f"Bearer {token}"}
            
            # Get basic progress
            progress_response = requests.get(
                f"{self.api_url}/api/v1/players/{user_id}/progress",
                headers=headers,
                timeout=5
            )
            
            # Get visualization data
            viz_response = requests.get(
                f"{self.api_url}/api/v1/players/{user_id}/progress/viz?days=14",
                headers=headers,
                timeout=5
            )
            
            # Get dashboard data
            dashboard_response = requests.get(
                f"{self.api_url}/api/v1/players/{user_id}/dashboard",
                headers=headers,
                timeout=5
            )
            
            return {
                "progress": progress_response.json() if progress_response.status_code == 200 else {},
                "visualization": viz_response.json() if viz_response.status_code == 200 else {},
                "dashboard": dashboard_response.json() if dashboard_response.status_code == 200 else {}
            }
        except Exception as e:
            print(f"Error getting user progress data: {e}")
            return {}
    
    def create_system_health_visualization(self, metrics: Dict):
        """Create system health visualization"""
        try:
            # Extract service health data
            health_data = metrics.get("service_health", [])
            
            if not health_data:
                print("No health data available for visualization")
                return
            
            services = []
            statuses = []
            
            for metric in health_data:
                service_name = metric.get("metric", {}).get("service", "unknown")
                status = float(metric.get("value", [0, "0"])[1])
                services.append(service_name)
                statuses.append("UP" if status == 1 else "DOWN")
            
            # Create visualization
            plt.figure(figsize=(12, 6))
            
            # Service health status
            plt.subplot(1, 2, 1)
            status_counts = pd.Series(statuses).value_counts()
            colors = ['green' if status == 'UP' else 'red' for status in status_counts.index]
            plt.pie(status_counts.values, labels=status_counts.index, colors=colors, autopct='%1.1f%%')
            plt.title('TTA System Health Status')
            
            # Service details
            plt.subplot(1, 2, 2)
            service_df = pd.DataFrame({'Service': services, 'Status': statuses})
            service_counts = service_df.groupby(['Service', 'Status']).size().unstack(fill_value=0)
            service_counts.plot(kind='bar', stacked=True, color=['red', 'green'])
            plt.title('Service Status by Component')
            plt.xticks(rotation=45)
            plt.legend(['DOWN', 'UP'])
            
            plt.tight_layout()
            plt.savefig('tta_system_health.png', dpi=300, bbox_inches='tight')
            plt.show()
            
        except Exception as e:
            print(f"Error creating system health visualization: {e}")
    
    def create_user_progress_visualization(self, user_data: Dict):
        """Create user progress visualization"""
        try:
            viz_data = user_data.get("visualization", {})
            
            if not viz_data.get("time_buckets"):
                print("No user progress data available for visualization")
                return
            
            # Extract data
            time_buckets = viz_data["time_buckets"]
            sessions = viz_data["series"]["sessions"]
            duration_minutes = viz_data["series"]["duration_minutes"]
            
            # Convert to pandas DataFrame
            df = pd.DataFrame({
                'Date': pd.to_datetime(time_buckets),
                'Sessions': sessions,
                'Duration (minutes)': duration_minutes
            })
            
            # Create visualization
            plt.figure(figsize=(14, 8))
            
            # Session count over time
            plt.subplot(2, 2, 1)
            plt.plot(df['Date'], df['Sessions'], marker='o', linewidth=2, markersize=6)
            plt.title('Daily Session Count')
            plt.xlabel('Date')
            plt.ylabel('Number of Sessions')
            plt.xticks(rotation=45)
            plt.grid(True, alpha=0.3)
            
            # Duration over time
            plt.subplot(2, 2, 2)
            plt.plot(df['Date'], df['Duration (minutes)'], marker='s', color='orange', linewidth=2, markersize=6)
            plt.title('Daily Session Duration')
            plt.xlabel('Date')
            plt.ylabel('Duration (minutes)')
            plt.xticks(rotation=45)
            plt.grid(True, alpha=0.3)
            
            # Summary statistics
            plt.subplot(2, 2, 3)
            summary_stats = {
                'Total Sessions': df['Sessions'].sum(),
                'Total Duration': df['Duration (minutes)'].sum(),
                'Avg Session Length': df['Duration (minutes)'].mean() if df['Sessions'].sum() > 0 else 0,
                'Active Days': (df['Sessions'] > 0).sum()
            }
            
            bars = plt.bar(range(len(summary_stats)), list(summary_stats.values()))
            plt.xticks(range(len(summary_stats)), list(summary_stats.keys()), rotation=45)
            plt.title('User Progress Summary')
            
            # Add value labels on bars
            for bar, value in zip(bars, summary_stats.values()):
                plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                        f'{value:.1f}', ha='center', va='bottom')
            
            # Progress trend analysis
            plt.subplot(2, 2, 4)
            # Calculate 7-day moving average
            df['Sessions_MA'] = df['Sessions'].rolling(window=7, center=True).mean()
            plt.plot(df['Date'], df['Sessions'], alpha=0.3, label='Daily Sessions')
            plt.plot(df['Date'], df['Sessions_MA'], linewidth=2, label='7-day Moving Average')
            plt.title('Session Trend Analysis')
            plt.xlabel('Date')
            plt.ylabel('Sessions')
            plt.legend()
            plt.xticks(rotation=45)
            plt.grid(True, alpha=0.3)
            
            plt.tight_layout()
            plt.savefig('tta_user_progress.png', dpi=300, bbox_inches='tight')
            plt.show()
            
        except Exception as e:
            print(f"Error creating user progress visualization: {e}")
    
    def generate_analytics_report(self, metrics: Dict, user_data: Dict) -> str:
        """Generate comprehensive analytics report"""
        report = []
        report.append("# TTA Analytics Report")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # System Health Summary
        report.append("## System Health Summary")
        health_data = metrics.get("service_health", [])
        if health_data:
            up_services = sum(1 for m in health_data if float(m.get("value", [0, "0"])[1]) == 1)
            total_services = len(health_data)
            health_percentage = (up_services / total_services * 100) if total_services > 0 else 0
            
            report.append(f"- **System Health**: {health_percentage:.1f}% ({up_services}/{total_services} services up)")
            report.append(f"- **Services Monitored**: {total_services}")
            report.append("")
            
            # List service statuses
            report.append("### Service Status Details")
            for metric in health_data:
                service = metric.get("metric", {}).get("service", "unknown")
                status = "UP" if float(metric.get("value", [0, "0"])[1]) == 1 else "DOWN"
                report.append(f"- **{service}**: {status}")
        else:
            report.append("- No system health data available")
        
        report.append("")
        
        # User Analytics Summary
        report.append("## User Analytics Summary")
        progress_data = user_data.get("progress", {})
        viz_data = user_data.get("visualization", {})
        
        if progress_data:
            report.append(f"- **Total Sessions**: {progress_data.get('total_sessions', 0)}")
            report.append(f"- **Total Time**: {progress_data.get('total_time_minutes', 0)} minutes")
            report.append(f"- **Milestones Achieved**: {progress_data.get('milestones_achieved', 0)}")
        
        if viz_data and viz_data.get("series"):
            sessions = viz_data["series"]["sessions"]
            duration = viz_data["series"]["duration_minutes"]
            active_days = sum(1 for s in sessions if s > 0)
            total_sessions = sum(sessions)
            total_duration = sum(duration)
            
            report.append(f"- **Active Days (14-day period)**: {active_days}")
            report.append(f"- **Recent Sessions**: {total_sessions}")
            report.append(f"- **Recent Duration**: {total_duration:.1f} minutes")
        
        report.append("")
        
        # Recommendations
        report.append("## Recommendations")
        if health_data:
            down_services = [m.get("metric", {}).get("service", "unknown") 
                           for m in health_data if float(m.get("value", [0, "0"])[1]) == 0]
            if down_services:
                report.append("### System Health")
                report.append("- **Action Required**: The following services are down:")
                for service in down_services:
                    report.append(f"  - {service}")
                report.append("- Consider investigating and restarting these services")
        
        if viz_data and viz_data.get("series"):
            sessions = viz_data["series"]["sessions"]
            if sum(sessions) == 0:
                report.append("### User Engagement")
                report.append("- **Low Activity**: No recent user sessions detected")
                report.append("- Consider user engagement strategies or system promotion")
        
        return "\n".join(report)
    
    async def run_demo(self):
        """Run the complete analytics demonstration"""
        print("🚀 Starting TTA Analytics Demonstration")
        print("=" * 50)
        
        # Get system metrics
        print("📊 Fetching system metrics from Prometheus...")
        metrics = self.get_system_metrics()

        # Test user (from environment variables for security)
        user_id = os.getenv("TEST_USER_ID", "a809f576-4382-4cf3-ae1b-206710a25112")
        token = os.getenv("TEST_JWT_TOKEN")

        if not token:
            print("⚠️  WARNING: TEST_JWT_TOKEN environment variable not set")
            print("   Skipping user analytics data retrieval")
            token = None
        
        # Get user analytics
        print("👤 Fetching user analytics data...")
        user_data = self.get_user_progress_data(user_id, token)
        
        # Create visualizations
        print("📈 Creating system health visualization...")
        self.create_system_health_visualization(metrics)
        
        print("📊 Creating user progress visualization...")
        self.create_user_progress_visualization(user_data)
        
        # Generate report
        print("📋 Generating analytics report...")
        report = self.generate_analytics_report(metrics, user_data)
        
        # Save report
        with open("tta_analytics_report.md", "w") as f:
            f.write(report)
        
        print("\n✅ Analytics demonstration complete!")
        print("📁 Generated files:")
        print("   - tta_system_health.png")
        print("   - tta_user_progress.png") 
        print("   - tta_analytics_report.md")
        
        # Print summary
        print("\n📊 Summary:")
        health_data = metrics.get("service_health", [])
        if health_data:
            up_services = sum(1 for m in health_data if float(m.get("value", [0, "0"])[1]) == 1)
            total_services = len(health_data)
            print(f"   System Health: {up_services}/{total_services} services up")
        
        progress_data = user_data.get("progress", {})
        if progress_data:
            print(f"   User Sessions: {progress_data.get('total_sessions', 0)}")
            print(f"   User Time: {progress_data.get('total_time_minutes', 0)} minutes")


if __name__ == "__main__":
    # Install required packages if not available
    try:
        import matplotlib.pyplot as plt
        import pandas as pd
        import seaborn as sns
    except ImportError:
        print("Installing required packages...")
        import subprocess
        subprocess.check_call(["pip", "install", "matplotlib", "pandas", "seaborn"])
        import matplotlib.pyplot as plt
        import pandas as pd
        import seaborn as sns
    
    demo = TTAAnalyticsDemo()
    asyncio.run(demo.run_demo())
