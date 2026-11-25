# CLAUDE.md

Guidance for Claude Code when working in this repository.

## Project

Lead Triage Agent: a LangGraph agent that reads a customer inquiry, extracts key fields, grades the lead (hot / warm / cold), routes it, drafts a reply for hot leads, and pauses for human approval before anything is sent. All data is synthetic (fictional company "Brightwave Web Studio").

## Structure

| Path | Role |
| --- | --- |
| `app/state.py` | `AgentState` (TypedDict, `total=False`). The shared state every node reads and writes. |
| `app/schemas.py` | Pydantic models for LLM structured output (`ExtractedLead`, `Classification`) and, later, API request/response models. |
| `app/prompts.py` | System prompts. Each prompt has a `#vN` version comment. Company info is loaded from `data/company.json`. |
| `app/nodes.py` | Node functions (`extract`, `classify`, `draft_reply`, ...) and router functions (`route_by_grade`). |
| `app/graph.py` | Builds and compiles the `StateGraph`. |
| `app/tracing.py` | Optional Langfuse tracing. Callbacks go in the run config so one lead = one trace. Off when `LANGFUSE_PUBLIC_KEY` is not set (tests, CI). |
| `app/main.py` | Async FastAPI endpoints: `POST /leads`, `GET /leads/{thread_id}`, `POST /leads/{thread_id}/approve`. |
| `data/` | `company.json` (fictional company config) and `sample_leads.json` (20 sample inquiries). |
| `evals/` | `dataset.json` (labeled leads), `run_evals.py`, and `prompt_log.md` (record of every prompt change). |
| `tests/` | pytest tests. LLM calls are mocked with `monkeypatch` (see `use_fake_llms` in `test_graph.py`). |

Import direction: `nodes -> state -> schemas`. `schemas.py` must never import `state.py` or `nodes.py`.

## Commands

Run everything from the project root.

```bash
uv run python playground.py              # run a sample lead through the graph (real API, costs money)
uv run pytest                            # tests (LLM mocked, free)
uv run python -m evals.run_evals v1      # eval set against the real API (costs money; only when asked)
uv run uvicorn app.main:app --reload     # API at http://localhost:8000/docs
docker compose up --build                # same API in Docker (reads keys from .env)
uv run ruff format .          # format
uv run ruff check .           # lint
```

## Code rules

- A node returns only the fields it changed, as a dict (for example `{"extracted": result}`). Never mutate and return the whole `state`.
- Read fields that must exist with `state["key"]`. Use `state.get("key")` only for fields that may not be set yet.
- Router functions return the next node name as a string and never call the LLM.
- Create the LLM objects (`llm`, `extract_llm`, `classify_llm`) once at the top of `nodes.py`, not inside node functions.
- Use `temperature=0` for extraction and classification.
- Indent with 4 spaces.
- Build file paths from `Path(__file__)`, not from the current working directory.

## Prompt changes

- When changing a prompt in `app/prompts.py`, bump its `#vN` comment.
- Record what failed, what changed, and why in `evals/prompt_log.md`.
- Do not "fix" a prompt before the current version has an eval score. The before/after numbers are part of the project.

## Human-in-the-loop

- `human_approval` uses `interrupt`. When the graph resumes, the node runs again from the top, so never put side effects (sending, saving) before `interrupt()`.
- The graph must be compiled with a checkpointer, and every `invoke` must pass `{"configurable": {"thread_id": ...}}`.

## Do not

- Do not read, print, or commit `.env` or `.env.local`. Never write an API key into code or any committed file. `.env.example` holds placeholders only.
- Do not run `evals/run_evals.py` or `playground.py` unless asked. They call the paid OpenAI API.
- Do not add real customer data. All leads stay synthetic.
- Do not push to `main` or rewrite git history without being asked.
