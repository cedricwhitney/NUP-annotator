import pytest
from src.analysis.types import Task, Annotation, AnnotationCategory, AgreementScore
from src.analysis.agreement import (
    calculate_f1_score,
    find_disagreement_examples,
    calculate_agreement_scores,
    find_lowest_agreement_categories
)

@pytest.fixture
def sample_annotations():
    """Create sample annotations for testing."""
    ann1 = Annotation(
        task_id="1",
        annotator_id="user1@example.com",
        turn_annotations={
            0: {
                AnnotationCategory.MEDIA_FORMAT: {"video", "image"},
                AnnotationCategory.TOPIC: {"sports"},
                AnnotationCategory.INTENT: {"inform"},
                AnnotationCategory.SENTIMENT: {"positive"}
            }
        },
        timestamp="2024-01-01T00:00:00Z"
    )
    
    ann2 = Annotation(
        task_id="1",
        annotator_id="user2@example.com",
        turn_annotations={
            0: {
                AnnotationCategory.MEDIA_FORMAT: {"video"},
                AnnotationCategory.TOPIC: {"sports", "news"},
                AnnotationCategory.INTENT: {"inform"},
                AnnotationCategory.SENTIMENT: {"neutral"}
            }
        },
        timestamp="2024-01-01T00:00:00Z"
    )
    
    return [ann1, ann2]

@pytest.fixture
def sample_task(sample_annotations):
    """Create a sample task with annotations."""
    return Task(
        task_id="1",
        original_data={"id": "1", "text": "Sample text"},
        annotations=sample_annotations
    )

def test_calculate_f1_score():
    """Test F1 score calculation."""
    # Perfect match
    assert calculate_f1_score({"a", "b"}, {"a", "b"}) == 1.0
    
    # No overlap
    assert calculate_f1_score({"a", "b"}, {"c", "d"}) == 0.0
    
    # Partial overlap
    assert calculate_f1_score({"a", "b"}, {"b", "c"}) == 0.5
    
    # Empty sets
    assert calculate_f1_score(set(), set()) == 1.0
    assert calculate_f1_score({"a"}, set()) == 0.0
    assert calculate_f1_score(set(), {"a"}) == 0.0

def test_find_disagreement_examples():
    """Test finding disagreement examples."""
    set1 = {"video", "image"}
    set2 = {"video", "audio"}
    
    examples = find_disagreement_examples(set1, set2)
    assert len(examples) == 1
    assert "image" in examples[0]
    assert "audio" in examples[0]

def test_calculate_agreement_scores(sample_task):
    """Test agreement score calculation."""
    scores = calculate_agreement_scores([sample_task])
    
    # Check that we have scores for all categories
    assert all(cat in scores for cat in AnnotationCategory)
    
    # Check specific scores
    media_scores = scores[AnnotationCategory.MEDIA_FORMAT][0]
    assert len(media_scores) == 1
    assert media_scores[0].f1_score == 2/3  # video matches, image doesn't
    
    sentiment_scores = scores[AnnotationCategory.SENTIMENT][0]
    assert len(sentiment_scores) == 1
    assert sentiment_scores[0].f1_score == 0.0  # completely different

def test_find_lowest_agreement_categories(sample_task):
    """Test finding categories with lowest agreement."""
    scores = calculate_agreement_scores([sample_task])
    lowest = find_lowest_agreement_categories(scores, top_n=2)
    
    assert len(lowest) == 2
    assert isinstance(lowest[0], tuple)
    assert len(lowest[0]) == 3  # (category, turn, score)
    
    # Sentiment should be among lowest since it has 0 agreement
    assert any(cat == AnnotationCategory.SENTIMENT for cat, _, _ in lowest)
