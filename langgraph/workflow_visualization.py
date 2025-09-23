#!/usr/bin/env python
# coding: utf-8

"""
Script to visualize the proposal analysis workflow.
"""

import networkx as nx
import matplotlib.pyplot as plt
from proposal_analyzer import create_proposal_analysis_graph

def visualize_workflow():
    """
    Create and visualize the workflow graph.
    """
    print("Generating workflow visualization...")
    
    # Get the graph from the proposal_analyzer module
    graph = create_proposal_analysis_graph()
    
    # Convert the LangGraph to a NetworkX graph for visualization
    nx_graph = nx.DiGraph()
    
    # Define the workflow structure
    workflow_nodes = [
        "planning_agent",
        "search_tool",
        "indexer_tool",
        "reader_tool",
        "analyzing_agent",
        "claim_evidence_graph",
        "signal_detectors",
        "hypothesizer",
        "skeptic_agent",
        "rag_fallback",
        "prioritizer_agent",
        "strategy_agent",
        "END"
    ]
    
    workflow_edges = [
        ("planning_agent", "search_tool"),
        ("search_tool", "indexer_tool"),
        ("indexer_tool", "reader_tool"),
        ("reader_tool", "analyzing_agent"),
        ("analyzing_agent", "claim_evidence_graph"),
        ("claim_evidence_graph", "signal_detectors"),
        ("signal_detectors", "hypothesizer"),
        ("hypothesizer", "skeptic_agent"),
        ("skeptic_agent", "rag_fallback", "use_rag"),
        ("skeptic_agent", "prioritizer_agent", "skip_rag"),
        ("rag_fallback", "prioritizer_agent"),
        ("prioritizer_agent", "strategy_agent"),
        ("strategy_agent", "END")
    ]
    
    # Add nodes to the NetworkX graph
    for node in workflow_nodes:
        nx_graph.add_node(node)
    
    # Add edges to the NetworkX graph
    for edge in workflow_edges:
        if len(edge) == 2:
            nx_graph.add_edge(edge[0], edge[1])
        elif len(edge) == 3:
            nx_graph.add_edge(edge[0], edge[1], condition=edge[2])
    
    # Create a figure
    plt.figure(figsize=(15, 10), facecolor='white')
    
    # Set white background
    plt.rcParams['figure.facecolor'] = 'white'
    plt.rcParams['axes.facecolor'] = 'white'
    
    # Create a manual layout for better visualization
    pos = {
        "planning_agent": (0, 0),
        "search_tool": (0, -1),
        "indexer_tool": (0, -2),
        "reader_tool": (0, -3),
        "analyzing_agent": (0, -4),
        "claim_evidence_graph": (0, -5),
        "signal_detectors": (0, -6),
        "hypothesizer": (0, -7),
        "skeptic_agent": (0, -8),
        "rag_fallback": (-2, -9),
        "prioritizer_agent": (0, -10),
        "strategy_agent": (0, -11),
        "END": (0, -12)
    }
    
    # Define node colors and shapes
    node_colors = {
        "planning_agent": "#E6F3FF",
        "search_tool": "#F0FFF0",
        "indexer_tool": "#F0FFF0",
        "reader_tool": "#F0FFF0",
        "analyzing_agent": "#E6F3FF",
        "claim_evidence_graph": "#FFEBCC",
        "signal_detectors": "#FFEBCC",
        "hypothesizer": "#E6F3FF",
        "skeptic_agent": "#E6F3FF",
        "rag_fallback": "#F0FFF0",
        "prioritizer_agent": "#E6F3FF",
        "strategy_agent": "#E6F3FF",
        "END": "#FFCCCC"
    }
    
    # Get the colors for each node
    node_color_list = [node_colors[node] for node in nx_graph.nodes()]
    
    # Draw edges
    edge_labels = {}
    for u, v, data in nx_graph.edges(data=True):
        if 'condition' in data:
            edge_labels[(u, v)] = data['condition']
    
    # Draw the graph
    nx.draw_networkx_nodes(nx_graph, pos, node_color=node_color_list, 
                          node_size=2000, edgecolors='black', linewidths=1.5)
    
    # Draw regular edges
    regular_edges = [(u, v) for u, v, d in nx_graph.edges(data=True) if 'condition' not in d]
    nx.draw_networkx_edges(nx_graph, pos, edgelist=regular_edges, 
                          arrows=True, width=1.5, edge_color='gray')
    
    # Draw conditional edges
    conditional_edges = [(u, v) for u, v, d in nx_graph.edges(data=True) if 'condition' in d]
    nx.draw_networkx_edges(nx_graph, pos, edgelist=conditional_edges, 
                          arrows=True, width=1.5, edge_color='red', style='dashed')
    
    # Draw labels
    nx.draw_networkx_labels(nx_graph, pos, font_size=10, font_weight='bold')
    
    # Draw edge labels
    nx.draw_networkx_edge_labels(nx_graph, pos, edge_labels=edge_labels, font_size=8)
    
    # Add a legend
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], marker='o', color='w', markerfacecolor='#E6F3FF', markersize=15, 
              label='Agent Nodes', markeredgecolor='black'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='#F0FFF0', markersize=15, 
              label='Tool Nodes', markeredgecolor='black'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='#FFEBCC', markersize=15, 
              label='Data Processing Nodes', markeredgecolor='black'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='#FFCCCC', markersize=15, 
              label='End Node', markeredgecolor='black'),
        Line2D([0], [0], color='gray', lw=2, label='Standard Flow'),
        Line2D([0], [0], color='red', lw=2, linestyle='--', label='Conditional Flow')
    ]
    plt.legend(handles=legend_elements, loc="upper right", frameon=True, 
              facecolor='white', edgecolor='black')
    
    # Add title
    plt.title("Proposal Analysis Workflow", fontsize=16, fontweight='bold')
    
    # Remove axis
    plt.axis('off')
    
    # Adjust layout
    plt.tight_layout()
    
    return plt

