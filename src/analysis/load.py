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
                annotator = data.get('metadata', {}).get('annotator', '')
                for task in data['annotations']:
                    if task.get('annotations'):  # Check if task has annotations
                        for annotation in task['annotations']:
                            # Add task data and annotator to the annotation
                            annotation['task'] = task['id']
                            annotation['data'] = task['data']
                            annotation['_annotator'] = annotator
                            all_annotations.append(annotation)
            else:  # Handle direct list of annotations
                all_annotations.extend(data)
    
    return all_annotations

def parse_annotation(raw_annotation: dict) -> Tuple[Annotation, Dict[int, Set[str]]]:
    """
    Convert raw annotation JSON to Annotation object and return completed categories per turn.
    Returns (Annotation, Dict[turn_idx, Set[completed_categories]])
    """
    task_id = str(raw_annotation.get('task', ''))
    # Use annotator name from metadata if available, otherwise use completed_by
    annotator_id = raw_annotation.get('_annotator', str(raw_annotation.get('completed_by', '')))
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
            
        # Extract base category name without turn number
        category = extract_category(from_name)
        if not category:
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
            
        # Map the category to our internal names
        category_map = {
            'media_format': 'media_format',
            'topic': 'topic',
            'function_purpose': 'function_purpose',
            'multi_turn_relationship': 'multi_turn_relationship',
            'anthropomorphization': 'anthropomorphization',
            'restricted_flags': 'restricted_flags',
            'answer_form': 'answer_form',
            'self_disclosure': 'self_disclosure'
        }
        
        internal_category = category_map.get(category)
        if internal_category:
            # Only count category as completed if it has choices
            if result['value']['choices']:
                turns[turn_idx][internal_category].update(result['value']['choices'])
                completed_categories[turn_idx].add(internal_category)
    
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
    
    annotation = Annotation(
        task_id=task_id,
        annotator_id=annotator_id,
        timestamp=timestamp,
        turns=turn_annotations,
        completed_categories=completed_categories
    )
    
    return annotation, completed_categories

def load_original_tasks(batch_dir: str = "data") -> List[dict]:
    """Load original tasks from batch JSON files."""
    tasks = []
    batch_files = sorted(glob.glob(f"{batch_dir}/batch_*.json"))
    
    for batch_file in batch_files:
        with open(batch_file, 'r') as f:
            try:
                batch_data = json.load(f)
                # Extract batch number from filename
                batch_num = int(batch_file.split('_')[-1].split('.')[0])
                
                # Add batch info to each task
                for task in batch_data:
                    task['_batch_num'] = batch_num
                    # Add a hash of the conversation text to help with matching
                    conversation = task.get("data", {}).get("conversation", task.get("conversation", []))
                    conv_text = "\n".join(
                        turn["text"] for turn in conversation
                    )
                    task["_conv_hash"] = hash(conv_text)
                    tasks.append(task)
            except json.JSONDecodeError:
                print(f"Warning: Failed to parse {batch_file}")
                continue
    
    return tasks

def map_annotators_to_batches() -> Dict[str, List[dict]]:
    """Create a mapping of annotator -> list of their assigned tasks from batch files."""
    # Map of annotator name -> batch number based on filename convention
    annotator_batches = {
        'ahmet': 1,
        'anka': 2,
        'cedricwhitney': 3,
        'dayeon': 4,
        'megan': 5,
        'niloofar': 6,
        'shayne': 7,
        'victor': 8,
        'wenting': 9,
        'yuntian': 10,
        'zhiping': 11,
        'advisor': 12
    }
    
    # Load each batch and map to annotator
    annotator_tasks = {}
    for annotator, batch_num in annotator_batches.items():
        batch_file = f"data/batch_{batch_num}.json"
        try:
            with open(batch_file, 'r') as f:
                batch_data = json.load(f)
                # Add batch info to each task
                for task in batch_data:
                    task['_batch_num'] = batch_num
                    # Add a hash of the conversation text to help with matching
                    conversation = task.get("data", {}).get("conversation", task.get("conversation", []))
                    conv_text = "\n".join(
                        turn["text"] for turn in conversation
                    )
                    task["_conv_hash"] = hash(conv_text)
                annotator_tasks[annotator] = batch_data
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Warning: Failed to load batch {batch_num} for {annotator}: {e}")
            continue
    
    return annotator_tasks

