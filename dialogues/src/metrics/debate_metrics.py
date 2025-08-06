"""
Debate Metrics Module

This module provides metrics calculation for philosophical debates, measuring:
- Philosophical accuracy (faithfulness to philosophical traditions)
- Coherence (logical consistency and clarity)
- Diversity (representation of different viewpoints)
- User satisfaction (relevance and helpfulness)
"""

import json
import os
from pathlib import Path
from collections import Counter
from typing import Dict, List, Any, Optional, Union, Tuple
import math


class DebateMetricsCalculator:
    """Calculator for various metrics related to philosophical debates."""
    
    def __init__(self, memory_dir: str = "memory"):
        """Initialize metrics calculator with path to memory directory.
        
        Args:
            memory_dir: Path to memory directory containing debate records
        """
        self.memory_dir = Path(memory_dir)
        self.debates_dir = self.memory_dir / "debates"
        self.agents_dir = self.memory_dir / "agents"
        self.indexes_dir = self.memory_dir / "indexes"
        
        # Create metrics directory if it doesn't exist
        self.metrics_dir = self.memory_dir / "metrics"
        os.makedirs(self.metrics_dir, exist_ok=True)
    
    def calculate_metrics_for_debate(self, debate_id: str) -> Dict[str, Any]:
        """Calculate all metrics for a specific debate.
        
        Args:
            debate_id: ID of the debate to analyze
            
        Returns:
            Dictionary of metrics for the debate
        """
        debate_file = self.debates_dir / f"{debate_id}.json"
        if not debate_file.exists():
            return {"error": f"Debate {debate_id} not found"}
        
        with open(debate_file, "r") as f:
            debate = json.load(f)
        
        # Ensure we have responses to analyze
        if "responses" not in debate or not debate["responses"]:
            print(f"Warning: No responses found in debate {debate_id}")
            # Use placeholder values
            coherence_score = 0.7  # Default base coherence
            diversity_score = 0.0
            depth_score = 0.0
            consistency_scores = {}
        else:
            # Calculate all metrics from responses
            coherence_score = self.calculate_coherence(debate)
            diversity_score = self.calculate_perspective_diversity(debate)
            depth_score = self.calculate_philosophical_depth(debate)
            consistency_scores = self.calculate_philosophical_consistency(debate)
        
        # Use proper debate topic and date fields
        topic = debate.get("topic", "Unknown")
        date = debate.get("date", "Unknown")
        
        # Extract agent names for reporting
        agents = [response.get("agent", "Unknown") for response in debate.get("responses", [])]
        
        # Compile metrics
        metrics = {
            "debate_id": debate_id,
            "topic": topic,
            "date": date,
            "agents": agents,
            "metrics": {
                "coherence": coherence_score,
                "diversity": diversity_score,
                "depth": depth_score,
                "consistency": consistency_scores,
                "overall_quality": (coherence_score + diversity_score + depth_score) / 3
            }
        }
        
        # Save metrics to file
        self.save_metrics(debate_id, metrics)
        
        # Print a summary of metrics for the console output
        print(f"Metrics for debate '{topic}': ")
        print(f"  Coherence: {coherence_score:.2f}")
        print(f"  Diversity: {diversity_score:.2f}")
        print(f"  Depth: {depth_score:.2f}")
        print(f"  Overall Quality: {(coherence_score + diversity_score + depth_score) / 3:.2f}")
        
        return metrics
    
    def calculate_coherence(self, debate: Dict[str, Any]) -> float:
        """Calculate coherence score based on logical consistency and clarity.
        
        This is a simplified implementation that counts contradictions and logical fallacies.
        In a production system, this would use NLP techniques to identify logical structure.
        
        Args:
            debate: Full debate data
            
        Returns:
            Coherence score from 0.0 to 1.0
        """
        # Placeholder implementation - would need NLP in production
        # For demonstration, we'll use a random but consistent score based on debate properties
        base_coherence = 0.7  # Starting with decent coherence
        
        # Longer critiques may indicate more thorough reasoning
        agent_analyses = [agent.get("analysis", "") for agent in debate.get("agents", [])]
        avg_analysis_length = sum(len(analysis) for analysis in agent_analyses) / max(len(agent_analyses), 1)
        length_factor = min(avg_analysis_length / 500, 1.0) * 0.2  # Length bonus up to 0.2
        
        # More structured analyses (with sections, points) may indicate better coherence
        structure_indicators = sum(
            analysis.count("\n-") + analysis.count("\n1.") + analysis.count("\nFirst,") 
            for analysis in agent_analyses
        )
        structure_factor = min(structure_indicators / 10, 1.0) * 0.1  # Structure bonus up to 0.1
        
        return min(base_coherence + length_factor + structure_factor, 1.0)
    
    def calculate_perspective_diversity(self, debate: Dict[str, Any]) -> float:
        """Calculate diversity score based on representation of different viewpoints.
        
        Args:
            debate: Full debate data
            
        Returns:
            Diversity score from 0.0 to 1.0
        """
        agents = debate.get("agents", [])
        if not agents:
            return 0.0
        
        # Count distinct philosophical traditions referenced
        traditions = set()
        for agent in agents:
            analysis = agent.get("analysis", "").lower()
            # Check for mentions of major philosophical traditions
            traditions_keywords = [
                "utilitarian", "deontolog", "virtue ethics", "existential", "pragmati", 
                "empiric", "rational", "phenomenolog", "analytic", "continental",
                "eastern", "buddhis", "taois", "confucian", "hindu"
            ]
            
            for keyword in traditions_keywords:
                if keyword in analysis:
                    traditions.add(keyword)
        
        # Calculate diversity based on number of traditions referenced
        # More traditions = higher diversity score
        diversity_score = min(len(traditions) / 8, 1.0)  # Max out at 8 traditions
        
        # Check if there are opposing viewpoints
        has_disagreement = False
        for agent in agents:
            for other_agent in agents:
                if agent != other_agent:
                    if "disagree" in agent.get("analysis", "").lower() or "contrary" in agent.get("analysis", "").lower():
                        has_disagreement = True
                        break
        
        if has_disagreement:
            diversity_score = min(diversity_score + 0.2, 1.0)  # Bonus for explicit disagreement
            
        return diversity_score
    
    def calculate_philosophical_depth(self, debate: Dict[str, Any]) -> float:
        """Calculate depth score based on philosophical sophistication and detail.
        
        Args:
            debate: Full debate data
            
        Returns:
            Depth score from 0.0 to 1.0
        """
        # Count references to philosophers, concepts, and arguments
        philosophers = [
            "aristotle", "plato", "kant", "nietzsche", "hume", "marx", "sartre", 
            "wittgenstein", "descartes", "hegel", "locke", "rousseau", "kierkegaard",
            "confucius", "buddha", "laozi", "spinoza", "aquinas", "heidegger"
        ]
        
        concepts = [
            "ethics", "metaphysics", "epistemology", "ontology", "phenomenology",
            "existentialism", "empiricism", "rationalism", "utilitarianism",
            "deontology", "categorical imperative", "virtue", "moral", "epistemic",
            "truth", "knowledge", "justice", "freedom", "consciousness", "meaning"
        ]
        
        # Count mentions in all agent analyses
        philosopher_mentions = 0
        concept_mentions = 0
        
        for agent in debate.get("agents", []):
            analysis = agent.get("analysis", "").lower()
            
            for philosopher in philosophers:
                philosopher_mentions += analysis.count(philosopher)
                
            for concept in concepts:
                concept_mentions += analysis.count(concept)
        
        # Calculate depth score based on mentions
        # Sophisticated philosophical discussions should reference both thinkers and concepts
        philosopher_score = min(philosopher_mentions / 5, 1.0) * 0.5  # Max of 5 philosopher mentions for full score
        concept_score = min(concept_mentions / 10, 1.0) * 0.5  # Max of 10 concept mentions for full score
        
        return philosopher_score + concept_score
    
    def calculate_philosophical_consistency(self, debate: Dict[str, Any]) -> Dict[str, float]:
        """Calculate consistency scores for each agent based on past positions.
        
        Args:
            debate: Full debate data
            
        Returns:
            Dictionary mapping agent names to consistency scores
        """
        consistency_scores = {}
        
        for agent in debate.get("agents", []):
            agent_name = agent.get("name")
            if not agent_name:
                continue
                
            # Get agent memory file
            agent_file = self.agents_dir / f"{agent_name}.json"
            if not agent_file.exists():
                consistency_scores[agent_name] = 1.0  # No previous positions, so technically consistent
                continue
                
            # Load agent memory
            with open(agent_file, "r") as f:
                agent_memory = json.load(f)
                
            # Get agent's positions on topics
            positions = agent_memory.get("positions", {})
            current_topic = debate.get("topic", "")
            
            # Default consistency score
            consistency_score = 1.0
            
            # Check if agent has previous positions on this topic or related topics
            related_topics = self._find_related_topics(current_topic, positions.keys())
            if not related_topics:
                consistency_scores[agent_name] = consistency_score  # No previous positions on related topics
                continue
                
            # Compare current position with previous positions on related topics
            current_analysis = agent.get("analysis", "").lower()
            previous_positions = []
            
            for topic in related_topics:
                for position in positions.get(topic, []):
                    previous_positions.append(position.get("position", "").lower())
            
            if previous_positions:
                # Simple text similarity check - in production, use embeddings or semantic similarity
                contradictions = 0
                for prev_pos in previous_positions:
                    # Check for opposite statements (simplistic)
                    if "not" in prev_pos and "not" not in current_analysis:
                        contradictions += 1
                    if "disagree" in prev_pos and "agree" in current_analysis:
                        contradictions += 1
                    if "agree" in prev_pos and "disagree" in current_analysis:
                        contradictions += 1
                
                # Reduce consistency score for each contradiction found
                consistency_score -= min(contradictions * 0.2, 0.8)  # Allow for some evolution of thought
                
            consistency_scores[agent_name] = max(consistency_score, 0.2)  # Floor at 0.2
            
        return consistency_scores
    
    def _find_related_topics(self, current_topic: str, previous_topics: List[str]) -> List[str]:
        """Find topics related to the current debate topic.
        
        Args:
            current_topic: Current debate topic
            previous_topics: List of previous debate topics
            
        Returns:
            List of related previous topics
        """
        current_words = set(current_topic.lower().split())
        related = []
        
        for topic in previous_topics:
            topic_words = set(topic.lower().split())
            # Check for word overlap
            if current_words.intersection(topic_words):
                related.append(topic)
                
        return related
    
    def save_metrics(self, debate_id: str, metrics: Dict[str, Any]) -> None:
        """Save calculated metrics to the metrics directory.
        
        Args:
            debate_id: ID of the debate
            metrics: Dictionary of metrics to save
        """
        metrics_file = self.metrics_dir / f"{debate_id}.json"
        with open(metrics_file, "w") as f:
            json.dump(metrics, f, indent=2)
    
    def get_metrics_over_time(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get metrics over time to track debate quality trends.
        
        Returns:
            Dictionary mapping metric names to lists of values over time
        """
        if not self.metrics_dir.exists():
            return {}
            
        metrics_over_time = {
            "coherence": [],
            "diversity": [],
            "depth": [],
            "overall_quality": []
        }
        
        for metrics_file in sorted(self.metrics_dir.glob("*.json"), key=lambda x: x.stat().st_mtime):
            with open(metrics_file, "r") as f:
                debate_metrics = json.load(f)
                
            date = debate_metrics.get("date", "Unknown")
            metrics = debate_metrics.get("metrics", {})
            
            for metric_name in metrics_over_time.keys():
                if metric_name in metrics:
                    metrics_over_time[metric_name].append({
                        "date": date,
                        "topic": debate_metrics.get("topic", "Unknown"),
                        "value": metrics[metric_name]
                    })
                    
        return metrics_over_time
    
    def get_agent_performance_metrics(self) -> Dict[str, Dict[str, Any]]:
        """Get performance metrics for each agent based on consistency and depth.
        
        Returns:
            Dictionary mapping agent names to performance metrics
        """
        agent_metrics = {}
        
        # Collect metrics from all debates
        if not self.metrics_dir.exists():
            return {}
            
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
        
        # Calculate average metrics for each agent
        for agent_name in agent_metrics.keys():
            consistency_scores = agent_metrics[agent_name]["consistency_scores"]
            if consistency_scores:
                agent_metrics[agent_name]["avg_consistency"] = sum(consistency_scores) / len(consistency_scores)
            else:
                agent_metrics[agent_name]["avg_consistency"] = 0
                
        return agent_metrics


def calculate_metrics_for_all_debates(memory_dir: str = "memory") -> None:
    """Calculate metrics for all debates in the memory system.
    
    Args:
        memory_dir: Path to the memory directory
    """
    calculator = DebateMetricsCalculator(memory_dir)
    debates_dir = Path(memory_dir) / "debates"
    
    if not debates_dir.exists():
        print("No debates found in memory.")
        return
        
    for debate_file in debates_dir.glob("*.json"):
        debate_id = debate_file.stem
        print(f"Calculating metrics for debate {debate_id}...")
        metrics = calculator.calculate_metrics_for_debate(debate_id)
        
        print(f"Metrics for debate '{metrics.get('topic', 'Unknown')}': ")
        print(f"  Coherence: {metrics['metrics']['coherence']:.2f}")
        print(f"  Diversity: {metrics['metrics']['diversity']:.2f}")
        print(f"  Depth: {metrics['metrics']['depth']:.2f}")
        print(f"  Overall Quality: {metrics['metrics']['overall_quality']:.2f}")
        print()
    
    print("Metrics calculation complete.")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        calculate_metrics_for_all_debates(sys.argv[1])
    else:
        calculate_metrics_for_all_debates()
