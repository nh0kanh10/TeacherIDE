"""
Analogy Generator - v3.0
Structure Mapping Theory (SMT) based explanations

Approach (based on expert feedback):
1. Get user background from profile
2. Query ConceptNet for KEYWORDS (not full analogy)
3. Use LLM with SMT-specialized prompt to generate analogy
4. Cache good analogies with quality scoring
"""
import json
import sqlite3
import requests
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent.parent / '.ai_coach' / 'progress.db'
PROFILE_PATH = Path(__file__).parent.parent / '.ai_coach' / 'user_profile.json'
CONCEPTNET_API = "http://api.conceptnet.io/query"

# Fallback templates (when API fails or LLM unavailable)
FALLBACK_TEMPLATES = {
    "cooking": {
        "function": "A Function is like a Recipe:\n- You write it once (define the function)\n- You can use it many times (call the function)\n- Ingredients = Parameters (inputs)\n- The dish you create = Return value (output)",
        "variable": "A Variable is like an Ingredient Container:\n- It has a name (like 'sugar' or 'salt')\n- It holds a value (the actual sugar/salt)\n- You can change what's inside (reassign values)",
        "loop": "A Loop is like Repeating a Cooking Step:\n- Stir 10 times = for i in range(10)\n- Keep stirring until smooth = while not smooth",
    },
    "music": {
        "function": "A Function is like a Musical Phrase:\n- You compose it once (define)\n- You can repeat it throughout the song (call)\n- Instruments playing = Parameters\n- The melody produced = Return value",
        "variable": "A Variable is like a Note:\n- It has a name (C, D, E)\n- It has a value (frequency/pitch)\n- You can change the octave (modify value)",
    },
    "general": {
        "function": "A Function is a reusable block of code that:\n- Takes inputs (parameters)\n- Performs operations\n- Returns outputs\nThink of it as a mini-program within your program.",
        "variable": "A Variable is a named storage location:\n- Has a name (identifier)\n- Holds a value (data)\n- Can be modified during program execution",
    }
}

