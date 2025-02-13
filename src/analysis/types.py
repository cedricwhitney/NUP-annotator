from dataclasses import dataclass
from typing import Dict, List, Optional, Set
from enum import Enum

class AnnotationCategory(str, Enum):
    # Media Format
    MEDIA_FORMAT = "media_format"
    
    # Topics
    TOPIC = "topic"
    
    # Function/Purpose
    FUNCTION_PURPOSE = "function_purpose"
    
    # Multi-turn Relationship
    MULTI_TURN_RELATIONSHIP = "multi_turn_relationship"
    
    # Anthropomorphization
    ANTHROPOMORPHIZATION = "anthropomorphization"
    
    # Restricted Flags
    RESTRICTED_FLAGS = "restricted_flags"
    
    # Answer Form (only for responses)
    ANSWER_FORM = "answer_form"
    
    # Self Disclosure (only for responses)
    SELF_DISCLOSURE = "self_disclosure"

@dataclass
class TurnAnnotation:
    """Annotation data for a single turn."""
    media_format: Set[str]
    topic: Set[str]
    function_purpose: Optional[Set[str]]  # Not present in responses
    multi_turn_relationship: Optional[Set[str]]  # Not present in responses
    anthropomorphization: Optional[Set[str]]  # Not present in responses
    restricted_flags: Set[str]
    answer_form: Optional[Set[str]]  # Only present in responses
    self_disclosure: Optional[Set[str]]  # Only present in responses

@dataclass
class Annotation:
    """Complete annotation for a task by one annotator."""
    task_id: str
    annotator_id: str
    timestamp: str
    turns: Dict[int, TurnAnnotation]  # turn_idx -> TurnAnnotation
    completed_categories: Dict[int, Set[str]]  # turn_idx -> set of completed categories

@dataclass
class Task:
    """A task with its original data and all annotations."""
    task_id: str
    original_data: dict  # The original conversation data
    annotations: List[Annotation]
    
@dataclass
class AgreementScore:
    """Agreement score for a specific category in a turn."""
    category: AnnotationCategory
    turn_idx: int
    f1_score: float
    annotator_pair: tuple[str, str]
    disagreement_examples: Optional[List[str]] = None

@dataclass
class DisagreementExample:
    """Example of a disagreement between annotators."""
    task_id: str
    turn_idx: int
    category: AnnotationCategory
    annotator1_id: str
    annotator2_id: str
    annotator1_values: Set[str]
    annotator2_values: Set[str]
    conversation_text: str  # The actual text from the conversation for this turn
    f1_score: float

@dataclass
class MissingAnnotation:
    """Details about a missing category annotation."""
    task_id: str
    turn_idx: int
    category: AnnotationCategory
    annotator_id: str
    is_response: bool  # Whether this was a response turn

@dataclass
class CompletionStats:
    """Statistics about annotation completion rates."""
    total_tasks: int
    total_turns: int
    completion_by_category: Dict[AnnotationCategory, float]  # category -> completion rate
    completion_by_annotator: Dict[str, Dict[AnnotationCategory, float]]  # annotator -> category -> completion rate
    missing_annotations: List[MissingAnnotation]  # Detailed list of what's missing

@dataclass
class AgreementReport:
    """Complete agreement analysis report."""
    tasks_analyzed: int
    annotator_pairs: List[tuple[str, str]]
    # Per-turn scores
    scores_by_category: Dict[AnnotationCategory, Dict[int, List[AgreementScore]]]  # category -> turn_idx -> scores
    # Overall category scores (aggregated across turns)
    overall_category_scores: Dict[AnnotationCategory, List[AgreementScore]]  # category -> scores
    missing_annotations: List[str]  # task_ids with missing annotations
    lowest_agreement_categories: List[tuple[AnnotationCategory, int, float]]  # (category, turn_idx, score)
    lowest_agreement_overall: List[tuple[AnnotationCategory, float]]  # (category, score)
    # Examples of major disagreements
    disagreement_examples: List[DisagreementExample]  # Examples of significant disagreements
    # Completion statistics
    completion_stats: CompletionStats  # Statistics about annotation completion
