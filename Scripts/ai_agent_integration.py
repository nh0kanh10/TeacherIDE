"""
AI Agent Integration - v3.0
Integration layer to use AI Agent (me) for generating content

This allows the system to leverage the AI Agent already in the IDE
instead of calling external APIs.

Usage:
    from ai_agent_integration import generate_with_agent
    
    result = generate_with_agent(
        task="generate_analogy",
        target_concept="function",
        source_domain="cooking"
    )
"""
import json
from pathlib import Path
from datetime import datetime

# Path to store prompts and responses
CACHE_DIR = Path(__file__).parent.parent / '.ai_coach' / 'ai_cache'
CACHE_DIR.mkdir(parents=True, exist_ok=True)

def generate_with_agent(task, **params):
    """
    Generate content using AI Agent
    
    This is a MANUAL workflow:
    1. System creates prompt file
    2. User pastes prompt to AI Agent
    3. User pastes AI response back
    4. System processes response
    
    Args:
        task: Type of generation (generate_analogy, explain_concept, etc.)
        **params: Task-specific parameters
    
    Returns:
        dict with generated content
    """
    if task == "generate_analogy":
        return _generate_analogy_prompt(params)
    elif task == "explain_concept":
        return _explain_concept_prompt(params)
    else:
        return {"status": "error", "message": f"Unknown task: {task}"}

def _generate_analogy_prompt(params):
    """
    Create SMT analogy generation prompt for AI Agent
    
    Returns prompt that user can paste to AI Agent
    """
    target_concept = params.get('target_concept')
    source_domain = params.get('source_domain', 'general')
    keywords = params.get('keywords', [])
    
    # SMT-specialized prompt
    prompt = f"""You are an expert teacher using Structure Mapping Theory (SMT) for analogies.

**Task:** Explain the programming concept "{target_concept}" using an analogy from the "{source_domain}" domain.

**Context:**
- Target Concept: {target_concept} (programming)
- Source Domain: {source_domain} (familiar to learner)
- Related Keywords: {', '.join(keywords[:5])}

**Instructions:**
1. Map RELATIONAL STRUCTURE (not surface attributes) from {source_domain} to {target_concept}
2. Start with: "{target_concept.capitalize()} is like [concept from {source_domain}]"
3. Explain the structural mappings:
   - Key relation 1 in {source_domain} → relation 1 in programming
   - Key relation 2 in {source_domain} → relation 2 in programming
4. Keep it concise (3-4 sentences max)
5. Make it memorable and emotionally resonant

**Format your response as:**
```
[Your analogy here]
```

**Example (for Function → Cooking):**
```
A Function is like a Recipe:
- You write it once (define the function) → use it many times (call the function)
- Ingredients you prepare = Parameters (inputs)
- The dish you create = Return value (output)
Think of it as a reusable cooking instruction that turns ingredients into a meal.
```
"""
    
    # Save prompt to file for user
    prompt_file = CACHE_DIR / f"analogy_{target_concept}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    prompt_file.write_text(prompt, encoding='utf-8')
    
    print("\n" + "=" * 60)
    print("📝 AI Agent Prompt Created")
    print("=" * 60)
    print(f"\n📁 Saved to: {prompt_file}")
    print("\n📋 INSTRUCTIONS:")
    print("1. Copy the prompt below")
    print("2. Paste it to AI Agent (me!)")
    print("3. Copy my response")
    print("4. Paste back using: save_agent_response()")
    print("\n" + "=" * 60)
    print("PROMPT TO COPY:")
    print("=" * 60)
    print(prompt)
    print("=" * 60)
    
    return {
        "status": "prompt_generated",
        "prompt_file": str(prompt_file),
        "prompt": prompt,
        "next_step": "Paste prompt to AI Agent, then use save_agent_response()"
    }

def save_agent_response(task_id, response_text):
    """
    Save AI Agent's response
    
    Args:
        task_id: ID from generate_with_agent() output
        response_text: Text copied from AI Agent
    
    Returns:
        Parsed response
    """
    # Extract content between ``` markers
    import re
    match = re.search(r'```(.*?)```', response_text, re.DOTALL)
    if match:
        content = match.group(1).strip()
    else:
        content = response_text.strip()
    
    # Save to cache
    response_file = CACHE_DIR / f"response_{task_id}.txt"
    response_file.write_text(content, encoding='utf-8')
    
    print(f"\n✅ Response saved to: {response_file}")
    
    return {
        "status": "success",
        "content": content,
        "file": str(response_file)
    }

def _explain_concept_prompt(params):
    """Generate concept explanation prompt"""
    concept = params.get('concept')
    context = params.get('context', '')
    
    prompt = f"""Explain the programming concept "{concept}" in simple terms.

Context: {context}

Requirements:
- Start with a one-sentence summary
- Use analogies if helpful
- Provide a code example
- Explain common pitfalls

Keep it concise but complete.
"""
    
    prompt_file = CACHE_DIR / f"explain_{concept}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    prompt_file.write_text(prompt, encoding='utf-8')
    
    print(f"\n📁 Prompt saved: {prompt_file}")
    print("\nCopy to AI Agent:\n")
    print("=" * 60)
    print(prompt)
    print("=" * 60)
    
    return {
        "status": "prompt_generated",
        "prompt_file": str(prompt_file),
        "prompt": prompt
    }

# FUTURE: Automated integration via VS Code Extension API
# This would allow direct AI Agent calls without copy-paste
def _future_automated_call(prompt):
    """
    FUTURE ENHANCEMENT: Direct AI Agent API call
    
    Would require:
    1. VS Code Extension with AI Agent access
    2. IPC mechanism (JSON-RPC, WebSocket)
    3. Streaming response handler
    
    For now: Manual copy-paste workflow
    """
    pass

if __name__ == "__main__":
    # Example usage
    print("AI Agent Integration Module")
    print("\nExample: Generate analogy for 'function' concept")
    
    result = generate_with_agent(
        task="generate_analogy",
        target_concept="function",
        source_domain="cooking",
        keywords=["reusable", "input", "output"]
    )
    
    print("\n💡 Next: Copy prompt above and paste to AI Agent!")
