#!/usr/bin/env python3
"""
Script to analyze inter-rater agreement between annotators.
"""

import argparse
from pathlib import Path

from src.analysis.load import (
    load_annotator_exports,
    load_original_tasks,
    match_annotations,
    filter_dual_annotated_tasks
)
from src.analysis.report import generate_report, format_report_summary

def main():
    parser = argparse.ArgumentParser(description="Analyze inter-rater agreement between annotators.")
    parser.add_argument(
        "--exports-dir",
        default="annotator_exports",
        help="Directory containing annotator export JSON files"
    )
    parser.add_argument(
        "--sample-path",
        default="data/cedric_120_sample.json",
        help="Path to original sample tasks JSON"
    )
    parser.add_argument(
        "--output-dir",
        default="reports",
        help="Directory to save report outputs"
    )
    args = parser.parse_args()

    # Load and process annotations
    print("Loading annotations...")
    raw_annotations = load_annotator_exports(args.exports_dir)
    original_tasks = load_original_tasks(args.sample_path)
    
    print("Matching annotations to tasks...")
    tasks = match_annotations(raw_annotations, original_tasks)
    
    print("Filtering for dual-annotated tasks...")
    dual_tasks = filter_dual_annotated_tasks(tasks)
    
    print(f"Found {len(dual_tasks)} tasks with exactly 2 annotators")
    
    # Generate report
    print("\nGenerating agreement report...")
    report = generate_report(dual_tasks, args.output_dir)
    
    # Print summary
    print("\n" + format_report_summary(report))
    print(f"\nDetailed results saved to {args.output_dir}/")

if __name__ == "__main__":
    main() 