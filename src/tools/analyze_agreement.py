#!/usr/bin/env python3
"""
Script to analyze inter-rater agreement between annotators.
"""

import argparse
from pathlib import Path

from src.analysis.load import analyze_agreement
from src.analysis.report import generate_report, format_report_summary

def main():
    parser = argparse.ArgumentParser(description="Analyze inter-rater agreement between annotators.")
    parser.add_argument(
        "--exports-dir",
        default="annotator_exports",
        help="Directory containing annotator export JSON files"
    )
    parser.add_argument(
        "--output-dir",
        default="reports",
        help="Directory to save report outputs"
    )
    args = parser.parse_args()

    # Load and process annotations
    print("Analyzing inter-annotator agreement...")
    tasks = analyze_agreement(args.exports_dir)
    
    print(f"Found {len(tasks)} tasks with multiple annotators")
    
    # Generate report
    print("\nGenerating agreement report...")
    report = generate_report(tasks, args.output_dir)
    
    # Print summary
    print("\n" + format_report_summary(report))
    print(f"\nDetailed results saved to {args.output_dir}/")

if __name__ == "__main__":
    main() 