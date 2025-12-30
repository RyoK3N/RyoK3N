#!/usr/bin/env python3
"""
AI Agent - Metrics Generation Module
Generates performance metrics and tracking data for the AI agent.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

# Configuration
DATA_DIR = Path(__file__).parent / "data"
METRICS_FILE = DATA_DIR / "agent_metrics.json"

def load_existing_metrics() -> Dict[str, Any]:
    """Load existing metrics if available."""
    if METRICS_FILE.exists():
        with open(METRICS_FILE, 'r') as f:
            return json.load(f)
    
    # Initialize new metrics structure
    return {
        "created_at": datetime.now().isoformat(),
        "total_runs": 0,
        "successful_runs": 0,
        "failed_runs": 0,
        "last_run": None,
        "run_history": []
    }

def calculate_success_rate(metrics: Dict[str, Any]) -> float:
    """Calculate success rate percentage."""
    total = metrics["total_runs"]
    if total == 0:
        return 100.0
    return round((metrics["successful_runs"] / total) * 100, 2)

def update_metrics(success: bool = True) -> Dict[str, Any]:
    """Update metrics with current run information."""
    metrics = load_existing_metrics()
    
    # Update counters
    metrics["total_runs"] += 1
    if success:
        metrics["successful_runs"] += 1
    else:
        metrics["failed_runs"] += 1
    
    # Update last run
    metrics["last_run"] = datetime.now().isoformat()
    
    # Add to history (keep last 30 runs)
    run_record = {
        "timestamp": datetime.now().isoformat(),
        "success": success,
        "run_number": metrics["total_runs"]
    }
    
    metrics["run_history"].append(run_record)
    metrics["run_history"] = metrics["run_history"][-30:]  # Keep last 30
    
    # Calculate success rate
    metrics["success_rate"] = calculate_success_rate(metrics)
    
    return metrics

def generate_performance_summary(metrics: Dict[str, Any]) -> Dict[str, str]:
    """Generate a human-readable performance summary."""
    success_rate = metrics.get("success_rate", 0)
    
    # Determine status
    if success_rate >= 95:
        status = "🟢 Excellent"
    elif success_rate >= 85:
        status = "🟡 Good"
    else:
        status = "🔴 Needs Attention"
    
    # Calculate uptime
    total_runs = metrics["total_runs"]
    successful_runs = metrics["successful_runs"]
    
    return {
        "status": status,
        "success_rate": f"{success_rate}%",
        "total_runs": str(total_runs),
        "successful_runs": str(successful_runs),
        "uptime": f"{success_rate}%" if total_runs > 0 else "N/A"
    }

def save_metrics(metrics: Dict[str, Any]) -> None:
    """Save metrics to file."""
    DATA_DIR.mkdir(exist_ok=True)
    
    with open(METRICS_FILE, 'w') as f:
        json.dump(metrics, f, indent=2)

def print_metrics_summary(metrics: Dict[str, Any]) -> None:
    """Print a formatted summary of metrics."""
    summary = generate_performance_summary(metrics)
    
    print("\n" + "=" * 60)
    print("📊 AI AGENT PERFORMANCE METRICS")
    print("=" * 60)
    print(f"Status:          {summary['status']}")
    print(f"Success Rate:    {summary['success_rate']}")
    print(f"Total Runs:      {summary['total_runs']}")
    print(f"Successful:      {summary['successful_runs']}")
    print(f"Failed:          {metrics['failed_runs']}")
    print(f"Last Run:        {metrics['last_run']}")
    print("=" * 60)

def main():
    """Main metrics generation function."""
    try:
        print("📊 Generating performance metrics...")
        
        # Update metrics (assuming success if this script runs)
        metrics = update_metrics(success=True)
        
        # Save metrics
        save_metrics(metrics)
        print(f"✅ Metrics saved to {METRICS_FILE}")
        
        # Print summary
        print_metrics_summary(metrics)
        
        # Check if any attention is needed
        if metrics["success_rate"] < 85:
            print("\n⚠️  Warning: Success rate is below 85%")
            print("   Consider reviewing recent failures")
        
    except Exception as e:
        print(f"❌ Error generating metrics: {e}")
        
        # Log failure
        try:
            metrics = update_metrics(success=False)
            save_metrics(metrics)
        except:
            pass
        
        raise

if __name__ == "__main__":
    main()
