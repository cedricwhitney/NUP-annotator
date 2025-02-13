import json
import glob
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple
from datetime import datetime

from .types import Annotation, Task, TurnAnnotation, AnnotationCategory, CompletionStats, MissingAnnotation

def extract_turn_number(name: str) -> Optional[int]:
    """Extract turn number from field name (e.g., 'media_format_1' -> 0)."""
    # Note: We subtract 1 from the turn number since we want 0-based indexing
    if name.endswith('_1'):
        return 0
    elif name.endswith('_2'):
        return 1
    elif name.endswith('_3'):
        return 2
    return None

def extract_category(name: str) -> Optional[str]:
    """Extract category from field name (e.g., 'media_format_1' -> 'media_format')."""
    parts = name.rsplit('_', 1)
    if len(parts) == 2 and parts[1].isdigit():
        return parts[0]
    return None

def load_annotator_exports(exports_dir: str = "annotator_exports") -> List[dict]:
    """Load all JSON files from the annotator_exports directory."""
    json_files = glob.glob(f"{exports_dir}/*.json")
    all_annotations = []
    
    for json_file in json_files:
        with open(json_file, 'r') as f:
            data = json.load(f)
            if 'annotations' in data:  # Handle the new format with metadata
                all_annotations.extend(data['annotations'])
            else:  # Handle direct list of annotations
                all_annotations.extend(data)
    
    return all_annotations

def parse_annotation(raw_annotation: dict) -> Tuple[Annotation, Dict[int, Set[str]]]:
    """
    Convert raw annotation JSON to Annotation object and return completed categories per turn.
    Returns (Annotation, Dict[turn_idx, Set[completed_categories]])
    """
    task_id = str(raw_annotation['task'])
    annotator_id = raw_annotation['completed_by']
    timestamp = raw_annotation['created_at']
    
    # Initialize turn annotations
    turns: Dict[int, Dict[str, Set[str]]] = {}
    completed_categories: Dict[int, Set[str]] = {}
    
    # First pass: collect all annotations by turn
    for result in raw_annotation['result']:
        if 'value' not in result or 'choices' not in result['value']:
            continue
            
        from_name = result['from_name']
        turn_idx = extract_turn_number(from_name)
        if turn_idx is None:
            continue
            
        category = extract_category(from_name)
        if category is None:
            continue
            
        if turn_idx not in turns:
            turns[turn_idx] = {
                'media_format': set(),
                'topic': set(),
                'function_purpose': set(),
                'multi_turn_relationship': set(),
                'anthropomorphization': set(),
                'restricted_flags': set(),
                'answer_form': set(),
                'self_disclosure': set()
            }
            completed_categories[turn_idx] = set()
            
        # Only count category as completed if it has choices
        if result['value']['choices']:
            turns[turn_idx][category].update(result['value']['choices'])
            completed_categories[turn_idx].add(category)
    
    # Second pass: convert to TurnAnnotation objects
    turn_annotations = {}
    for turn_idx, data in turns.items():
        # Determine if this is a response turn (odd indices are responses)
        is_response = turn_idx % 2 == 1
        
        # Create turn annotation if at least one category is completed
        if completed_categories[turn_idx]:
            turn_annotations[turn_idx] = TurnAnnotation(
                media_format=data['media_format'],
                topic=data['topic'],
                function_purpose=None if is_response else data['function_purpose'],
                multi_turn_relationship=None if is_response else data['multi_turn_relationship'],
                anthropomorphization=None if is_response else data['anthropomorphization'],
                restricted_flags=data['restricted_flags'],
                answer_form=data['answer_form'] if is_response else None,
                self_disclosure=data['self_disclosure'] if is_response else None
            )
    
    return Annotation(
        task_id=task_id,
        annotator_id=annotator_id,
        timestamp=timestamp,
        turns=turn_annotations
    ), completed_categories

def load_original_tasks(sample_path: str) -> List[dict]:
    """Load original tasks from sample JSON file."""
    with open(sample_path, 'r') as f:
        tasks = json.load(f)
    
    # Add a hash of the conversation text to help with matching
    for task in tasks:
        conv_text = "\n".join(
            turn["text"] for turn in task["conversation"]
        )
        task["_conv_hash"] = hash(conv_text)
    
    return tasks

