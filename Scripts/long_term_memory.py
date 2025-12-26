"""
Long-Term Memory System
Phase 2 Feature #5

Tracks:
- Conceptual misconceptions and corrections
- "Aha moments" for retention
- Error patterns and fixes
- Concept relationships

✅ With validation: Confidence scoring and thresholds
"""
import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from performance_guard import async_guard

DB_PATH = Path(__file__).parent.parent / '.ai_coach' / 'progress.db'

# ✅ Validation threshold per expert feedback
MIN_CONFIDENCE_THRESHOLD = 0.7  # Only surface high-confidence memories


class LongTermMemory:
    """
    Manages deep conceptual understanding and error patterns
    
    Key features:
    - Validation via confidence scoring
    - Error pattern detection
    - Concept link tracking
    """
    
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
    
    @async_guard
    def save_misconception(self, concept: str, misconception: str, 
                          correct_understanding: str, aha_moment: str = None,
                          confidence: float = 0.8):
        """
        Save a conceptual misunder standing and correction
        
        Args:
            concept: The concept name
            misconception: What user incorrectly believed
            correct_understanding: The correct understanding
            aha_moment: The insight that clicked
            confidence: Confidence in this understanding (0-1)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if concept already exists
        cursor.execute("""
            SELECT id, validation_count FROM deep_memory
            WHERE concept = ?
        """, (concept,))
        
        existing = cursor.fetchone()
        
        if existing:
            # Update existing with higher confidence
            cursor.execute("""
                UPDATE deep_memory
                SET user_misconception = ?,
                    correct_understanding = ?,
                    aha_moment = ?,
                    confidence_score = ?,
                    validation_count = validation_count + 1,
                    last_recalled = ?
                WHERE id = ?
            """, (misconception, correct_understanding, aha_moment, 
                  confidence, datetime.now().isoformat(), existing[0]))
        else:
            # Insert new
            cursor.execute("""
                INSERT INTO deep_memory (
                    concept, user_misconception, correct_understanding,
                    aha_moment, confidence_score
                ) VALUES (?, ?, ?, ?, ?)
            """, (concept, misconception, correct_understanding, aha_moment, confidence))
        
        conn.commit()
        conn.close()
    
    @async_guard
    def record_error_pattern(self, error_type: str, pattern_description: str,
                            example_code: str = None, related_concept: str = None):
        """
        Record a recurring error pattern
        
        Args:
            error_type: 'syntax', 'logic', 'concept', 'typo'
            pattern_description: How to recognize this pattern
            example_code: Code example of the error
            related_concept: Related concept name
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if pattern exists
        cursor.execute("""
            SELECT id, occurrence_count FROM error_patterns
            WHERE error_type = ? AND pattern_description = ?
        """, (error_type, pattern_description))
        
        existing = cursor.fetchone()
        
        if existing:
            # Increment count
            cursor.execute("""
                UPDATE error_patterns
                SET occurrence_count = occurrence_count + 1,
                    last_occurred = ?,
                    example_code = COALESCE(?, example_code)
                WHERE id = ?
            """, (datetime.now().isoformat(), example_code, existing[0]))
        else:
            # Insert new pattern
            cursor.execute("""
                INSERT INTO error_patterns (
                    error_type, pattern_description, example_code, related_concept
                ) VALUES (?, ?, ?, ?)
            """, (error_type, pattern_description, example_code, related_concept))
        
        conn.commit()
        conn.close()
    
    def get_validated_memories(self, min_confidence: float = MIN_CONFIDENCE_THRESHOLD) -> List[Dict]:
        """
        Get high-confidence conceptual memories
        
        ✅ Validation: Only returns memories above threshold
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                concept, user_misconception, correct_understanding,
                aha_moment, confidence_score, validation_count,
                recall_count, retention_score
            FROM deep_memory
            WHERE confidence_score >= ?
            ORDER BY confidence_score DESC, last_recalled DESC
        """, (min_confidence,))
        
        memories = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return memories
    
    def get_recurring_errors(self, min_occurrences: int = 2) -> List[Dict]:
        """
        Get recurring error patterns
        
        Focus on patterns that repeat (worth fixing)
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                error_type, pattern_description, example_code,
                occurrence_count, related_concept, fix_learned
            FROM error_patterns
            WHERE occurrence_count >= ?
                AND fix_learned = 0
            ORDER BY occurrence_count DESC
        """, (min_occurrences,))
        
        errors = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return errors
    
    def mark_error_fixed(self, error_id: int):
        """Mark an error pattern as learned/fixed"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE error_patterns
            SET fix_learned = 1
            WHERE id = ?
        """, (error_id,))
        
        conn.commit()
        conn.close()
    
    def link_concepts(self, concept_a: str, concept_b: str, 
                     link_type: str = 'related', strength: float = 0.5):
        """
        Create a link between two concepts
        
        Args:
            concept_a: First concept
            concept_b: Second concept
            link_type: 'prerequisite', 'related', 'opposite', 'example'
            strength: Link strength (0-1)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO concept_links (
                concept_a, concept_b, link_type, strength
            ) VALUES (?, ?, ?, ?)
        """, (concept_a, concept_b, link_type, strength))
        
        conn.commit()
        conn.close()
    
    def get_related_concepts(self, concept: str, min_strength: float = 0.3) -> List[Dict]:
        """Get concepts related to a given concept"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT concept_b as related_concept, link_type, strength
            FROM concept_links
            WHERE concept_a = ? AND strength >= ?
            ORDER BY strength DESC
        """, (concept, min_strength))
        
        related = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return related


if __name__ == "__main__":
    # Demo
    memory = LongTermMemory()
    
    print("💾 Long-Term Memory Demo\n")
    
    # 1. Save a misconception
    print("1. Saving misconception...")
    memory.save_misconception(
        concept="Python Lists",
        misconception="Lists are immutable like strings",
        correct_understanding="Lists are mutable - can be changed in place",
        aha_moment="When I tried list.append() and it worked!",
        confidence=0.9
    )
    
    # 2. Record error pattern
    print("2. Recording error pattern...")
    memory.record_error_pattern(
        error_type="syntax",
        pattern_description="Forgetting colon after if statement",
        example_code="if x > 5\n    print(x)",
        related_concept="Python Conditionals"
    )
    
    # 3. Link concepts
    print("3. Linking concepts...")
    memory.link_concepts("Python Lists", "Python Loops", "related", 0.8)
    
    # 4. Retrieve validated memories
    print("\n📚 Validated Memories (confidence >= 0.7):")
    memories = memory.get_validated_memories()
    for m in memories:
        print(f"\n  Concept: {m['concept']}")
        print(f"  Misconception: {m['user_misconception']}")
        print(f"  Correct: {m['correct_understanding']}")
        print(f"  Confidence: {m['confidence_score']:.0%}")
    
    # 5. Get recurring errors
    print("\n⚠️ Recurring Errors:")
    errors = memory.get_recurring_errors(min_occurrences=1)
    for e in errors:
        print(f"\n  Type: {e['error_type']}")
        print(f"  Pattern: {e['pattern_description']}")
        print(f"  Occurrences: {e['occurrence_count']}")
    
    # 6. Get related concepts
    print("\n🔗 Related to 'Python Lists':")
    related = memory.get_related_concepts("Python Lists")
    for r in related:
        print(f"  - {r['related_concept']} ({r['link_type']}, strength: {r['strength']:.0%})")
