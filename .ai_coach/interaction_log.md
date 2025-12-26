# User Interaction Log

**Purpose:** Track user preferences, decisions, and feedback patterns to enable better personalization across sessions.

---

## Session 2025-12-26 (v4.7 Development)

### Major Decisions
- ✅ Rejected Cloud-Native architecture (v4.0 report)
  - **Reason:** Too expensive ($15k/mo vs $0 local)
  - **Preference:** Local-first always
  
- ✅ Rejected LLM "Why" Engine (Feature #2)
  - **Reason:** Redundant (AI Agent already available)
  - **Choice:** Focus on high-ROI features only

- ✅ Rejected GPT-4 API in favor of Gemini
  - **Reason:** Cost ($50/mo vs free) + quality equivalent
  - **Pattern:** Budget-sensitive, pragmatic choices

- ✅ Rejected TopCV scraper in favor of manual data
  - **Reason:** Pragmatic > Perfect
  - **Pattern:** Shipping fast > complex engineering

### Learned Preferences

**Engineering Philosophy:**
- Over-engineering threshold: Very low
- Approach: Pragmatic, ROI-driven
- Motto: "Min time, max profit"
- Pattern: Reject complexity, embrace simplicity

**Communication Style:**
- Role: "Brutally honest companion"
- Wants: Challenge ideas, not "yes man"
- Expects: Devil's advocate, critical analysis
- Language: Tiếng Việt comfortable

**Budget & Resources:**
- Budget sensitivity: HIGH
- $50 vs $15k matters significantly
- Prefers: $0 solutions > paid
- Constraint: Solo developer (no team)

**Decision Making:**
- Speed: Fast iteration > long planning
- Validation: Test quickly, fail fast
- Scope: ruthlessly deprioritize non-essentials
- Example: Feature #2 (LLM Why) → bỏ luôn

### Technical Preferences

**Architecture:**
- ✅ Local-first (SQLite, Python scripts)
- ❌ Cloud-native (Kubernetes, microservices)
- ✅ Manual data > broken scrapers
- ✅ Simple >>>>> Complex

**Stack:**
- Database: SQLite (not PostgreSQL, ClickHouse)
- Language: Python
- AI: Gemini (not GPT-4)
- Deployment: Local (not cloud)

---

## Patterns Observed

### 1. "Sân bay cho máy bay giấy" Detector
User flags over-engineering instantly:
- 12 tables database for minimal data → "Sân bay trống"
- Cloud infra for 1 person → "Overkill"
- GraphRAG when simple RAG works → "Too complex"

**Threshold:** If resource/complexity >> actual need → REJECT

### 2. Catch Inconsistencies
User spots logical flaws:
- "GPT-4? Aren't you (Gemini) equally good?"
- "Feature #2 not needed - already have AI"

**Pattern:** Think critically, question assumptions

### 3. ROI-First Decision Making
Every feature evaluated by:
- Time investment vs. value delivered
- Will this make $$$ or just look cool?
- If Tier 3 (low ROI) → deprioritize/skip

---

## Goals & Motivations

**Primary Goal:** Maximize profitable knowledge in minimum time

**NOT:**
- Build perfect systems
- Learn for completeness
- Academic exercises

**YES:**
- Learn what earns $$$
- Ship fast, iterate
- Pragmatic solutions

---

## Next Session Guidelines for AI

**When starting next conversation:**
1. Read this log first
2. Remember: User is pragmatic, budget-sensitive
3. Default to simple solutions
4. Challenge with "ROI Devil's Advocate"
5. Vietnamese OK, mix English for technical terms

**Red Flags (Avoid):**
- Over-engineered solutions
- "Academic" approaches
- Expensive cloud services
- Features without clear $$$ value

**Green Lights (Embrace):**
- Simple, local-first
- Manual data > complex scraping
- $0 cost > $50/mo
- Week-long implementations > month-long

---

**Last Updated:** 2025-12-26  
**Version:** v4.7

### Decision: Rejected Cloud-Native
- **Time:** 2025-12-26T21:09:31.184766
- **Reason:** Too expensive + overkill for solo dev
- **Category:** architecture

### Decision: Manual market data > Scraping
- **Time:** 2025-12-26T21:09:31.185448
- **Reason:** Pragmatic, ships faster
- **Category:** implementation