def match_annotations(raw_annotations: List[dict], original_tasks: List[dict]) -> List[Task]:
    """Match annotations from Label Studio exports with original tasks."""
    # First, build a map of conversation hash -> original task
    task_map = {
        task["_conv_hash"]: task 
        for task in original_tasks
    }
    
    # Group annotations by conversation text and annotator
    annotation_groups: Dict[int, Dict[str, List[Tuple[Annotation, Dict[int, Set[str]], datetime]]]] = {}
    
    for raw_task in raw_annotations:
        # Skip if no annotations
        if not raw_task["annotations"]:
            continue
            
        # Get conversation text
        conv_text = "\n".join(
            turn["text"] for turn in raw_task["data"]["conversation"]
        )
        conv_hash = hash(conv_text)
        
        # Skip if we can't find matching original task
        if conv_hash not in task_map:
            continue
            
        # Parse annotations
        for raw_annotation in raw_task["annotations"]:
            annotation, completed_categories = parse_annotation(raw_annotation)
            timestamp = datetime.fromisoformat(annotation.timestamp.rstrip('Z'))
            
            if conv_hash not in annotation_groups:
                annotation_groups[conv_hash] = {}
                
            if annotation.annotator_id not in annotation_groups[conv_hash]:
                annotation_groups[conv_hash][annotation.annotator_id] = []
                
            annotation_groups[conv_hash][annotation.annotator_id].append(
                (annotation, completed_categories, timestamp)
            )
    
    # Create Task objects
    tasks = []
    for conv_hash, annotator_groups in annotation_groups.items():
        original_task = task_map[conv_hash]
        final_annotations = []
        
        # For each annotator, merge their annotations
        for annotator_id, annotations in annotator_groups.items():
            # Sort annotations by timestamp
            annotations.sort(key=lambda x: x[2])
            
            # Track the most recent annotation for each turn and category
            final_turns = {}
            final_categories: Dict[int, Set[str]] = {}
            
            for annotation, completed_cats, _ in annotations:
                for turn_idx, categories in completed_cats.items():
                    if turn_idx not in final_categories:
                        final_categories[turn_idx] = set()
                    
                    # For each newly completed category in this turn
                    for category in categories:
                        if category not in final_categories[turn_idx]:
                            final_categories[turn_idx].add(category)
                            if turn_idx in annotation.turns:
                                if turn_idx not in final_turns:
                                    final_turns[turn_idx] = annotation.turns[turn_idx]
            
            if final_turns:  # Only include if there are any valid turns
                final_annotations.append(Annotation(
                    task_id=original_task.get("id", ""),
                    annotator_id=annotator_id,
                    timestamp=annotations[-1][0].timestamp,  # Use latest timestamp
                    turns=final_turns,
                    completed_categories=final_categories  # Add completed categories to annotation
                ))
        
        if len(final_annotations) >= 2:  # Only include if we have at least 2 annotators
            tasks.append(Task(
                task_id=str(original_task.get("id", "")),
                original_data=original_task,
                annotations=final_annotations
            ))
    
    return tasks

def validate_annotations(tasks: List[Task]) -> List[str]:
    """Find tasks with missing or incomplete annotations."""
    missing = []
    
    for task in tasks:
        if len(task.annotations) < 2:
            missing.append(task.task_id)
            continue
            
        # Check each annotation has at least one turn
        for annotation in task.annotations:
            if not annotation.turns:
                missing.append(task.task_id)
                break
    
    return missing

def filter_dual_annotated_tasks(tasks: List[Task]) -> List[Task]:
    """Filter for tasks that have exactly 2 different annotators."""
    return [
        task for task in tasks
        if len(task.annotations) == 2 and
        task.annotations[0].annotator_id != task.annotations[1].annotator_id
    ]

