from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict

from .types import (
    Task, AnnotationCategory, AgreementScore, TurnAnnotation,
    DisagreementExample
)

def calculate_f1_score(set1: Set[str], set2: Set[str]) -> float:
    """Calculate F1 score between two sets of annotations."""
    if not set1 and not set2:  # Both empty
        return 1.0
    if not set1 or not set2:  # One empty
        return 0.0
        
    intersection = len(set1.intersection(set2))
    precision = intersection / len(set1)
    recall = intersection / len(set2)
    
    if precision + recall == 0:
        return 0.0
    
    return 2 * (precision * recall) / (precision + recall)

def find_disagreement_examples(set1: Set[str], set2: Set[str]) -> List[str]:
    """Find examples of disagreements between two sets."""
    # Items in set1 but not in set2
    only_in_1 = set1.difference(set2)
    # Items in set2 but not in set1
    only_in_2 = set2.difference(set1)
    
    return [f"Annotator 1 only: {sorted(only_in_1)}, Annotator 2 only: {sorted(only_in_2)}"]

def get_category_values(turn: TurnAnnotation, category: AnnotationCategory) -> Optional[Set[str]]:
    """Get values for a specific category from a turn annotation."""
    if category == AnnotationCategory.MEDIA_FORMAT:
        return turn.media_format
    elif category == AnnotationCategory.TOPIC:
        return turn.topic
    elif category == AnnotationCategory.FUNCTION_PURPOSE:
        return turn.function_purpose
    elif category == AnnotationCategory.MULTI_TURN_RELATIONSHIP:
        return turn.multi_turn_relationship
    elif category == AnnotationCategory.ANTHROPOMORPHIZATION:
        return turn.anthropomorphization
    elif category == AnnotationCategory.RESTRICTED_FLAGS:
        return turn.restricted_flags
    elif category == AnnotationCategory.ANSWER_FORM:
        return turn.answer_form
    elif category == AnnotationCategory.SELF_DISCLOSURE:
        return turn.self_disclosure
    return None

def get_applicable_categories(is_response: bool) -> List[AnnotationCategory]:
    """Get list of applicable categories based on whether it's a response or prompt."""
    categories = [
        AnnotationCategory.MEDIA_FORMAT,
        AnnotationCategory.TOPIC,
        AnnotationCategory.RESTRICTED_FLAGS
    ]
    
    if is_response:
        categories.extend([
            AnnotationCategory.ANSWER_FORM,
            AnnotationCategory.SELF_DISCLOSURE
        ])
    else:
        categories.extend([
            AnnotationCategory.FUNCTION_PURPOSE,
            AnnotationCategory.MULTI_TURN_RELATIONSHIP,
            AnnotationCategory.ANTHROPOMORPHIZATION
        ])
    
    return categories

def get_turn_text(task: Task, turn_idx: int) -> str:
    """Extract the conversation text for a specific turn."""
    conversation = task.original_data.get("data", {}).get("conversation", task.original_data.get("conversation", []))
    if not conversation or turn_idx >= len(conversation):
        return "Text not available"
    return conversation[turn_idx].get('text', "Text not available")

