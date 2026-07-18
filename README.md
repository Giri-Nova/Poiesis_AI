# Poiesis

Poiesis is a chained multi-agent Google ADK system that turns a
natural-language description into a working, tested, documented ADK agent
project.

## Pipeline

```
main_agent
    -> requirement_analyser_agent
        -> architecture_designer_agent
            -> code_generator_agent      (writes files to output/<Agent_Name>/)
                -> testing_agent          (validates the written files)
                    -> documentation_designer_agent   (writes README + report)
```

Each stage is an `LlmAgent` with the next stage registered as its
`sub_agents=[...]`, so the model can call the built-in `transfer_to_agent`
tool once its stage is complete. Shared data (agent name, purpose,
requirements, architecture, generated file paths, test results) is passed
via ADK session `state`, keyed by constants in `common/state_keys.py`.

## What changed from the original draft

- **`documentation_designer_agent` now exists.** Every other agent's
  instructions referenced it, but it had no implementation.
- **`code_generator_agent` actually writes files.** It previously only had
  instructions to "generate a project" with no tool to persist anything —
  now `write_agent_project()` writes `__init__.py`, `.env`, and `agent.py`
  to `output/<Agent_Name>/`.
- **`testing_agent` runs real checks.** `validate_project()` parses the
  generated `agent.py` with Python's `ast` module, checks for a
  `root_agent` assignment, checks required files exist, and checks the
  `.env` template — instead of relying purely on the model's self-report.
- **`documentation_designer_agent` writes real output too.**
  `save_documentation()` writes `README.md` and `POIESIS_BUILD_REPORT.md`
  into the finished project folder.
- **Consistent model name** (`gemini-2.5-flash` everywhere, overridable via
  `POIESIS_MODEL` env var) — the original mixed in a nonexistent
  `gemini-3.5-flash` for `main_agent`.
- **Consistent state keys** via `common/state_keys.py` instead of ad hoc
  string literals in each file.
- **Explicit transfer instructions** — each stage's prompt now says
  exactly when to call `transfer_to_agent` and what must happen first
  (e.g. testing must call `save_test_result` before handing off).

## Running it

```bash
pip install -r requirements.txt
cp .env.example .env   # then fill in GOOGLE_API_KEY
adk run main_agent
# or
adk web
```

Generated projects land in `output/<Agent_Name>/` (override with
`POIESIS_OUTPUT_DIR`), each containing:

```
output/<Agent_Name>/
├── __init__.py
├── .env
├── agent.py
├── README.md
└── POIESIS_BUILD_REPORT.md
```
New agents can be created.
