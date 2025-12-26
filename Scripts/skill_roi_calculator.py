"""
Skill ROI Calculator - v3.0
Calculates Return on Investment for programming skills using market data

Improved Formula (based on expert feedback):
ROI(skill) = (Market_Value × Demand_Trend) / Learning_Cost
Learning_Cost = Complexity × (1 - Current_Mastery_Prob)
"""
import json
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
import requests

DB_PATH = Path(__file__).parent.parent / '.ai_coach' / 'progress.db'
CACHE_DURATION_DAYS = 90  # Cache market data for 3 months

# Skill complexity ratings (1-10) - Can be expanded
SKILL_COMPLEXITY = {
    # Languages
    "python": 3,
    "javascript": 4,
    "java": 6,
    "c#": 6,
    "rust": 9,
    "go": 5,
    "typescript": 5,
    
    # Frameworks
    "react": 5,
    "django": 6,
    "flask": 4,
    "spring_boot": 7,
    "asp.net_core": 7,
    
    # Domains
    "machine_learning": 8,
    "data_engineering": 7,
    "devops": 6,
    "cloud_infrastructure": 6,
    "web_scraping": 3,
    
    # Tools
    "docker": 5,
    "kubernetes": 8,
    "terraform": 6,
    "git": 3,
    "sql": 4
}

# Market data (Mock - In production, fetch from Stack Overflow API)
MARKET_DATA = {
    "python": {"salary": 75000, "trend": 1.2},
    "javascript": {"salary": 72000, "trend": 1.1},
    "java": {"salary": 78000, "trend": 0.9},
    "c#": {"salary": 77000, "trend": 1.0},
    "rust": {"salary": 88000, "trend": 1.5},
    "go": {"salary": 82000, "trend": 1.3},
    "typescript": {"salary": 79000, "trend": 1.4},
    
    "react": {"salary": 76000, "trend": 1.3},
    "django": {"salary": 74000, "trend": 1.1},
    "spring_boot": {"salary": 81000, "trend": 1.0},
    
    "machine_learning": {"salary": 90000, "trend": 1.6},
    "data_engineering": {"salary": 85000, "trend": 1.4},
    "devops": {"salary": 84000, "trend": 1.3},
    "cloud_infrastructure": {"salary": 83000, "trend": 1.3},
    
    "docker": {"salary": 78000, "trend": 1.2},
    "kubernetes": {"salary": 86000, "trend": 1.4},
    "terraform": {"salary": 81000, "trend": 1.3},
    "sql": {"salary": 70000, "trend": 0.9}
}

def get_current_mastery(skill_name):
    """
    Get current mastery probability from BKT
    If not found, assume beginner (0.1)
    """
    try:
        conn = sqlite3.connect(str(DB_PATH), timeout=30)
        cur = conn.cursor()
        
        # Check if skill_mastery table exists (v3 schema)
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='skill_mastery'")
        if not cur.fetchone():
            conn.close()
            return 0.1  # Default for beginners
        
        cur.execute("SELECT mastery_prob FROM skill_mastery WHERE skill_name = ?", (skill_name,))
        result = cur.fetchone()
        conn.close()
        
        if result:
            return result[0]
        else:
            return 0.1  # No data yet
    
    except Exception as e:
        print(f"⚠️  Error fetching mastery: {e}")
        return 0.1

def calculate_learning_cost(skill_name, current_mastery=None):
    """
    Calculate learning cost with improved formula
    Learning_Cost = Complexity × (1 - Current_Mastery)
    
    This means:
    - If you already know 70% of Java (0.7 mastery), learning Spring Boot costs less
    - Complete beginners (0.1 mastery) face full complexity cost
    """
    complexity = SKILL_COMPLEXITY.get(skill_name.lower(), 5)  # Default medium
    
    if current_mastery is None:
        current_mastery = get_current_mastery(skill_name)
    
    # Learning cost decreases as mastery increases
    learning_cost = complexity * (1.0 - current_mastery)
    
    return {
        "complexity": complexity,
        "current_mastery": current_mastery,
        "learning_cost": learning_cost,
        "hours_estimate": learning_cost * 10  # Rough estimate: 10 hours per unit
    }

def calculate_roi(skill_name, use_cache=True):
    """
    Calculate ROI for a skill
    
    ROI = (Market_Value × Demand_Trend) / Learning_Cost
    """
    skill_key = skill_name.lower().replace(' ', '_')
    
    # Check cache first
    if use_cache:
        cached = get_cached_roi(skill_name)
        if cached:
            return cached
    
    # Get market data
    market = MARKET_DATA.get(skill_key)
    if not market:
        return {
            "status": "error",
            "message": f"No market data for '{skill_name}'. Add to MARKET_DATA or fetch from API."
        }
    
    # Get learning cost
    cost_data = calculate_learning_cost(skill_name)
    
    # Calculate ROI
    market_value = market['salary']
    demand_trend = market['trend']
    learning_cost = max(cost_data['learning_cost'], 0.1)  # Avoid division by zero
    
    roi_score = (market_value * demand_trend) / learning_cost
    
    result = {
        "skill_name": skill_name,
        "roi_score": round(roi_score, 2),
        "market_salary": market_value,
        "demand_trend": demand_trend,
        "learning_cost": round(cost_data['learning_cost'], 2),
        "hours_estimate": round(cost_data['hours_estimate'], 1),
        "current_mastery": round(cost_data['current_mastery'], 2),
        "complexity": cost_data['complexity'],
        "recommendation": get_recommendation(roi_score, demand_trend),
        "calculated_at": datetime.now().isoformat()
    }
    
    # Cache result
    cache_roi(result)
    
    return result

