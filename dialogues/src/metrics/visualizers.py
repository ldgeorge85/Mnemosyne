"""
Metrics Visualization Module

This module provides visualization capabilities for debate metrics, including:
- Quality metrics over time
- Agent performance comparisons
- Topic diversity visualizations
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

# Note: In a production environment, we would use matplotlib or another plotting library
# Since we're operating in a CLI environment, we'll use ASCII/text-based visualizations


class MetricsVisualizer:
    """Visualizer for debate metrics using text-based charts."""
    
    def __init__(self, memory_dir: str = "memory"):
        """Initialize the metrics visualizer.
        
        Args:
            memory_dir: Path to the memory directory
        """
        self.memory_dir = Path(memory_dir)
        self.metrics_dir = self.memory_dir / "metrics"
    
    def visualize_metrics_over_time(self, metric_name: str = "overall_quality") -> str:
        """Create a text-based line chart of metrics over time.
        
        Args:
            metric_name: Name of the metric to visualize
            
        Returns:
            ASCII visualization of the metric over time
        """
        if not self.metrics_dir.exists():
            return "No metrics data available."
        
        # Collect metrics data
        metrics_data = []
        for metrics_file in sorted(self.metrics_dir.glob("*.json"), key=lambda x: x.stat().st_mtime):
            with open(metrics_file, "r") as f:
                debate_metrics = json.load(f)
            
            date = debate_metrics.get("date", "Unknown")
            topic = debate_metrics.get("topic", "Unknown")
            value = debate_metrics.get("metrics", {}).get(metric_name)
            
            if value is not None:
                metrics_data.append({
                    "date": date,
                    "topic": topic,
                    "value": value
                })
        
        if not metrics_data:
            return f"No data available for metric '{metric_name}'."
        
        # Create a simple ASCII line chart
        chart = f"\nMetric: {metric_name.capitalize()} Over Time\n"
        chart += "=" * 60 + "\n"
        
        # Y-axis labels and grid
        max_value = max(item["value"] for item in metrics_data)
        min_value = min(item["value"] for item in metrics_data)
        
        # Ensure we have a reasonable range
        if max_value == min_value:
            min_value = max(0, min_value - 0.2)
            max_value = min(1.0, max_value + 0.2)
            
        value_range = max_value - min_value
        
        # Create the chart
        height = 10  # Height of the chart
        width = min(len(metrics_data), 40)  # Width of the chart
        
        # Draw Y-axis and grid
        y_labels = []
        for i in range(height + 1):
            value = max_value - (i / height) * value_range
            if i % 2 == 0:  # Only show every other label for clarity
                y_labels.append(f"{value:.2f}")
            else:
                y_labels.append("")
        
        max_label_width = max(len(label) for label in y_labels)
        
        # Draw chart
        for i in range(height + 1):
            label = y_labels[i].rjust(max_label_width)
            chart += label + " | "
            
            # Draw horizontal grid line
            if i == 0:
                chart += "─" * width  # Top line
            elif i == height:
                chart += "─" * width  # Bottom line
            elif i % 2 == 0:
                chart += "┄" * width  # Grid line
            else:
                chart += " " * width  # Space
            
            chart += "\n"
        
        # Draw X-axis
        chart += " " * max_label_width + " └" + "─" * width + "\n"
        
        # Calculate positions of data points
        data_points = []
        for i, item in enumerate(metrics_data[:width]):
            x = i
            normalized_value = (item["value"] - min_value) / value_range
            y = int((1 - normalized_value) * height)
            data_points.append((x, y, item))
        
        # Draw data points on chart
        chart_lines = chart.split("\n")
        for x, y, item in data_points:
            line = chart_lines[y]
            pos = max_label_width + 3 + x
            if pos < len(line):
                chart_lines[y] = line[:pos] + "●" + line[pos+1:]
        
        chart = "\n".join(chart_lines)
        
        # Add legend
        chart += "\n" + " " * max_label_width + "   "
        for i in range(min(width, len(metrics_data))):
            if i % 5 == 0:  # Show index every 5 points
                chart += str(i).ljust(5)
            else:
                chart += " "
                
        # Add topics for reference
        chart += "\n\nTopics:\n"
        for i, item in enumerate(metrics_data[:width]):
            chart += f"{i}: {item['topic'][:30]}"
            if i % 2 == 0:
                chart += "\n"
            else:
                chart += "  "
                
        return chart
    
    def visualize_agent_performance(self) -> str:
        """Create a bar chart of agent performance metrics.
        
        Returns:
            ASCII bar chart of agent performance
        """
        if not self.metrics_dir.exists():
            return "No metrics data available."
        
        # Collect agent data
        agent_metrics = {}
        
        for metrics_file in self.metrics_dir.glob("*.json"):
            with open(metrics_file, "r") as f:
                debate_metrics = json.load(f)
            
            consistency_scores = debate_metrics.get("metrics", {}).get("consistency", {})
            
            for agent_name, consistency in consistency_scores.items():
                if agent_name not in agent_metrics:
                    agent_metrics[agent_name] = {
                        "consistency_scores": [],
                        "debate_count": 0
                    }
                
                agent_metrics[agent_name]["consistency_scores"].append(consistency)
                agent_metrics[agent_name]["debate_count"] += 1
        
        if not agent_metrics:
            return "No agent performance data available."
        
        # Calculate average metrics
        for agent_name in agent_metrics:
            scores = agent_metrics[agent_name]["consistency_scores"]
            agent_metrics[agent_name]["avg_consistency"] = sum(scores) / len(scores) if scores else 0
        
        # Sort by average consistency
        sorted_agents = sorted(
            agent_metrics.items(), 
            key=lambda x: x[1]["avg_consistency"], 
            reverse=True
        )
        
        # Create bar chart
        chart = "\nAgent Performance (Philosophical Consistency)\n"
        chart += "=" * 60 + "\n"
        
        max_agent_name_len = max(len(agent_name) for agent_name in agent_metrics.keys())
        max_agent_name_len = min(max_agent_name_len, 20)  # Limit for display
        
        for agent_name, metrics in sorted_agents:
            avg_consistency = metrics["avg_consistency"]
            debate_count = metrics["debate_count"]
            
            # Create bar
            bar_length = int(avg_consistency * 30)
            bar = "█" * bar_length
            
            # Format for display
            display_name = agent_name[:max_agent_name_len].ljust(max_agent_name_len)
            chart += f"{display_name} | {bar} {avg_consistency:.2f} ({debate_count} debates)\n"
        
        return chart
    
    def visualize_topic_diversity(self) -> str:
        """Create a visualization of topic diversity.
        
        Returns:
            ASCII visualization of topic diversity
        """
        if not self.metrics_dir.exists():
            return "No metrics data available."
        
        # Collect topic data
        topics = {}
        
        for metrics_file in self.metrics_dir.glob("*.json"):
            with open(metrics_file, "r") as f:
                metrics = json.load(f)
            
            topic = metrics.get("topic", "Unknown")
            diversity = metrics.get("metrics", {}).get("diversity", 0)
            
            if topic != "Unknown":
                if topic not in topics:
                    topics[topic] = []
                topics[topic].append(diversity)
        
        if not topics:
            return "No topic diversity data available."
        
        # Calculate average diversity for each topic
        topic_diversity = {}
        for topic, diversity_scores in topics.items():
            topic_diversity[topic] = sum(diversity_scores) / len(diversity_scores)
        
        # Create visualized output
        viz = "\nTopic Diversity Metrics\n"
        viz += "=" * 60 + "\n"
        
        # Sort topics by diversity score
        sorted_topics = sorted(
            topic_diversity.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        max_topic_len = max(len(topic) for topic in topics.keys())
        max_topic_len = min(max_topic_len, 30)  # Limit for display
        
        for topic, diversity in sorted_topics:
            # Create diversity visualization
            bar_length = int(diversity * 30)
            bar = "█" * bar_length
            
            # Format for display
            display_topic = topic[:max_topic_len].ljust(max_topic_len)
            viz += f"{display_topic} | {bar} {diversity:.2f}\n"
        
        return viz


def visualize_metrics_cli():
    """Command-line interface for metrics visualization."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Visualize debate metrics")
    parser.add_argument("--memory-dir", default="memory", help="Path to memory directory")
    parser.add_argument("--metric", default="overall_quality", 
                        choices=["overall_quality", "coherence", "diversity", "depth"],
                        help="Metric to visualize over time")
    parser.add_argument("--type", default="time", 
                        choices=["time", "agents", "topics"],
                        help="Type of visualization to show")
    
    args = parser.parse_args()
    
    visualizer = MetricsVisualizer(args.memory_dir)
    
    if args.type == "time":
        print(visualizer.visualize_metrics_over_time(args.metric))
    elif args.type == "agents":
        print(visualizer.visualize_agent_performance())
    elif args.type == "topics":
        print(visualizer.visualize_topic_diversity())


if __name__ == "__main__":
    visualize_metrics_cli()