def create_roadmap_visualization():
    """
    Create a roadmap visualization showing the implementation phases.
    """
    print("Generating roadmap visualization...")
    
    # Create a figure
    plt.figure(figsize=(15, 8), facecolor='white')
    
    # Set white background
    plt.rcParams['figure.facecolor'] = 'white'
    plt.rcParams['axes.facecolor'] = 'white'
    
    # Define the phases and their tasks
    phases = {
        "Phase 1: Data Collection": [
            "Planning agent creates research plan",
            "Search tool gathers web information",
            "Indexer tool accesses canonical sources",
            "Reader tool extracts relevant quotes"
        ],
        "Phase 2: Analysis": [
            "Analyzing agent extracts claims and evidence",
            "Claim-evidence graph builds relationships",
            "Signal detectors identify important patterns",
            "Hypothesizer generates initial hypotheses"
        ],
        "Phase 3: Evaluation": [
            "Skeptic agent critically evaluates hypotheses",
            "RAG fallback provides additional context when needed"
        ],
        "Phase 4: Roadmap": [
            "Prioritizer agent identifies and ranks tasks",
            "Strategy agent develops implementation roadmap",
            "Final report generation with recommendations"
        ]
    }
    
    # Define colors for each phase
    phase_colors = {
        "Phase 1: Data Collection": "#E6F3FF",
        "Phase 2: Analysis": "#F0FFF0",
        "Phase 3: Evaluation": "#FFEBCC",
        "Phase 4: Roadmap": "#FFE6E6"
    }
    
    # Create a horizontal timeline
    ax = plt.subplot(111)
    
    # Calculate positions
    num_phases = len(phases)
    phase_width = 1.0 / num_phases
    
    # Draw the phases
    for i, (phase, tasks) in enumerate(phases.items()):
        # Phase box
        left = i * phase_width
        rect = plt.Rectangle((left, 0.6), phase_width * 0.9, 0.3, 
                            facecolor=phase_colors[phase], edgecolor='black', 
                            linewidth=1.5, alpha=0.8)
        ax.add_patch(rect)
        
        # Phase label
        plt.text(left + phase_width * 0.45, 0.75, phase, 
                ha='center', va='center', fontweight='bold', fontsize=12)
        
        # Tasks
        for j, task in enumerate(tasks):
            plt.text(left + phase_width * 0.45, 0.5 - j * 0.1, 
                    f"• {task}", ha='center', va='center', fontsize=10)
    
    # Add connecting arrows between phases
    for i in range(num_phases - 1):
        plt.arrow(
            (i + 0.9) * phase_width, 0.75, 
            0.1 * phase_width, 0, 
            head_width=0.02, head_length=0.01, 
            fc='black', ec='black'
        )
    
    # Add title
    plt.title("Proposal Analysis Implementation Roadmap", fontsize=16, fontweight='bold')
    
    # Remove axis
    plt.axis('off')
    
    # Set limits
    plt.xlim(0, 1)
    plt.ylim(0, 1)
    
    # Adjust layout
    plt.tight_layout()
    
    return plt

if __name__ == "__main__":
    workflow_plt = visualize_workflow()
    workflow_plt.savefig("workflow_visualization.png", dpi=300, bbox_inches='tight')
    
    roadmap_plt = create_roadmap_visualization()
    roadmap_plt.savefig("roadmap_visualization.png", dpi=300, bbox_inches='tight')
    
    print("Visualizations saved as workflow_visualization.png and roadmap_visualization.png")