def get_recommendation(roi_score, demand_trend):
    """Generate human-readable recommendation"""
    if roi_score > 30000:
        return "🔥 Excellent ROI - Highly recommended"
    elif roi_score > 20000:
        return "✅ Good ROI - Worth learning"
    elif roi_score > 10000:
        return "⚠️ Moderate ROI - Consider alternatives"
    else:
        return "❌ Low ROI - Not recommended unless required"

def get_cached_roi(skill_name):
    """Get cached ROI if recent"""
    try:
        conn = sqlite3.connect(str(DB_PATH), timeout=30)
        cur = conn.cursor()
        
        cur.execute("""
            SELECT roi_score, market_salary, demand_trend, learning_cost, last_updated
            FROM skill_roi
            WHERE skill_name = ?
        """, (skill_name,))
        
        result = cur.fetchone()
        conn.close()
        
        if result:
            last_updated = datetime.fromisoformat(result[4])
            if datetime.now() - last_updated < timedelta(days=CACHE_DURATION_DAYS):
                return {
                    "skill_name": skill_name,
                    "roi_score": result[0],
                    "market_salary": result[1],
                    "demand_trend": result[2],
                    "learning_cost": result[3],
                    "cached": True,
                    "last_updated": result[4]
                }
        
        return None
    
    except Exception:
        return None

def cache_roi(data):
    """Save ROI to database"""
    try:
        conn = sqlite3.connect(str(DB_PATH), timeout=30)
        cur = conn.cursor()
        
        # Check if table exists
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='skill_roi'")
        if not cur.fetchone():
            # Create table if not exists (migration will handle this properly)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS skill_roi (
                    skill_name TEXT PRIMARY KEY,
                    market_salary REAL,
                    demand_trend REAL,
                    learning_cost REAL,
                    roi_score REAL,
                    last_updated TIMESTAMP
                )
            """)
        
        cur.execute("""
            INSERT OR REPLACE INTO skill_roi 
            (skill_name, market_salary, demand_trend, learning_cost, roi_score, last_updated)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            data['skill_name'],
            data['market_salary'],
            data['demand_trend'],
            data['learning_cost'],
            data['roi_score'],
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    except Exception as e:
        print(f"⚠️  Error caching ROI: {e}")

def compare_skills(skills):
    """Compare ROI of multiple skills"""
    results = []
    for skill in skills:
        roi = calculate_roi(skill)
        if roi.get('status') != 'error':
            results.append(roi)
    
    # Sort by ROI score descending
    results.sort(key=lambda x: x['roi_score'], reverse=True)
    
    return results

def main():
    """CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Skill ROI Calculator - v3.0')
    parser.add_argument('command', choices=['calc', 'compare', 'list'],
                       help='calc: calculate single skill, compare: compare multiple, list: show all')
    parser.add_argument('--skill', help='Skill name for calc')
    parser.add_argument('--skills', help='Comma-separated skills for compare')
    
    args = parser.parse_args()
    
    if args.command == 'calc':
        if not args.skill:
            print("❌ --skill required for calc")
            return 1
        
        result = calculate_roi(args.skill)
        if result.get('status') == 'error':
            print(f"❌ {result['message']}")
            return 1
        
        print("\n" + "=" * 60)
        print(f"💰 Skill ROI Analysis: {result['skill_name']}")
        print("=" * 60)
        print(f"\n📊 ROI Score: {result['roi_score']:,.0f}")
        print(f"💵 Market Salary: ${result['market_salary']:,}")
        print(f"📈 Demand Trend: {result['demand_trend']}x")
        print(f"📚 Learning Cost: {result['learning_cost']:.2f}")
        print(f"⏱️  Estimated Hours: {result['hours_estimate']:.1f}h")
        print(f"💪 Current Mastery: {result['current_mastery']:.0%}")
        print(f"🎯 Complexity: {result['complexity']}/10")
        print(f"\n{result['recommendation']}\n")
    
    elif args.command == 'compare':
        if not args.skills:
            print("❌ --skills required for compare (e.g., python,rust,java)")
            return 1
        
        skills = [s.strip() for s in args.skills.split(',')]
        results = compare_skills(skills)
        
        print("\n" + "=" * 60)
        print("📊 Skill ROI Comparison")
        print("=" * 60)
        print(f"\n{'Rank':<5} {'Skill':<20} {'ROI':<12} {'Salary':<12} {'Trend':<8}")
        print("-" * 60)
        
        for i, r in enumerate(results, 1):
            print(f"{i:<5} {r['skill_name']:<20} {r['roi_score']:>10,.0f}  ${r['market_salary']:>8,}  {r['demand_trend']:>6}x")
        
        print("\n💡 Recommendation: Focus on top 3 skills for maximum ROI\n")
    
    elif args.command == 'list':
        all_skills = list(SKILL_COMPLEXITY.keys())
        results = compare_skills(all_skills)
        
        print("\n" + "=" * 70)
        print("📊 All Skills Ranked by ROI")
        print("=" * 70)
        print(f"\n{'#':<4} {'Skill':<25} {'ROI':<12} {'Salary':<12} {'Hours':<8} {'Rating'}")
        print("-" * 70)
        
        for i, r in enumerate(results[:20], 1):  # Top 20
            emoji = "🔥" if i <= 5 else "✅" if i <= 10 else "⚠️"
            print(f"{i:<4} {r['skill_name']:<25} {r['roi_score']:>10,.0f}  ${r['market_salary']:>8,}  {r['hours_estimate']:>6.0f}h  {emoji}")
        
        print()
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
