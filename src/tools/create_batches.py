import json
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict

class BatchCreator:
    def __init__(
        self,
        num_raters: int = 12,
        num_tasks: int = 120,
        tasks_per_rater: int = 20,
        raters_per_task: int = 2,
        max_turns: int = 10
    ):
        self.num_raters = num_raters
        self.num_tasks = num_tasks
        self.tasks_per_rater = tasks_per_rater
        self.raters_per_task = raters_per_task
        self.max_turns = max_turns
        
        # Initialize assignments
        self.assignments = defaultdict(set)  # rater -> set of tasks
        self.task_raters = defaultdict(set)  # task -> set of raters
        
        # Validate inputs
        self._validate_inputs()
    
    def _validate_inputs(self):
        """Validate input parameters."""
        min_tasks_per_rater = (self.num_tasks * self.raters_per_task) / self.num_raters
        if self.tasks_per_rater < min_tasks_per_rater:
            raise ValueError(
                f"Tasks per rater ({self.tasks_per_rater}) is too low. "
                f"Need at least {min_tasks_per_rater:.1f} tasks per rater to ensure "
                f"{self.raters_per_task} raters per task."
            )
    
    def _get_rater_scores(self) -> Dict[int, float]:
        """Get scores for each rater based on their current workload."""
        scores = {}
        for rater in range(self.num_raters):
            if len(self.assignments[rater]) >= self.tasks_per_rater:
                scores[rater] = float('inf')
            else:
                scores[rater] = len(self.assignments[rater]) / self.tasks_per_rater
        return scores
    
    def _get_overlap_counts(self) -> Dict[Tuple[int, int], int]:
        """Get current overlap counts between all rater pairs."""
        overlaps = defaultdict(int)
        for task, raters in self.task_raters.items():
            rater_list = sorted(raters)
            for i, r1 in enumerate(rater_list):
                for r2 in rater_list[i+1:]:
                    overlaps[(r1, r2)] += 1
        return overlaps
    
    def _assign_task(self, task: int) -> bool:
        """
        Assign raters to a task using a greedy approach that maintains balance.
        Returns True if assignment was successful.
        """
        # Get current rater scores and overlaps
        rater_scores = self._get_rater_scores()
        overlap_counts = self._get_overlap_counts()
        
        # Calculate target overlap
        total_overlaps = (self.num_tasks * self.raters_per_task * (self.raters_per_task - 1)) // 2
        num_pairs = (self.num_raters * (self.num_raters - 1)) // 2
        target_overlap = total_overlaps / num_pairs
        
        while len(self.task_raters[task]) < self.raters_per_task:
            best_score = float('inf')
            best_rater = None
            
            current_raters = self.task_raters[task]
            
            for rater in range(self.num_raters):
                if rater_scores[rater] == float('inf') or rater in current_raters:
                    continue
                
                # Calculate overlap penalty
                overlap_penalty = 0
                for existing_rater in current_raters:
                    pair = tuple(sorted([rater, existing_rater]))
                    current_overlap = overlap_counts.get(pair, 0)
                    overlap_penalty += abs(current_overlap + 1 - target_overlap)
                
                score = rater_scores[rater] + (overlap_penalty / self.num_raters)
                
                if score < best_score:
                    best_score = score
                    best_rater = rater
            
            if best_rater is None:
                return False
            
            # Make the assignment
            self.assignments[best_rater].add(task)
            self.task_raters[task].add(best_rater)
            
            # Update scores and overlaps
            rater_scores[best_rater] = len(self.assignments[best_rater]) / self.tasks_per_rater
            for other_rater in current_raters:
                pair = tuple(sorted([best_rater, other_rater]))
                overlap_counts[pair] = overlap_counts.get(pair, 0) + 1
        
        return True
    
    def create_assignments(self) -> Tuple[bool, Dict[int, Set[int]]]:
        """Create balanced assignments of tasks to raters."""
        # Clear any existing assignments
        self.assignments.clear()
        self.task_raters.clear()
        
        # Sort tasks by ID to ensure deterministic assignment
        tasks = list(range(self.num_tasks))
        
        # First pass: assign one rater to each task
        for task in tasks:
            rater = task % self.num_raters
            self.assignments[rater].add(task)
            self.task_raters[task].add(rater)
        
        # Second pass: assign remaining raters
        for task in tasks:
            if not self._assign_task(task):
                return False, {}
        
        return True, dict(self.assignments)
    
    def _transform_conversation(self, conversation: List[Dict]) -> Dict:
        """Transform a conversation into the Label Studio format."""
        transformed = {
            "conversation": [],
            "turn_dialogues": []
        }
        
        # Process each message
        for idx, msg in enumerate(conversation):
            # Create a copy and standardize role
            processed_msg = msg.copy()
            processed_msg["role"] = "User" if idx % 2 == 0 else "LLM"
            
            # Ensure text and content fields exist
            if "content" in processed_msg and "text" not in processed_msg:
                processed_msg["text"] = processed_msg["content"]
            elif "text" in processed_msg and "content" not in processed_msg:
                processed_msg["content"] = processed_msg["text"]
            elif "text" not in processed_msg and "content" not in processed_msg:
                processed_msg["text"] = ""
                processed_msg["content"] = ""
            
            transformed["conversation"].append(processed_msg)
        
        # Create turn dialogues
        actual_turns = (len(conversation) + 1) // 2  # Round up to include partial turns
        actual_turns = min(actual_turns, self.max_turns)
        
        for turn_idx in range(actual_turns):
            start_idx = turn_idx * 2
            end_idx = min(start_idx + 2, len(conversation))
            
            # Get messages for this turn
            turn_dialogue = []
            for idx in range(start_idx, end_idx):
                msg = conversation[idx].copy()
                msg["role"] = "User" if (idx - start_idx) % 2 == 0 else "LLM"
                turn_dialogue.append(msg)
            
            # Add empty LLM response if needed
            if len(turn_dialogue) == 1:
                turn_dialogue.append({"role": "LLM", "text": "", "content": ""})
            
            # Only add turn if it has content
            if any(msg.get("text") or msg.get("content") for msg in turn_dialogue):
                transformed[f"turn{turn_idx+1}_dialogue"] = turn_dialogue
        
        return transformed

