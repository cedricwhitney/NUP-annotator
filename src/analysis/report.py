from typing import Dict, List, Set
import json
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from .types import Task, AnnotationCategory, AgreementScore, AgreementReport
from .agreement import calculate_agreement_scores, find_lowest_agreement_categories
from .load import validate_annotations

def generate_agreement_matrix(scores_by_category: Dict[AnnotationCategory, Dict[int, List[AgreementScore]]]) -> pd.DataFrame:
    """Generate a matrix of agreement scores by category and turn."""
    data = []
    
    for category in AnnotationCategory:
        if category in scores_by_category:
            for turn_idx, scores in scores_by_category[category].items():
                avg_score = sum(s.f1_score for s in scores) / len(scores)
                data.append({
                    'Category': category.value,
                    'Turn': turn_idx + 1,  # Convert to 1-based indexing for display
                    'Agreement Score': avg_score
                })
    
    df = pd.DataFrame(data)
    return pd.pivot_table(
        df,
        values='Agreement Score',
        index='Category',
        columns='Turn',
        fill_value=0
    )

def generate_overall_agreement_table(overall_scores: Dict[AnnotationCategory, List[AgreementScore]]) -> pd.DataFrame:
    """Generate a table of overall agreement scores by category."""
    data = []
    
    for category in AnnotationCategory:
        if category in overall_scores:
            scores = overall_scores[category]
            avg_score = sum(s.f1_score for s in scores) / len(scores)
            data.append({
                'Category': category.value,
                'Overall Agreement Score': avg_score
            })
    
    return pd.DataFrame(data).sort_values('Overall Agreement Score', ascending=False)

def plot_agreement_heatmap(matrix: pd.DataFrame, output_path: str = "agreement_heatmap.png"):
    """Generate a heatmap visualization of agreement scores."""
    plt.figure(figsize=(12, 8))
    sns.heatmap(
        matrix,
        annot=True,
        cmap='RdYlGn',
        vmin=0,
        vmax=1,
        center=0.5,
        fmt='.2f'
    )
    plt.title('Inter-rater Agreement Scores by Category and Turn')
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

def plot_overall_agreement_bars(overall_scores: pd.DataFrame, output_path: str = "overall_agreement.png"):
    """Generate a bar plot of overall agreement scores."""
    plt.figure(figsize=(12, 6))
    sns.barplot(
        data=overall_scores,
        x='Category',
        y='Overall Agreement Score',
        color='skyblue'
    )
    plt.xticks(rotation=45, ha='right')
    plt.title('Overall Inter-rater Agreement Scores by Category')
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

def generate_report(tasks: List[Task], output_dir: str = "reports") -> AgreementReport:
    """Generate a comprehensive agreement report."""
    # Ensure output directory exists
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Calculate agreement scores
    scores_by_category, overall_scores, disagreement_examples = calculate_agreement_scores(tasks)
    
    # Get annotator pairs
    annotator_pairs = list({
        (ann1.annotator_id, ann2.annotator_id)
        for task in tasks
        if len(task.annotations) >= 2
        for ann1, ann2 in [(task.annotations[0], task.annotations[1])]
    })
    
    # Find problematic tasks
    missing_annotations = validate_annotations(tasks)
    
    # Find lowest agreement categories
    lowest_by_turn, lowest_overall = find_lowest_agreement_categories(scores_by_category, overall_scores)
    
    # Generate agreement matrix and plot
    matrix = generate_agreement_matrix(scores_by_category)
    plot_agreement_heatmap(matrix, f"{output_dir}/agreement_heatmap.png")
    
    # Generate overall agreement table and plot
    overall_table = generate_overall_agreement_table(overall_scores)
    plot_overall_agreement_bars(overall_table, f"{output_dir}/overall_agreement.png")
    
    # Create report object
    report = AgreementReport(
        tasks_analyzed=len(tasks),
        annotator_pairs=annotator_pairs,
        scores_by_category=scores_by_category,
        overall_category_scores=overall_scores,
        missing_annotations=missing_annotations,
        lowest_agreement_categories=lowest_by_turn,
        lowest_agreement_overall=[(cat, score) for cat, score in lowest_overall],
        disagreement_examples=disagreement_examples
    )
    
    # Save detailed report as JSON
    with open(f"{output_dir}/detailed_report.json", 'w') as f:
        json.dump({
            'tasks_analyzed': report.tasks_analyzed,
            'annotator_pairs': [list(pair) for pair in report.annotator_pairs],
            'lowest_agreement_categories': [
                {
                    'category': cat.value,
                    'turn': turn,
                    'score': score
                }
                for cat, turn, score in report.lowest_agreement_categories
            ],
            'lowest_agreement_overall': [
                {
                    'category': cat.value,
                    'score': score
                }
                for cat, score in report.lowest_agreement_overall
            ],
            'disagreement_examples': [
                {
                    'task_id': ex.task_id,
                    'turn': ex.turn_idx + 1,  # Convert to 1-based indexing for display
                    'category': ex.category.value,
                    'annotator1': {
                        'id': ex.annotator1_id,
                        'values': list(ex.annotator1_values)
                    },
                    'annotator2': {
                        'id': ex.annotator2_id,
                        'values': list(ex.annotator2_values)
                    },
                    'conversation_text': ex.conversation_text,
                    'f1_score': ex.f1_score
                }
                for ex in disagreement_examples
            ],
            'missing_annotations': report.missing_annotations
        }, f, indent=2)
    
    # Save agreement matrices as CSV
    matrix.to_csv(f"{output_dir}/agreement_matrix.csv")
    overall_table.to_csv(f"{output_dir}/overall_agreement.csv")
    
    return report