def calculate_agreement_scores(
    tasks: List[Task],
    disagreement_threshold: float = 0.5  # Only collect examples for scores below this
) -> Tuple[
    Dict[AnnotationCategory, Dict[int, List[AgreementScore]]],  # Per-turn scores
    Dict[AnnotationCategory, List[AgreementScore]],  # Overall scores
    List[DisagreementExample]  # Major disagreement examples
]:
    """Calculate agreement scores for all categories, both per-turn and overall."""
    # Initialize score containers
    scores_by_category: Dict[AnnotationCategory, Dict[int, List[AgreementScore]]] = defaultdict(lambda: defaultdict(list))
    overall_scores: Dict[AnnotationCategory, List[AgreementScore]] = defaultdict(list)
    disagreement_examples: List[DisagreementExample] = []
    
    # Track cumulative values for overall scores, separate for each annotator
    cumulative_values: Dict[str, Dict[str, Dict[AnnotationCategory, Set[str]]]] = {}
    
    for task in tasks:
        if len(task.annotations) != 2:
            continue
            
        ann1, ann2 = task.annotations[0], task.annotations[1]
        annotator_pair = (ann1.annotator_id, ann2.annotator_id)
        pair_key = f"{ann1.annotator_id}_{ann2.annotator_id}"
        
        if pair_key not in cumulative_values:
            cumulative_values[pair_key] = {
                ann1.annotator_id: defaultdict(set),
                ann2.annotator_id: defaultdict(set)
            }
        
        # Get all unique turn indices
        all_turns = set(ann1.turns.keys()).union(set(ann2.turns.keys()))
        
        for turn_idx in all_turns:
            # Skip if either annotator doesn't have this turn
            if turn_idx not in ann1.turns or turn_idx not in ann2.turns:
                continue
                
            turn1 = ann1.turns[turn_idx]
            turn2 = ann2.turns[turn_idx]
            
            # Get applicable categories for this turn
            is_response = turn_idx % 2 == 1
            categories = get_applicable_categories(is_response)
            
            # Calculate agreement for each applicable category
            for category in categories:
                values1 = get_category_values(turn1, category)
                values2 = get_category_values(turn2, category)
                
                if values1 is None or values2 is None:
                    continue
                
                # Calculate per-turn agreement
                f1 = calculate_f1_score(values1, values2)
                disagreements = find_disagreement_examples(values1, values2) if f1 < 1.0 else None
                
                score = AgreementScore(
                    category=category,
                    turn_idx=turn_idx,
                    f1_score=f1,
                    annotator_pair=annotator_pair,
                    disagreement_examples=disagreements
                )
                
                scores_by_category[category][turn_idx].append(score)
                
                # Collect disagreement examples if score is below threshold
                if f1 < disagreement_threshold:
                    example = DisagreementExample(
                        task_id=task.task_id,
                        turn_idx=turn_idx,
                        category=category,
                        annotator1_id=ann1.annotator_id,
                        annotator2_id=ann2.annotator_id,
                        annotator1_values=values1,
                        annotator2_values=values2,
                        conversation_text=get_turn_text(task, turn_idx),
                        f1_score=f1
                    )
                    disagreement_examples.append(example)
                
                # Accumulate values for overall agreement, separate for each annotator
                cumulative_values[pair_key][ann1.annotator_id][category].update(values1)
                cumulative_values[pair_key][ann2.annotator_id][category].update(values2)
                
    # Calculate overall agreement scores
    for pair_key, annotator_values in cumulative_values.items():
        annotator1, annotator2 = pair_key.split('_')
        annotator_pair = (annotator1, annotator2)
        
        # Get the cumulative sets for each annotator
        values1_by_category = annotator_values[annotator1]
        values2_by_category = annotator_values[annotator2]
        
        # Calculate agreement for each category
        for category in set(values1_by_category.keys()).union(values2_by_category.keys()):
            values1 = values1_by_category[category]
            values2 = values2_by_category[category]
            
            f1 = calculate_f1_score(values1, values2)
            disagreements = find_disagreement_examples(values1, values2) if f1 < 1.0 else None
            
            score = AgreementScore(
                category=category,
                turn_idx=-1,  # Use -1 to indicate this is an overall score
                f1_score=f1,
                annotator_pair=annotator_pair,
                disagreement_examples=disagreements
            )
            
            overall_scores[category].append(score)
    
    # Sort disagreement examples by f1_score ascending (worst disagreements first)
    disagreement_examples.sort(key=lambda x: x.f1_score)
    
    return scores_by_category, overall_scores, disagreement_examples

def find_lowest_agreement_categories(
    scores_by_category: Dict[AnnotationCategory, Dict[int, List[AgreementScore]]],
    overall_scores: Dict[AnnotationCategory, List[AgreementScore]],
    top_n: int = 5
) -> Tuple[List[Tuple[AnnotationCategory, int, float]], List[Tuple[AnnotationCategory, float]]]:
    """Find categories with lowest agreement, both per-turn and overall."""
    # Per-turn analysis
    all_turn_scores = []
    for category, turn_scores in scores_by_category.items():
        for turn_idx, scores in turn_scores.items():
            avg_score = sum(s.f1_score for s in scores) / len(scores)
            all_turn_scores.append((category, turn_idx, avg_score))
    
    # Overall analysis
    all_overall_scores = []
    for category, scores in overall_scores.items():
        avg_score = sum(s.f1_score for s in scores) / len(scores)
        all_overall_scores.append((category, avg_score))
    
    # Sort both lists by score ascending and return top_n lowest scores
    lowest_by_turn = sorted(all_turn_scores, key=lambda x: x[2])[:top_n]
    lowest_overall = sorted(all_overall_scores, key=lambda x: x[1])[:top_n]
    
    return lowest_by_turn, lowest_overall
