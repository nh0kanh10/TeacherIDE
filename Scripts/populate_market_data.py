"""
Market Scraper v2 - Simplified Approach
Không scrape TopCV (quá nhiều JS), dùng static data + manual updates

Strategy: Populate initial market data manually, update weekly
"""
import sqlite3
from pathlib import Path
from datetime import date

DB_PATH = Path(__file__).parent.parent / '.ai_coach' / 'progress.db'

# Market data cho top skills VN (Dec 2025)
# Source: Manual check TopCV, VietnamWorks
MARKET_DATA = {
    'Python': {'job_count': 1200, 'salary_avg': 35000000},
    'Java': {'job_count': 800, 'salary_avg': 32000000},
    'JavaScript': {'job_count': 950, 'salary_avg': 30000000},
    'React': {'job_count': 750, 'salary_avg': 33000000},
    'Node.js': {'job_count': 600, 'salary_avg': 31000000},
    'Angular': {'job_count': 400, 'salary_avg': 30000000},
    'Vue.js': {'job_count': 350, 'salary_avg': 29000000},
    'TypeScript': {'job_count': 500, 'salary_avg': 34000000},
    'Go': {'job_count': 200, 'salary_avg': 40000000},
    'Rust': {'job_count': 50, 'salary_avg': 45000000},
    'Docker': {'job_count': 600, 'salary_avg': 36000000},
    'Kubernetes': {'job_count': 400, 'salary_avg': 42000000},
    'AWS': {'job_count': 700, 'salary_avg': 38000000},
    'PostgreSQL': {'job_count': 500, 'salary_avg': 32000000},
    'MongoDB': {'job_count': 400, 'salary_avg': 30000000},
    'Redis': {'job_count': 300, 'salary_avg': 33000000},
    'GraphQL': {'job_count': 250, 'salary_avg': 35000000},
    'Microservices': {'job_count': 450, 'salary_avg': 40000000},
    'System Design': {'job_count': 300, 'salary_avg': 45000000},
    'Machine Learning': {'job_count': 400, 'salary_avg': 42000000},
}


def populate_market_data():
    """Populate database với initial market data"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    today = date.today().isoformat()
    
    print("📊 Populating market data...\n")
    
    for skill, data in MARKET_DATA.items():
        cursor.execute("""
            INSERT OR REPLACE INTO market_data (
                skill_name, date, job_count,
                salary_min, salary_max, salary_avg,
                source
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            skill,
            today,
            data['job_count'],
            int(data['salary_avg'] * 0.7),  # Min = 70% avg
            int(data['salary_avg'] * 1.3),  # Max = 130% avg
            data['salary_avg'],
            'manual_dec2025'
        ))
        
        print(f"✅ {skill:20s}: {data['job_count']:4d} jobs, {data['salary_avg']/1e6:.0f}M VND")
    
    conn.commit()
    conn.close()
    
    print(f"\n💾 Saved {len(MARKET_DATA)} skills to database")


def calculate_all_roi():
    """Calculate ROI for all skills"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get skills with market data
    cursor.execute("""
        SELECT DISTINCT m.skill_name, m.job_count, m.salary_avg
        FROM market_data m
        ORDER BY m.skill_name
    """)
    
    skills = cursor.fetchall()
    
    print("\n📈 Calculating ROI...\n")
    
    baseline_salary = 15_000_000  # Junior dev baseline
    
    for skill_name, job_count, salary_avg in skills:
        # Get or estimate learning time
        # Simple heuristic: Most skills = 20-40 hours
        learning_time = 30  # hours (default)
        
        # Market value = salary premium
        market_value = (salary_avg - baseline_salary) * 12  # Annual
        
        # ROI = (Value × Demand) / Time
        roi = (market_value * job_count / 1000) / learning_time
        
        # Update skills table
        cursor.execute("""
            UPDATE skills 
            SET market_value = ?,
                demand_score = ?,
                last_market_update = ?
            WHERE name = ?
        """, (
            int(market_value),
            job_count,
            date.today().isoformat(),
            skill_name
        ))
        
        if cursor.rowcount == 0:
            # Skill doesn't exist, create it
            cursor.execute("""
                INSERT INTO skills (name, category, complexity, market_value, demand_score)
                VALUES (?, ?, ?, ?, ?)
            """, (skill_name, 'programming', 5, int(market_value), job_count))
        
        print(f"  {skill_name:20s}: ROI = {roi/1e6:.1f}M VND per hour")
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ Updated {len(skills)} skills with ROI")


if __name__ == "__main__":
    populate_market_data()
    calculate_all_roi()
    
    print("\n🎉 Market intelligence ready!")
    print("   Use: python Scripts/review_cli.py session")
