#!/bin/bash
# Script to analyze debate metrics inside Docker container

# Help message
show_help() {
  echo "Usage: ./analyze_debates.sh [OPTIONS]"
  echo "Analyze debate metrics and visualize results"
  echo
  echo "Options:"
  echo "  --calculate    Calculate metrics for all debates"
  echo "  --time         Visualize metrics over time"
  echo "  --agents       Visualize agent performance"
  echo "  --topics       Visualize topic diversity"
  echo "  --metric NAME  Specify metric to visualize (overall_quality, coherence, diversity, depth)"
  echo "  --help         Show this help message"
  echo
  echo "Examples:"
  echo "  ./analyze_debates.sh --calculate"
  echo "  ./analyze_debates.sh --time --metric diversity"
  echo "  ./analyze_debates.sh --agents"
}

# Default values
CALCULATE=false
VISUALIZE=""
METRIC="overall_quality"

# Parse arguments
while [[ $# -gt 0 ]]; do
  case "$1" in
    --calculate)
      CALCULATE=true
      shift
      ;;
    --time)
      VISUALIZE="time"
      shift
      ;;
    --agents)
      VISUALIZE="agents"
      shift
      ;;
    --topics)
      VISUALIZE="topics"
      shift
      ;;
    --metric)
      METRIC="$2"
      shift 2
      ;;
    --help)
      show_help
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      show_help
      exit 1
      ;;
  esac
done

# Show help if no arguments provided
if [[ "$CALCULATE" == "false" && -z "$VISUALIZE" ]]; then
  show_help
  exit 0
fi

# Calculate metrics if requested
if [[ "$CALCULATE" == "true" ]]; then
  echo "Calculating metrics for all debates..."
  docker compose run --rm debate-system python -m src.metrics.debate_metrics
fi

# Visualize metrics if requested
if [[ -n "$VISUALIZE" ]]; then
  echo "Visualizing debate metrics..."
  docker compose run --rm debate-system python -m src.metrics.visualizers --type "$VISUALIZE" --metric "$METRIC"
fi

echo "Analysis complete."