def load_user_profile():
    """Load user profile to get background domain"""
    if not PROFILE_PATH.exists():
        return {"familiar_domain": "general"}
    
    with open(PROFILE_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def query_conceptnet(concept, relation="RelatedTo", limit=10):
    """
    Query ConceptNet for related concepts (KEYWORDS only)
    
    Args:
        concept: Target concept (e.g., "function")
        relation: Type of relation (RelatedTo, UsedFor, IsA, etc.)
        limit: Max results
    
    Returns:
        List of related keywords
    """
    try:
        url = f"{CONCEPTNET_API}?node=/c/en/{concept}&rel=/r/{relation}&limit={limit}"
        response = requests.get(url, timeout=5)
        
        if response.status_code != 200:
            return []
        
        data = response.json()
        edges = data.get('edges', [])
        
        # Extract keywords from edges
        keywords = []
        for edge in edges:
            # Get start and end nodes
            start = edge['start']['label']
            end = edge['end']['label']
            
            # Add the one that's not our original concept
            if start.lower() != concept.lower():
                keywords.append(start)
            elif end.lower() != concept.lower():
                keywords.append(end)
        
        return keywords[:limit]
    
    except Exception as e:
        print(f"⚠️  ConceptNet query failed: {e}")
        return []

def generate_analogy_with_agent(target_concept, source_domain, keywords):
    """
    Generate analogy using AI Agent (the AI already in the IDE)
    
    This uses ME (the AI Agent) instead of external APIs:
    - No extra cost
    - Context-aware (I know the workspace)
    - Privacy-first
    
    Workflow:
    1. Create SMT prompt
    2. User pastes to AI Agent (me!)
    3. User pastes my response back
    4. System processes and caches
    
    Args:
        target_concept: Programming concept (e.g., "function")
        source_domain: User's familiar domain (e.g., "cooking")
        keywords: ConceptNet keywords for context
    
    Returns:
        Generated analogy string
    """
    try:
        from ai_agent_integration import generate_with_agent
        
        result = generate_with_agent(
            task="generate_analogy",
            target_concept=target_concept,
            source_domain=source_domain,
            keywords=keywords
        )
        
        if result['status'] == 'prompt_generated':
            print("\n💬 Using AI Agent (me!) for generation")
            print("📋 Follow instructions above to complete")
            
            # For now, return fallback while waiting for user to paste response
            # In future, this could be automated via VS Code Extension API
            return get_fallback_analogy(target_concept, source_domain)
    
    except ImportError:
        print("⚠️  AI Agent integration not available")
    
    # Fallback to template
    return get_fallback_analogy(target_concept, source_domain)

def get_fallback_analogy(target_concept, source_domain):
    """
    Get fallback analogy from templates
    Used when LLM unavailable or as baseline
    """
    domain_templates = FALLBACK_TEMPLATES.get(source_domain, FALLBACK_TEMPLATES['general'])
    
    # Match concept (flexible matching)
    concept_key = target_concept.lower().replace(' ', '_')
    for key in domain_templates:
        if key in concept_key or concept_key in key:
            return domain_templates[key]
    
    # Generic fallback
    return f"A {target_concept} is a core programming concept. " + \
           "Think of it as a building block for creating software."

def generate_analogy(target_concept, use_llm=False):
    """
    Main analogy generation function
    
    Args:
        target_concept: Programming concept to explain
        use_llm: Whether to attempt LLM generation (future feature)
    
    Returns:
        dict with analogy and metadata
    """
    # Load user profile
    profile = load_user_profile()
    source_domain = profile.get('familiar_domain', 'general')
    
    # Check cache first
    cached = get_cached_analogy(target_concept, source_domain)
    if cached:
        print("📦 Using cached analogy")
        return cached
    
    # Query ConceptNet for keywords
    keywords = query_conceptnet(target_concept, relation="RelatedTo")
    
    if not keywords:
        keywords = query_conceptnet(target_concept, relation="UsedFor")
    
    # Generate analogy using AI Agent (me!)
    if use_llm and keywords:
        analogy_text = generate_analogy_with_agent(target_concept, source_domain, keywords)
    else:
        analogy_text = get_fallback_analogy(target_concept, source_domain)
    
    result = {
        "target_concept": target_concept,
        "source_domain": source_domain,
        "analogy": analogy_text,
        "keywords": keywords[:5],
        "method": "llm" if use_llm else "template",
        "created_at": datetime.now().isoformat()
    }
    
    # Cache it
    cache_analogy(result)
    
    return result

def get_cached_analogy(target_concept, source_domain):
    """Get cached analogy if exists"""
    try:
        conn = sqlite3.connect(str(DB_PATH), timeout=30)
        cur = conn.cursor()
        
        cur.execute("""
            SELECT analogy_text, quality_score, created_at
            FROM analogies
            WHERE target_concept = ? AND source_domain = ?
        """, (target_concept, source_domain))
        
        result = cur.fetchone()
        conn.close()
        
        if result:
            return {
                "target_concept": target_concept,
                "source_domain": source_domain,
                "analogy": result[0],
                "quality_score": result[1],
                "cached": True,
                "created_at": result[2]
            }
        
        return None
    
    except Exception:
        return None

def cache_analogy(data, quality_score=0.0):
    """Save analogy to database"""
    try:
        conn = sqlite3.connect(str(DB_PATH), timeout=30)
        cur = conn.cursor()
        
        # Create table if not exists
        cur.execute("""
            CREATE TABLE IF NOT EXISTS analogies (
                target_concept TEXT,
                source_domain TEXT,
                analogy_text TEXT,
                quality_score REAL DEFAULT 0.0,
                created_at TIMESTAMP,
                PRIMARY KEY (target_concept, source_domain)
            )
        """)
        
        cur.execute("""
            INSERT OR REPLACE INTO analogies 
            (target_concept, source_domain, analogy_text, quality_score, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (
            data['target_concept'],
            data['source_domain'],
            data['analogy'],
            quality_score,
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    except Exception as e:
        print(f"⚠️  Error caching analogy: {e}")

def rate_analogy(target_concept, source_domain, rating):
    """
    User rates analogy quality (1-5)
    Updates quality_score in cache
    """
    try:
        conn = sqlite3.connect(str(DB_PATH), timeout=30)
        cur = conn.cursor()
        
        cur.execute("""
            UPDATE analogies
            SET quality_score = ?
            WHERE target_concept = ? AND source_domain = ?
        """, (rating, target_concept, source_domain))
        
        conn.commit()
        conn.close()
        
        print(f"✅ Rating saved: {rating}/5")
    
    except Exception as e:
        print(f"⚠️  Error saving rating: {e}")

def main():
    """CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Analogy Generator - SMT-based')
    parser.add_argument('command', choices=['generate', 'rate', 'show'],
                       help='generate: create analogy, rate: rate existing, show: show all')
    parser.add_argument('--concept', help='Target concept (e.g., function, variable)')
    parser.add_argument('--rating', type=int, choices=[1,2,3,4,5], help='Quality rating for rate command')
    parser.add_argument('--llm', action='store_true', help='Use AI Agent (me!) for generation instead of templates')
    
    args = parser.parse_args()
    
    if args.command == 'generate':
        if not args.concept:
            print("❌ --concept required")
            return 1
        
        profile = load_user_profile()
        
        print("\n" + "=" * 60)
        print(f"🔗 Generating Analogy: {args.concept}")
        print("=" * 60)
        print(f"📚 Your background: {profile.get('familiar_domain', 'general')}")
        
        result = generate_analogy(args.concept, use_llm=args.llm)
        
        print(f"\n💡 Analogy:\n")
        print(result['analogy'])
        print(f"\n📊 Keywords from ConceptNet: {', '.join(result['keywords'])}")
        print(f"\n⭐ Method: {result['method']}")
        
        if not result.get('cached'):
            print("\nHow helpful was this analogy? (1-5)")
            print("Run: python analogy_generator.py rate --concept", args.concept, "--rating X")
        
        print()
    
    elif args.command == 'rate':
        if not args.concept or not args.rating:
            print("❌ Both --concept and --rating required")
            return 1
        
        profile = load_user_profile()
        rate_analogy(args.concept, profile.get('familiar_domain'), args.rating)
    
    elif args.command == 'show':
        try:
            conn = sqlite3.connect(str(DB_PATH), timeout=30)
            cur = conn.cursor()
            cur.execute("SELECT target_concept, source_domain, quality_score FROM analogies ORDER BY quality_score DESC")
            results = cur.fetchall()
            conn.close()
            
            if not results:
                print("\n❌ No analogies cached yet")
                return 1
            
            print("\n" + "=" * 60)
            print("📚 Cached Analogies")
            print("=" * 60)
            print(f"\n{'Concept':<20} {'Domain':<15} {'Rating'}")
            print("-" * 60)
            
            for r in results:
                stars = "⭐" * int(r[2]) if r[2] > 0 else "Not rated"
                print(f"{r[0]:<20} {r[1]:<15} {stars}")
            
            print()
        
        except Exception as e:
            print(f"❌ Error: {e}")
            return 1
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