def analyze_completion_rates(tasks: List[Task]) -> CompletionStats:
    """Analyze completion rates and missing annotations across all tasks."""
    # Initialize counters
    total_tasks = len(tasks)
    total_turns = 0
    category_counts: Dict[AnnotationCategory, int] = {cat: 0 for cat in AnnotationCategory}
    annotator_counts: Dict[str, Dict[AnnotationCategory, int]] = {}
    missing_annotations: List[MissingAnnotation] = []
    
    # Track expected counts
    category_expected: Dict[AnnotationCategory, int] = {cat: 0 for cat in AnnotationCategory}
    annotator_expected: Dict[str, Dict[AnnotationCategory, int]] = {}
    
    for task in tasks:
        # Count total turns
        total_turns += len(task.original_data["conversation"])
        
        # Get all annotators
        for annotation in task.annotations:
            if annotation.annotator_id not in annotator_counts:
                annotator_counts[annotation.annotator_id] = {cat: 0 for cat in AnnotationCategory}
                annotator_expected[annotation.annotator_id] = {cat: 0 for cat in AnnotationCategory}
        
        # For each turn, check what categories should be present
        for turn_idx in range(len(task.original_data["conversation"])):
            is_response = turn_idx % 2 == 1
            
            # Determine required categories for this turn
            required_categories = {
                AnnotationCategory.MEDIA_FORMAT,
                AnnotationCategory.TOPIC,
                AnnotationCategory.RESTRICTED_FLAGS
            }
            
            if is_response:
                required_categories.update({
                    AnnotationCategory.ANSWER_FORM,
                    AnnotationCategory.SELF_DISCLOSURE
                })
            else:
                required_categories.update({
                    AnnotationCategory.FUNCTION_PURPOSE,
                    AnnotationCategory.MULTI_TURN_RELATIONSHIP,
                    AnnotationCategory.ANTHROPOMORPHIZATION
                })
            
            # Update expected counts
            for category in required_categories:
                category_expected[category] += len(task.annotations)
                for annotation in task.annotations:
                    annotator_expected[annotation.annotator_id][category] += 1
            
            # Check what's actually present
            for annotation in task.annotations:
                completed = (
                    annotation.completed_categories.get(turn_idx, set()) 
                    if hasattr(annotation, 'completed_categories') 
                    else set()
                )
                
                # Update completion counts
                for category in completed:
                    if category in required_categories:
                        category_counts[AnnotationCategory(category)] += 1
                        annotator_counts[annotation.annotator_id][AnnotationCategory(category)] += 1
                
                # Track missing categories
                for category in required_categories:
                    if category.value not in completed:
                        missing_annotations.append(MissingAnnotation(
                            task_id=task.task_id,
                            turn_idx=turn_idx,
                            category=category,
                            annotator_id=annotation.annotator_id,
                            is_response=is_response
                        ))
    
    # Calculate completion rates
    completion_by_category = {
        cat: (count / category_expected[cat] if category_expected[cat] > 0 else 0.0)
        for cat, count in category_counts.items()
    }
    
    completion_by_annotator = {
        annotator_id: {
            cat: (count / annotator_expected[annotator_id][cat] 
                  if annotator_expected[annotator_id][cat] > 0 else 0.0)
            for cat, count in counts.items()
        }
        for annotator_id, counts in annotator_counts.items()
    }
    
    return CompletionStats(
        total_tasks=total_tasks,
        total_turns=total_turns,
        completion_by_category=completion_by_category,
        completion_by_annotator=completion_by_annotator,
        missing_annotations=missing_annotations
    )

def format_completion_report(stats: CompletionStats) -> str:
    """Format completion statistics into a human-readable report."""
    lines = []
    lines.append("# Annotation Completion Report")
    lines.append(f"\n## Overview")
    lines.append(f"- Total Tasks: {stats.total_tasks}")
    lines.append(f"- Total Turns: {stats.total_turns}")
    
    lines.append("\n## Completion Rates by Category")
    # Sort categories by completion rate ascending (worst first)
    sorted_categories = sorted(
        stats.completion_by_category.items(),
        key=lambda x: x[1]
    )
    for category, rate in sorted_categories:
        lines.append(f"- {category.value}: {rate:.1%}")
    
    lines.append("\n## Completion Rates by Annotator")
    for annotator_id, rates in stats.completion_by_annotator.items():
        lines.append(f"\n### Annotator: {annotator_id}")
        # Sort categories by completion rate ascending (worst first)
        sorted_rates = sorted(rates.items(), key=lambda x: x[1])
        for category, rate in sorted_rates:
            lines.append(f"- {category.value}: {rate:.1%}")
    
    lines.append("\n## Missing Annotations")
    # Group by annotator
    missing_by_annotator: Dict[str, List[MissingAnnotation]] = {}
    for missing in stats.missing_annotations:
        if missing.annotator_id not in missing_by_annotator:
            missing_by_annotator[missing.annotator_id] = []
        missing_by_annotator[missing.annotator_id].append(missing)
    
    for annotator_id, missing_list in missing_by_annotator.items():
        lines.append(f"\n### Annotator: {annotator_id}")
        # Group by task
        missing_by_task: Dict[str, List[MissingAnnotation]] = {}
        for missing in missing_list:
            if missing.task_id not in missing_by_task:
                missing_by_task[missing.task_id] = []
            missing_by_task[missing.task_id].append(missing)
        
        for task_id, task_missing in missing_by_task.items():
            lines.append(f"\nTask {task_id}:")
            for missing in sorted(task_missing, key=lambda x: (x.turn_idx, x.category.value)):
                turn_type = "Response" if missing.is_response else "Prompt"
                lines.append(
                    f"- Turn {missing.turn_idx + 1} ({turn_type}): "
                    f"Missing {missing.category.value}"
                )
    
    return "\n".join(lines)