def format_report_summary(report: AgreementReport) -> str:
    """Format a human-readable summary of the agreement report."""
    summary = []
    summary.append("# Inter-rater Agreement Analysis Report")
    summary.append(f"\n## Overview")
    summary.append(f"- Tasks Analyzed: {report.tasks_analyzed}")
    summary.append(f"- Annotator Pairs: {len(report.annotator_pairs)}")
    
    summary.append("\n## Overall Category Agreement")
    for category, score in report.lowest_agreement_overall:
        summary.append(f"- {category.value}: {score:.2f}")
    
    summary.append("\n## Lowest Agreement Categories by Turn")
    for category, turn, score in report.lowest_agreement_categories:
        summary.append(f"- {category.value} (Turn {turn + 1}): {score:.2f}")
    
    if report.disagreement_examples:
        # Group examples by category
        examples_by_category = {}
        for ex in report.disagreement_examples:
            if ex.category not in examples_by_category:
                examples_by_category[ex.category] = []
            examples_by_category[ex.category].append(ex)
        
        # Sort categories by worst average F1 score
        categories_by_severity = sorted(
            examples_by_category.items(),
            key=lambda x: sum(ex.f1_score for ex in x[1]) / len(x[1])
        )
        
        summary.append("\n## Major Disagreements by Category")
        for category, examples in categories_by_severity:
            # Sort examples by F1 score (worst first)
            examples.sort(key=lambda x: x.f1_score)
            
            # Take worst 3 examples for this category
            worst_examples = examples[:3]
            
            summary.append(f"\n### {category.value}")
            summary.append(f"Found {len(examples)} significant disagreements. Here are the worst examples:")
            
            for ex in worst_examples:
                summary.append(f"\n#### Task {ex.task_id}, Turn {ex.turn_idx + 1} (F1: {ex.f1_score:.2f})")
                summary.append(f"\nConversation Text:")
                summary.append(f"```\n{ex.conversation_text}\n```")
                summary.append(f"\nAnnotator Choices:")
                summary.append(f"- {ex.annotator1_id}:")
                for value in sorted(ex.annotator1_values):
                    summary.append(f"  - {value}")
                summary.append(f"- {ex.annotator2_id}:")
                for value in sorted(ex.annotator2_values):
                    summary.append(f"  - {value}")
    
    if report.missing_annotations:
        summary.append("\n## Tasks with Missing Annotations")
        summary.append(f"- Count: {len(report.missing_annotations)}")
        summary.append("- Task IDs: " + ", ".join(report.missing_annotations[:5]) + 
                      ("..." if len(report.missing_annotations) > 5 else ""))
    
    summary.append("\n## Files Generated")
    summary.append("- agreement_heatmap.png: Visualization of per-turn agreement scores")
    summary.append("- overall_agreement.png: Bar plot of overall category agreement")
    summary.append("- agreement_matrix.csv: Detailed per-turn agreement scores")
    summary.append("- overall_agreement.csv: Overall agreement scores by category")
    summary.append("- detailed_report.json: Complete analysis results with disagreement examples")
    
    return "\n".join(summary)