def get_latest_annotations(exports_dir: str = "annotator_exports") -> Dict[str, Dict[str, Tuple[dict, datetime]]]:
    """
    Get the most recent annotation for each task by each annotator.
    Returns: Dict[annotator_name, Dict[task_hash, (annotation, timestamp)]]
    """
    latest_annotations = {}
    
    json_files = glob.glob(f"{exports_dir}/*.json")
    for json_file in json_files:
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
                if 'metadata' not in data or 'annotations' not in data:
                    continue
                    
                annotator = data['metadata']['annotator']
                if annotator not in latest_annotations:
                    latest_annotations[annotator] = {}
                
                # Process each task's annotations
                for task in data['annotations']:
                    if not task.get('annotations'):
                        continue
                        
                    # Get conversation hash for matching
                    conversation = task.get("data", {}).get("conversation", [])
                    conv_text = "\n".join(
                        turn["text"] for turn in conversation
                    )
                    conv_hash = hash(conv_text)
                    
                    # Find the latest annotation for this task
                    latest_timestamp = None
                    latest_annotation = None
                    
                    for annotation in task['annotations']:
                        timestamp = datetime.fromisoformat(annotation['created_at'].rstrip('Z'))
                        if latest_timestamp is None or timestamp > latest_timestamp:
                            latest_timestamp = timestamp
                            latest_annotation = annotation
                            # Add task data and annotator to the annotation
                            latest_annotation['task'] = task['id']
                            latest_annotation['data'] = task['data']
                            latest_annotation['_annotator'] = annotator
                    
                    if latest_annotation and latest_timestamp:
                        latest_annotations[annotator][conv_hash] = (latest_annotation, latest_timestamp)
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Warning: Failed to process {json_file}: {e}")
            continue
    
    return latest_annotations

def match_annotations(annotator_tasks: Dict[str, List[dict]], latest_annotations: Dict[str, Dict[str, Tuple[dict, datetime]]]) -> List[Task]:
    """Match annotations with their original tasks and create Task objects."""
    tasks = []
    
    # For each annotator's assigned tasks
    for annotator, assigned_tasks in annotator_tasks.items():
        # Skip if we don't have any annotations from this annotator
        if annotator not in latest_annotations:
            continue
            
        # Process each assigned task
        for task_idx, task in enumerate(assigned_tasks):
            conv_hash = task['_conv_hash']
            batch_num = task['_batch_num']
            
            # Find all annotators who have annotated this task
            task_annotations = []
            for ann_name, ann_tasks in latest_annotations.items():
                if conv_hash in ann_tasks:
                    raw_annotation, _ = ann_tasks[conv_hash]
                    # Skip empty annotations
                    if not raw_annotation.get('result'):
                        continue
                    annotation, completed_categories = parse_annotation(raw_annotation)
                    # Skip annotations with no completed categories
                    if not any(completed_categories.values()):
                        continue
                    task_annotations.append(annotation)
            
            # Only include tasks with at least 2 annotators
            if len(task_annotations) >= 2:
                # Create a task ID that reflects its position in the batch
                task_id = f"batch_{batch_num}_task_{task_idx + 1}"  # 1-based indexing for display
                tasks.append(Task(
                    task_id=task_id,
                    original_data=task,
                    annotations=task_annotations
                ))
    
    return tasks

def analyze_agreement(exports_dir: str = "annotator_exports") -> List[Task]:
    """Main function to analyze agreement between annotators."""
    # Step 1: Map annotators to their batch tasks
    print("Mapping annotators to batch tasks...")
    annotator_tasks = map_annotators_to_batches()
    
    # Step 2: Get latest annotations for each task
    print("Getting latest annotations...")
    latest_annotations = get_latest_annotations(exports_dir)
    
    # Step 3: Match annotations with tasks
    print("Matching annotations with tasks...")
    tasks = match_annotations(annotator_tasks, latest_annotations)
    
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
        conversation = task.original_data.get("data", {}).get("conversation", task.original_data.get("conversation", []))
        total_turns += len(conversation)
        
        # Get all annotators
        for annotation in task.annotations:
            if annotation.annotator_id not in annotator_counts:
                annotator_counts[annotation.annotator_id] = {cat: 0 for cat in AnnotationCategory}
                annotator_expected[annotation.annotator_id] = {cat: 0 for cat in AnnotationCategory}
        
        # For each turn, check what categories should be present
        for turn_idx in range(len(conversation)):
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
