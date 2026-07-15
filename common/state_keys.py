"""
Central registry of session-state keys shared by every agent in the Poiesis
pipeline. Importing from here (instead of hard-coding strings) prevents
typos like "ai_name" vs "AI_name" from silently breaking state hand-off
between agents.
"""

AI_NAME = "ai_name"
PURPOSE = "purpose"
REQUIREMENTS = "requirements"
ARCHITECTURE = "architecture"
GENERATED_PROJECT = "generated_project"
TESTING = "testing"
DOCUMENTATION = "documentation"
