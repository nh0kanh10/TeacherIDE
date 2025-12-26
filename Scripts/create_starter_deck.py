"""
Starter Deck Generator - Tạo 100+ Review Cards
v4.5 Content Fix

Giải quyết: "Có engine xịn nhưng không có content"
- Tạo 100+ cards ngay từ multi-domain packs
- Programming + Business English + API
- Immediate value cho user!
"""
import sqlite3
import json
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent.parent / '.ai_coach' / 'progress.db'
PACKS_PATH = Path(__file__).parent / 'skill_packs' / 'multi_domain.json'


class StarterDeckGenerator:
    """
    Tạo starter deck với 100+ cards từ nhiều domains
    """
    
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
    
    def load_content_packs(self) -> dict:
        """Load multi-domain content"""
        with open(PACKS_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def create_starter_deck(self):
        """
        Tạo 100+ review cards từ packs
        
        Domains:
        - Programming (30 cards)
        - Business English (40 cards)
        - API Documentation (30 cards)
        """
        packs = self.load_content_packs()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        total_created = 0
        
        print("🎴 Tạo Starter Deck...\n")
        
        # 1. Programming
        print("1️⃣ Programming Skills:")
        for skill_list in packs['programming'].values():
            for skill in skill_list:
                self._create_skill_card(cursor, skill['term'], 
                                       difficulty=skill['difficulty'],
                                       category=skill.get('category', 'programming'))
                total_created += 1
        
        print(f"   ✅ {total_created} programming cards\n")
        
        # 2. Business English
        prog_count = total_created
        print("2️⃣ Business English:")
        for category, terms in packs['business_english'].items():
            for term in terms:
                self._create_skill_card(cursor, term['term'],
                                       difficulty=term['difficulty'],
                                       category=f"business_{category}",
                                       translation=term.get('translation'))
                total_created += 1
        
        print(f"   ✅ {total_created - prog_count} business cards\n")
        
        # 3. API Documentation
        api_start = total_created
        print("3️⃣ API Documentation:")
        for category, concepts in packs['api_documentation'].items():
            for concept in concepts:
                self._create_skill_card(cursor, concept['term'],
                                       difficulty=concept['difficulty'],
                                       category=f"api_{category}",
                                       definition=concept.get('definition'))
                total_created += 1
        
        print(f"   ✅ {total_created - api_start} API cards\n")
        
        conn.commit()
        conn.close()
        
        print(f"🎉 Starter Deck Complete: {total_created} cards!")
        return total_created
    
    def _create_skill_card(self, cursor, skill_name: str,
                          difficulty: str = 'medium',
                          category: str = 'general',
                          translation: str = None,
                          definition: str = None):
        """
        Tạo 1 FSRS card
        
        Args:
            skill_name: Tên skill
            difficulty: easy/medium/hard → initial difficulty
            category: Phân loại
            translation: Bản dịch (cho business English)
            definition: Định nghĩa (cho API docs)
        """
        # Map difficulty → FSRS difficulty
        difficulty_map = {
            'easy': 3.0,
            'medium': 5.0,
            'hard': 7.0
        }
        
        initial_difficulty = difficulty_map.get(difficulty, 5.0)
        
        # Check if exists (cần skill_id, không query trực tiếp skill_name)
        # Bỏ qua check, just try insert
        pass
        
        # Get or create skill_id
        cursor.execute("SELECT id FROM skills WHERE name = ?", (skill_name,))
        row = cursor.fetchone()
        
        if not row:
            # Create skill first
            cursor.execute("""
                INSERT INTO skills (name, category, complexity)
                VALUES (?, ?, ?)
            """, (skill_name, category, int(initial_difficulty)))
            skill_id = cursor.lastrowid
        else:
            skill_id = row[0]
            # Check if card exists
            cursor.execute("""
                SELECT card_id FROM spaced_repetition 
                WHERE skill_id = ? AND user_id = ?
            """, (skill_id, 1))
            if cursor.fetchone():
                return  # Already exists
        
        # Create new FSRS card
        cursor.execute("""
            INSERT INTO spaced_repetition (
                user_id, skill_id, stability, difficulty,
                elapsed_days, scheduled_days, reps, lapses,
                state, last_review, due
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            1,  # user_id
            skill_id,
            0.0,  # stability (new card)
            initial_difficulty,
            0,  # elapsed_days
            0,  # scheduled_days
            0,  # reps
            0,  # lapses
            0,  # state (NEW)
            None,  # last_review
            datetime.now().isoformat()  # due now
        ))
        
        # Store metadata (translation/definition)
        if translation or definition:
            # TODO: Create metadata table
            pass


if __name__ == "__main__":
    generator = StarterDeckGenerator()
    
    total = generator.create_starter_deck()
    
    print(f"\n✅ Ready to review!")
    print(f"   Run: python Scripts/review_cli.py session")
