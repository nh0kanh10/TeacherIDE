# v4.0 Configuration - Production Settings
# Central config for all v4 features

# ===== EMBEDDINGS & VECTOR SEARCH =====

# ✅ Fix #2: Quantization strategy per platform
EMBEDDING_CONFIG = {
    "desktop": {
        "dimension": 384,  # all-MiniLM-L6-v2
        "dtype": "float32",  # Full precision
        "model": "sentence-transformers/all-MiniLM-L6-v2"
    },
    "mobile": {
        "dimension": 384,
        "dtype": "int8",  # Quantized for RAM efficiency
        "model": "sentence-transformers/all-MiniLM-L6-v2-quantized"
    },
    "ide_plugin": {
        "dimension": 384,
        "dtype": "float32",
        "runtime_embed": False,  # Query only, no embed at runtime
        "model": None  # Pre-embedded server-side
    }
}

# Current platform (auto-detect or override)
import platform
CURRENT_PLATFORM = "desktop"  # Default
if platform.system() == "Android" or platform.system() == "iOS":
    CURRENT_PLATFORM = "mobile"


# ===== FSRS OPTIMIZATION =====

# ✅ Fix #3: Guards against overfitting
FSRS_OPTIMIZATION = {
    "min_reviews_for_retrain": 500,  # Minimum data before optimizing weights
    "max_weight_delta": 0.15,  # ±15% max change per optimization
    "retrain_interval_days": 30,  # Re-optimize monthly
    "use_global_prior": True,  # Start with global weights, then personalize
}


# ===== EMOTIONAL DETECTION =====

# ✅ Fix #4: Cooldown to prevent spam
EMOTION_CONFIG = {
    "enabled": True,
    "threshold": 0.7,  # Confidence threshold
    "cooldown_minutes": 10,  # Min time between interventions
    "fatigue_zscore_threshold": 1.5,  # Z-score for fatigue detection
    "calibration_keystrokes": 250,  # Baseline calibration period
}


# ===== PROACTIVE SUGGESTIONS =====

# ✅ Fix #5: Conflict resolution & fatigue-aware
SUGGESTION_CONFIG = {
    "enabled": True,
    "max_per_session": 3,
    "priority_weights": {
        "review_reminder": 0.7,
        "fill_gap": 0.95,  # Highest priority
        "next_skill": 0.8,
        "market_trend": 0.6,
        "project_idea": 0.5
    },
    
    # Conflict resolver
    "fatigue_disabled_types": ["next_skill", "market_trend"],  # Disable when fatigued
    "max_concurrent": 1,  # Only show 1 suggestion at a time
}


# ===== SPACED REPETITION =====

SPACED_REP_CONFIG = {
    "enabled": True,
    "show_upcoming_count": 5,  # Show next 5 due reviews
    "early_review_threshold": 0.8,  # Allow review if > 80% of interval passed
}


# ===== PERFORMANCE =====

PERFORMANCE_LIMITS = {
    "max_sync_ms": 50,
    "max_async_ms": 500,
    "event_log_max_size": 1000,
}


# ===== PRIVACY =====

PRIVACY_CONFIG = {
    "keystroke_monitor_enabled": True,
    "store_actual_characters": False,  # NEVER store typed text
    "store_only_timings": True,
    "federated_learning_opt_in": False,  # Future: v5.0+
}


# ===== IDE HINTS (Phase 4) =====

IDE_HINTS_CONFIG = {
    "enabled": False,  # Disabled by default
    "max_hints_per_session": 3,
    "max_hints_per_10min": 1,
    "quiet_mode": False,
    "passive_only": True,  # Never auto-show, user must click
}


# Export current config
def get_config(section: str = None):
    """Get configuration section"""
    configs = {
        "embedding": EMBEDDING_CONFIG[CURRENT_PLATFORM],
        "fsrs": FSRS_OPTIMIZATION,
        "emotion": EMOTION_CONFIG,
        "suggestion": SUGGESTION_CONFIG,
        "spaced_rep": SPACED_REP_CONFIG,
        "performance": PERFORMANCE_LIMITS,
        "privacy": PRIVACY_CONFIG,
        "ide_hints": IDE_HINTS_CONFIG,
    }
    
    if section:
        return configs.get(section, {})
    return configs


if __name__ == "__main__":
    import json
    print("📋 v4.0 Configuration\n")
    print(json.dumps(get_config(), indent=2))
