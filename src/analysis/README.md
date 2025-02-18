# Inter-rater Agreement Analysis

This module provides tools for analyzing inter-rater agreement between annotators in the conversation annotation project.

## Overview

The analysis module consists of several components:

- `agreement.py`: Core agreement calculation logic
- `load.py`: Data loading and preprocessing utilities
- `report.py`: Report generation and visualization
- `types.py`: Type definitions and data structures

## Usage

The main analysis script can be run from the project root:

```bash
python src/tools/analyze_agreement.py
```

### Command Line Options

- `--exports-dir`: Directory containing annotator export JSON files (default: "annotator_exports")
- `--output-dir`: Directory to save report outputs (default: "reports")

### Output Files

The analysis generates several output files in the specified output directory:

1. `agreement_heatmap.png`: Visualization of per-turn agreement scores
2. `overall_agreement.png`: Bar plot of overall category agreement
3. `agreement_matrix.csv`: Detailed per-turn agreement scores
4. `overall_agreement.csv`: Overall agreement scores by category
5. `detailed_report.json`: Complete analysis results with disagreement examples

## Agreement Metrics

The analysis calculates agreement using the following metrics:

- **F1 Score**: Used to measure agreement between sets of annotations
- **Per-turn Agreement**: Agreement scores calculated for each conversation turn
- **Overall Agreement**: Aggregate agreement scores across all turns
- **Category-specific Agreement**: Separate scores for each annotation category

### Annotation Categories

The following categories are analyzed:

- Media Format
- Topic
- Function/Purpose
- Multi-turn Relationship
- Anthropomorphization
- Restricted Flags
- Answer Form (responses only)
- Self Disclosure (responses only)

## Report Details

The generated report includes:

1. **Overview Statistics**
   - Number of tasks analyzed
   - Number of annotator pairs
   - Total turns analyzed

2. **Agreement Scores**
   - Per-category agreement scores
   - Per-turn agreement scores
   - Lowest agreement categories

3. **Disagreement Analysis**
   - Examples of major disagreements
   - Detailed breakdown by category
   - Conversation context for disagreements

4. **Completion Statistics**
   - Annotation completion rates by category
   - Completion rates by annotator
   - Missing annotation details

## Implementation Details

### Data Loading (`load.py`)

- Loads annotations from JSON exports
- Matches annotations with original tasks
- Handles batch processing and annotator mapping

### Agreement Calculation (`agreement.py`)

- Implements F1 score calculation
- Handles category-specific agreement logic
- Identifies significant disagreements

### Report Generation (`report.py`)

- Generates visualizations using matplotlib/seaborn
- Creates detailed JSON reports
- Formats human-readable summaries

### Type System (`types.py`)

- Defines data structures for annotations
- Implements category enums
- Provides type safety for analysis 