def create_batch_files(
    master_file: str = "data/master_sample_file.json",
    output_dir: str = "data",
    num_raters: int = 12,
    tasks_per_rater: int = 20,
    raters_per_task: int = 2,
    max_turns: int = 10
):
    """Create balanced and transformed batch files from the master file."""
    # Load master file
    with open(master_file, 'r', encoding='utf-8') as f:
        master_data = json.load(f)
    
    num_tasks = len(master_data)
    print(f"📊 Creating balanced batches for {num_tasks} tasks")
    print(f"   • {num_raters} raters")
    print(f"   • {tasks_per_rater} tasks per rater")
    print(f"   • {raters_per_task} raters per task")
    
    # Create assignments
    creator = BatchCreator(
        num_raters=num_raters,
        num_tasks=num_tasks,
        tasks_per_rater=tasks_per_rater,
        raters_per_task=raters_per_task,
        max_turns=max_turns
    )
    
    success, assignments = creator.create_assignments()
    if not success:
        print("❌ Failed to create balanced assignments")
        return False
    
    # Create batch files
    for rater_id, task_indices in assignments.items():
        # Get tasks for this rater
        batch_tasks = []
        for idx in task_indices:
            task = master_data[idx]
            conversation = task["data"]["conversation"]
            conversation_id = task["data"]["conversation_id"]
            
            # Create transformed task
            transformed_task = {
                "id": conversation_id,
                "data": creator._transform_conversation(conversation)
            }
            transformed_task["data"]["conversation_id"] = conversation_id
            
            batch_tasks.append(transformed_task)
        
        # Save batch file
        batch_file = Path(output_dir) / f"batch_{rater_id + 1}.json"
        with open(batch_file, 'w', encoding='utf-8') as f:
            json.dump(batch_tasks, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Created batch_{rater_id + 1}.json with {len(task_indices)} tasks")
    
    # Print overlap statistics
    print("\n📈 Overlap Statistics:")
    overlaps = defaultdict(int)
    for rater1 in range(num_raters):
        for rater2 in range(rater1 + 1, num_raters):
            overlap = len(assignments[rater1] & assignments[rater2])
            overlaps[overlap] += 1
            print(f"   • Raters {rater1 + 1} and {rater2 + 1}: {overlap} shared tasks")
    
    print("\n🔄 Overlap Distribution:")
    for overlap, count in sorted(overlaps.items()):
        print(f"   • {overlap} shared tasks: {count} rater pairs")
    
    return True

def main():
    # Parameters
    num_raters = 12
    num_tasks = 120
    tasks_per_rater = 20
    raters_per_task = 2
    max_turns = 10
    
    master_file = "data/master_sample_file.json"
    output_dir = "data"
    
    if create_batch_files(
        master_file=master_file,
        output_dir=output_dir,
        num_raters=num_raters,
        tasks_per_rater=tasks_per_rater,
        raters_per_task=raters_per_task,
        max_turns=max_turns
    ):
        print("\n📋 Next steps:")
        print("1. Review the batch files")
        print("2. Import them into Label Studio")
    else:
        print("❌ Failed to create batch files")

if __name__ == "__main__":
    main() 