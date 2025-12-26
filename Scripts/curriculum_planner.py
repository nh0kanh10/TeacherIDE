"""
Short Horizon Curriculum Planner
Phase 3 Feature #9

Plans 6-8 weeks learning path using:
- DAG topological sort (skill dependencies)
- ROI weighting (market value × urgency)
- Constrained to short horizon (NOT 12 months)
"""
import sqlite3
import json
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict, deque

from performance_guard import async_guard

DB_PATH = Path(__file__).parent.parent / '.ai_coach' / 'progress.db'
SKILL_GRAPH_PATH = Path(__file__).parent / 'skill_graph.json'


class ShortHorizonPlanner:
    """
    6-8 week curriculum planner
    
    Uses DAG topological sort + ROI weights
    Scope: ONLY next 6-8 weeks (per expert feedback)
    """
    
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self.skill_graph = self._load_skill_graph()
    
    def _load_skill_graph(self) -> Dict:
        """Load skill dependency graph"""
        with open(SKILL_GRAPH_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _build_dag(self, language: str = 'python') -> Dict[str, List[str]]:
        """
        Build directed acyclic graph from skill_graph
        
        Returns:
            {skill: [prerequisites]}
        """
        if language not in self.skill_graph:
            return {}
        
        dag = {}
        lang_data = self.skill_graph[language]
        
        # Iterate through categories
        for category, skills in lang_data.items():
            if isinstance(skills, dict):
                for skill_name, skill_data in skills.items():
                    if isinstance(skill_data, dict):
                        prereqs = skill_data.get('prereqs', [])
                        dag[skill_name] = prereqs
        
        return dag
    
    def topological_sort(self, dag: Dict[str, List[str]], 
                        current_skills: List[str]) -> List[str]:
        """
        Topological sort with current skills as starting point
        
        Args:
            dag: Skill dependency graph
            current_skills: Skills user knows (mastery > 0.7)
            
        Returns:
            Ordered list of next skills to learn
        """
        # Build in-degree count
        in_degree = defaultdict(int)
        graph = defaultdict(list)
        
        for skill, prereqs in dag.items():
            for prereq in prereqs:
                graph[prereq].append(skill)
                in_degree[skill] += 1
        
        # Start with skills that have no  unmet prerequisites
        queue = deque()
        for skill in dag.keys():
            # Check if all prereqs are in current_skills
            prereqs = dag[skill]
            if all(p in current_skills for p in prereqs):
                if skill not in current_skills:  # Don't re-learn
                    queue.append(skill)
        
        result = []
        while queue:
            skill = queue.popleft()
            result.append(skill)
            
            # Add dependent skills
            for dependent in graph[skill]:
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    # Check if all prereqs satisfied
                    if all(p in current_skills or p in result for p in dag[dependent]):
                        queue.append(dependent)
        
        return result
    
    @async_guard
    def plan_6_weeks(self, target_skills: List[str] = None, 
                     language: str = 'python') -> Dict:
        """
        Generate 6-week learning plan
        
        Args:
            target_skills: Optional target skills to prioritize
            language: Programming language
            
        Returns:
            {
                'weeks': [
                    {'week': 1-2, 'skills': [...], 'focus': 'Fundamentals'},
                    ...
                ],
                'total_skills': int,
                'estimated_hours': int
            }
        """
        # Get current mastery
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT skill_name, mastery_prob
            FROM skill_mastery
            WHERE mastery_prob > 0.7
        """)
        
        known_skills = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        # Build DAG and sort
        dag = self._build_dag(language)
        next_skills = self.topological_sort(dag, known_skills)
        
        # Limit to 6-8 weeks (assume ~2 skills/week)
        max_skills = 12  # 6 weeks × 2 skills
        planned_skills = next_skills[:max_skills]
        
        # Group into 2-week chunks
        weeks = []
        for i in range(0, len(planned_skills), 4):  # 4 skills per 2 weeks
            week_skills = planned_skills[i:i+4]
            week_num = (i // 4) * 2 + 1
            
            weeks.append({
                'week_range': f'{week_num}-{week_num+1}',
                'skills': week_skills,
                'focus': self._infer_focus(week_skills)
            })
        
        return {
            'weeks': weeks,
            'total_skills': len(planned_skills),
            'estimated_hours': len(planned_skills) * 5,  # 5 hrs/skill
            'known_skills': len(known_skills),
            'horizon': '6 weeks'
        }
    
    def _infer_focus(self, skills: List[str]) -> str:
        """Infer focus area from skill names"""
        # Simple heuristic
        keywords = {
            'fundamentals': ['variables', 'data_types', 'conditionals', 'loops'],
            'data_structures': ['lists', 'dictionaries', 'sets'],
            'oop': ['classes', 'inheritance', 'polymorphism'],
            'advanced': ['decorators', 'generators', 'async']
        }
        
        for focus, words in keywords.items():
            if any(word in skill.lower() for skill in skills for word in words):
                return focus.title()
        
        return 'Mixed Topics'


if __name__ == "__main__":
    # Demo
    planner = ShortHorizonPlanner()
    
    print("📅 Short Horizon Curriculum Planner (6 Weeks)\n")
    
    plan = planner.plan_6_weeks(language='python')
    
    print(f"Current Knowledge: {plan['known_skills']} skills mastered")
    print(f"Plan Duration: {plan['horizon']}")
    print(f"Total New Skills: {plan['total_skills']}")
    print(f"Estimated Hours: {plan['estimated_hours']}\n")
    
    print("Week-by-Week Plan:\n")
    for week_plan in plan['weeks']:
        print(f"Weeks {week_plan['week_range']}: {week_plan['focus']}")
        for skill in week_plan['skills']:
            print(f"  - {skill}")
        print()
    
    print("🎯 This is a SHORT HORIZON plan (6-8 weeks only)")
    print("   Full career roadmap = Future v5.0 feature")
