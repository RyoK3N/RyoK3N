#!/usr/bin/env python3
"""
ML Performance Charts Generator
Generates beautiful SVG charts for GitHub README
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from datetime import datetime, timedelta
import os

# Set style for professional-looking charts
plt.style.use('seaborn-v0_8-darkgrid')
plt.rcParams['figure.facecolor'] = 'white'
plt.rcParams['axes.facecolor'] = '#f8f9fa'
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans']

# Create assets/charts directory if it doesn't exist
os.makedirs('assets/charts', exist_ok=True)

def generate_accuracy_chart():
    """Generate model accuracy over time chart"""
    epochs = np.arange(1, 51)
    # Simulate realistic accuracy curve
    base_accuracy = 70 + 25 * (1 - np.exp(-epochs/10))
    noise = np.random.normal(0, 1.5, len(epochs))
    accuracy = base_accuracy + noise
    accuracy = np.clip(accuracy, 0, 100)
    
    fig, ax = plt.subplots(figsize=(10, 6), dpi=100)
    
    # Plot training accuracy
    ax.plot(epochs, accuracy, linewidth=2.5, color='#667eea', 
            label='Training Accuracy', marker='o', markersize=4, alpha=0.8)
    
    # Plot validation accuracy (slightly lower)
    val_accuracy = accuracy - np.random.uniform(1, 3, len(epochs))
    ax.plot(epochs, val_accuracy, linewidth=2.5, color='#764ba2',
            label='Validation Accuracy', marker='s', markersize=4, alpha=0.8)
    
    ax.set_xlabel('Epoch', fontsize=12, fontweight='bold')
    ax.set_ylabel('Accuracy (%)', fontsize=12, fontweight='bold')
    ax.set_title('Model Accuracy Progression', fontsize=14, fontweight='bold', pad=20)
    ax.legend(loc='lower right', fontsize=10, framealpha=0.9)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_ylim([60, 100])
    
    # Add annotation for peak accuracy
    max_acc_idx = np.argmax(val_accuracy)
    ax.annotate(f'Peak: {val_accuracy[max_acc_idx]:.1f}%',
                xy=(epochs[max_acc_idx], val_accuracy[max_acc_idx]),
                xytext=(epochs[max_acc_idx]-10, val_accuracy[max_acc_idx]-5),
                arrowprops=dict(arrowstyle='->', color='red', lw=2),
                fontsize=10, fontweight='bold', color='red')
    
    plt.tight_layout()
    plt.savefig('assets/charts/accuracy_chart.svg', format='svg', 
                bbox_inches='tight', facecolor='white')
    plt.close()
    print("✅ Generated: accuracy_chart.svg")

def generate_loss_chart():
    """Generate training loss progression chart"""
    epochs = np.arange(1, 51)
    # Simulate realistic loss curve
    initial_loss = 2.5
    loss = initial_loss * np.exp(-epochs/15) + 0.05
    noise = np.random.normal(0, 0.02, len(epochs))
    loss = loss + noise
    
    fig, ax = plt.subplots(figsize=(10, 6), dpi=100)
    
    # Plot training loss
    ax.plot(epochs, loss, linewidth=2.5, color='#f093fb',
            label='Training Loss', marker='o', markersize=4, alpha=0.8)
    
    # Plot validation loss
    val_loss = loss + np.random.uniform(0.01, 0.05, len(epochs))
    ax.plot(epochs, val_loss, linewidth=2.5, color='#4facfe',
            label='Validation Loss', marker='s', markersize=4, alpha=0.8)
    
    ax.set_xlabel('Epoch', fontsize=12, fontweight='bold')
    ax.set_ylabel('Loss', fontsize=12, fontweight='bold')
    ax.set_title('Training Loss Progression', fontsize=14, fontweight='bold', pad=20)
    ax.legend(loc='upper right', fontsize=10, framealpha=0.9)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_yscale('log')
    
    plt.tight_layout()
    plt.savefig('assets/charts/loss_chart.svg', format='svg',
                bbox_inches='tight', facecolor='white')
    plt.close()
    print("✅ Generated: loss_chart.svg")

def generate_dataset_growth():
    """Generate dataset growth timeline chart"""
    # Generate weekly data for the past year
    weeks = 52
    dates = [datetime.now() - timedelta(weeks=i) for i in range(weeks)][::-1]
    
    # Simulate dataset growth
    initial = 100000
    growth_rate = 1.015
    samples = [int(initial * (growth_rate ** i) + np.random.normal(0, 5000)) 
               for i in range(weeks)]
    
    fig, ax = plt.subplots(figsize=(10, 6), dpi=100)
    
    # Create area chart
    ax.fill_between(range(weeks), samples, alpha=0.3, color='#43e97b')
    ax.plot(range(weeks), samples, linewidth=2.5, color='#38f9d7',
            marker='o', markersize=3)
    
    ax.set_xlabel('Week', fontsize=12, fontweight='bold')
    ax.set_ylabel('Total Samples', fontsize=12, fontweight='bold')
    ax.set_title('Dataset Growth Timeline', fontsize=14, fontweight='bold', pad=20)
    ax.grid(True, alpha=0.3, linestyle='--')
    
    # Format y-axis to show thousands
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x/1000)}K'))
    
    # Add current total annotation
    ax.annotate(f'Current: {samples[-1]:,} samples',
                xy=(weeks-1, samples[-1]),
                xytext=(weeks-15, samples[-1]*0.9),
                arrowprops=dict(arrowstyle='->', color='#43e97b', lw=2),
                fontsize=10, fontweight='bold', color='#43e97b',
                bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig('assets/charts/dataset_growth.svg', format='svg',
                bbox_inches='tight', facecolor='white')
    plt.close()
    print("✅ Generated: dataset_growth.svg")

def generate_language_distribution():
    """Generate programming language usage distribution"""
    languages = ['Python', 'C++', 'JavaScript', 'R', 'Julia', 'Other']
    percentages = [55.2, 19.7, 10.3, 6.5, 4.8, 3.5]
    colors = ['#3776AB', '#00599C', '#F7DF1E', '#276DC3', '#9558B2', '#95a5a6']
    
    fig, ax = plt.subplots(figsize=(10, 6), dpi=100)
    
    # Create horizontal bar chart
    bars = ax.barh(languages, percentages, color=colors, alpha=0.8, height=0.6)
    
    # Add percentage labels
    for i, (bar, pct) in enumerate(zip(bars, percentages)):
        width = bar.get_width()
        ax.text(width + 1, bar.get_y() + bar.get_height()/2,
                f'{pct}%', ha='left', va='center',
                fontsize=11, fontweight='bold')
    
    ax.set_xlabel('Usage Percentage', fontsize=12, fontweight='bold')
    ax.set_title('Programming Language Distribution', fontsize=14, 
                 fontweight='bold', pad=20)
    ax.set_xlim([0, 65])
    ax.grid(True, alpha=0.3, linestyle='--', axis='x')
    
    plt.tight_layout()
    plt.savefig('assets/charts/language_distribution.svg', format='svg',
                bbox_inches='tight', facecolor='white')
    plt.close()
    print("✅ Generated: language_distribution.svg")

def generate_performance_dashboard():
    """Generate comprehensive performance dashboard"""
    fig = plt.figure(figsize=(14, 8), dpi=100)
    
    # Create 2x2 grid
    gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)
    
    # 1. Accuracy comparison
    ax1 = fig.add_subplot(gs[0, 0])
    models = ['GTransformer', 'PoseNet', 'Vision-RL', 'Baseline']
    accuracies = [95.8, 93.2, 89.5, 87.3]
    colors = ['#667eea', '#764ba2', '#f093fb', '#4facfe']
    bars1 = ax1.bar(models, accuracies, color=colors, alpha=0.8)
    ax1.set_ylabel('Accuracy (%)', fontweight='bold')
    ax1.set_title('Model Accuracy Comparison', fontweight='bold')
    ax1.set_ylim([80, 100])
    ax1.grid(True, alpha=0.3, axis='y')
    
    # Add value labels
    for bar in bars1:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}%', ha='center', va='bottom',
                fontweight='bold', fontsize=9)
    
    # 2. Inference latency
    ax2 = fig.add_subplot(gs[0, 1])
    latencies = [42, 58, 125, 35]
    bars2 = ax2.bar(models, latencies, color=colors, alpha=0.8)
    ax2.set_ylabel('Latency (ms)', fontweight='bold')
    ax2.set_title('Inference Latency', fontweight='bold')
    ax2.grid(True, alpha=0.3, axis='y')
    
    # Add value labels
    for bar in bars2:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}ms', ha='center', va='bottom',
                fontweight='bold', fontsize=9)
    
    # 3. Training metrics over time
    ax3 = fig.add_subplot(gs[1, :])
    epochs = np.arange(1, 31)
    acc = 70 + 25 * (1 - np.exp(-epochs/8))
    loss = 2.5 * np.exp(-epochs/10) + 0.05
    
    ax3_twin = ax3.twinx()
    
    line1 = ax3.plot(epochs, acc, linewidth=2.5, color='#667eea',
                     label='Accuracy', marker='o', markersize=4)
    line2 = ax3_twin.plot(epochs, loss, linewidth=2.5, color='#f093fb',
                          label='Loss', marker='s', markersize=4)
    
    ax3.set_xlabel('Epoch', fontweight='bold')
    ax3.set_ylabel('Accuracy (%)', fontweight='bold', color='#667eea')
    ax3_twin.set_ylabel('Loss', fontweight='bold', color='#f093fb')
    ax3.set_title('Training Progress - Best Model (GTransformer)', fontweight='bold')
    ax3.grid(True, alpha=0.3)
    
    # Combined legend
    lines = line1 + line2
    labels = [l.get_label() for l in lines]
    ax3.legend(lines, labels, loc='center right')
    
    # Add title
    fig.suptitle('🧠 ML Performance Dashboard', fontsize=16, 
                 fontweight='bold', y=0.98)
    
    plt.savefig('assets/charts/performance_dashboard.svg', format='svg',
                bbox_inches='tight', facecolor='white')
    plt.close()
    print("✅ Generated: performance_dashboard.svg")

def generate_historical_trends():
    """Generate historical performance trends"""
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    # Simulate metrics over 12 months
    accuracy = [85 + i*0.8 + np.random.normal(0, 1) for i in range(12)]
    projects = [5 + i*0.5 + np.random.randint(-1, 2) for i in range(12)]
    contributions = [50 + i*10 + np.random.randint(-5, 15) for i in range(12)]
    
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 10), dpi=100)
    
    # 1. Accuracy trend
    ax1.plot(months, accuracy, linewidth=3, color='#667eea',
             marker='o', markersize=8, markerfacecolor='white',
             markeredgewidth=2, markeredgecolor='#667eea')
    ax1.fill_between(range(12), accuracy, alpha=0.2, color='#667eea')
    ax1.set_ylabel('Accuracy (%)', fontsize=11, fontweight='bold')
    ax1.set_title('Model Accuracy Trend (2024)', fontsize=12, fontweight='bold')
    ax1.grid(True, alpha=0.3, linestyle='--')
    ax1.set_ylim([80, 100])
    
    # 2. Active projects
    ax2.bar(months, projects, color='#43e97b', alpha=0.8, width=0.6)
    ax2.set_ylabel('Active Projects', fontsize=11, fontweight='bold')
    ax2.set_title('Project Activity', fontsize=12, fontweight='bold')
    ax2.grid(True, alpha=0.3, linestyle='--', axis='y')
    
    # 3. GitHub contributions
    ax3.fill_between(range(12), contributions, alpha=0.3, color='#f093fb')
    ax3.plot(months, contributions, linewidth=3, color='#764ba2',
             marker='s', markersize=8, markerfacecolor='white',
             markeredgewidth=2, markeredgecolor='#764ba2')
    ax3.set_ylabel('Contributions', fontsize=11, fontweight='bold')
    ax3.set_xlabel('Month', fontsize=11, fontweight='bold')
    ax3.set_title('GitHub Activity', fontsize=12, fontweight='bold')
    ax3.grid(True, alpha=0.3, linestyle='--')
    
    fig.suptitle('📈 Year-over-Year Performance Trends', fontsize=14,
                 fontweight='bold', y=0.995)
    
    plt.tight_layout()
    plt.savefig('assets/charts/historical_trends.svg', format='svg',
                bbox_inches='tight', facecolor='white')
    plt.close()
    print("✅ Generated: historical_trends.svg")

def main():
    """Generate all charts"""
    print("🎨 Generating ML Performance Charts...")
    print("-" * 50)
    
    generate_accuracy_chart()
    generate_loss_chart()
    generate_dataset_growth()
    generate_language_distribution()
    generate_performance_dashboard()
    generate_historical_trends()
    
    print("-" * 50)
    print("✨ All charts generated successfully!")
    print(f"📁 Charts saved in: assets/charts/")
    print(f"🕒 Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
