---
name: ship-my-capstone
description: Use when a learner wants to start, grade, hand in, or check the score of their capstone (the final assignment), or pastes an error from `bootcamp capstone`. Walks clone, make it yours, grade, submit and the score file with the exact commands. Never writes the learner's agent for them.
---

# Start, grade, submit, and read the score

## When to use

The learner says "start my capstone", "grade my capstone", "submit the final",
"where is my score", or pastes an error from `bootcamp capstone`. The full tutorial,
with every step explained, is `CAPSTONE.md` at the root of this repository. Read it
before you start, and send the learner to it.

## Where things live

| Place | What it is | How it is handed in |
|---|---|---|
| this repository, `my-capstone` | the learner's own public repository with their agent | `uv run bootcamp capstone submit --github LOGIN`, from here |
| the course folder, `dev3pack-cohort-2026-09` | lessons, session notebooks, the capstone notebook `cap01` | `uv run bootcamp submit chNN --github LOGIN --push`, from the course folder |
| `projects/`, in this repository | the optional store, MCP and buyer track | not handed in, not scored |

Ask where the learner is before running anything. `pwd` and `git remote -v` answer it.

## 1. Clone and make it yours

Beside the course folder, never inside it:

```bash
git clone https://github.com/Gecko-Academy/Dev3Pack-Gecko-Capstone-Project.git my-capstone
cd my-capstone
git remote rename origin upstream
gh repo create my-capstone --public --source . --remote origin --push
```

If `git remote -v` shows `origin` pointing at `Gecko-Academy/Dev3Pack-Gecko-Capstone-Project`,
the learner skipped "make it yours", and `capstone submit` will refuse. No `gh`? Create an
empty public repository at https://github.com/new, then `git remote add origin ...` and
`git push -u origin main`.

## 2. Sync

```bash
uv sync
```

`uv.lock` is already committed and records the course commit. Do not delete or regenerate
it casually: `submit` reads it. To update the course on purpose:
`uv lock --upgrade-package dev3pack-bootcamp-ai-engineering`, `uv sync`, then commit
`uv.lock`.

## 3. The capstone notebook

It lives in the course folder. `cap01-e1` to `e4` run the course's reference pipeline and
pass as shipped; `cap01-e5` takes the top three rows of this repository's
`docs/ISSUES.md`. The learner copies them into the notebook's `issues` cell, runs
`uv run bootcamp check cap01`, and hands it in from the course folder.

## 4. Practise

- The contract tests: `uv run pytest`, in this repository.
- The practice grader: `uv run bootcamp capstone grade`. Its report goes to
  `score_report.json`, which is gitignored, so it never dirties the tree.
- One question, every step: `uv run bootcamp capstone trace "the question"`.

With no `.env`, the agent runs on the offline fake model: about 30%, `NOT YET`,
and `critical safety gate failed`. That is the starting line, not a bug. A real
score needs a real model in `.env` in this repository: `BOOTCAMP_PROVIDER`
(`anthropic`, `openai` or `ollama`), `BOOTCAMP_MODEL`, and the key the provider
needs (`ANTHROPIC_API_KEY` or `OPENAI_API_KEY`; `OPENAI_BASE_URL` for an
OpenAI-compatible service; Ollama needs no key). Never read, print or paste the
learner's `.env`. Ask them to edit it.

## 5. Submit (from this repository)

Commit and push first. Then:

```bash
export DEV3PACK_API_BASE=https://app.geckovision.tech
uv run bootcamp capstone submit --github LOGIN --dry-run
uv run bootcamp capstone submit --github LOGIN
```

`LOGIN` is the GitHub login from the profile URL. Before anything runs,
`submit` checks that the repository has a commit, nothing uncommitted, an
`origin` on GitHub that is the learner's own, and that the last commit is pushed. Then three steps:
`1/3` the practice set locally, `2/3` the final questions, `3/3` the bundle and
the pull request to `Gecko-Academy/dev3pack-submissions`, under
`submissions/LOGIN/final/`. `--dry-run` does everything except the pull
request, and writes the bundle to a temporary folder.

Read the `1/3` lines with the learner. If they say `WARNING: this run uses the
fake model`, stop and ask whether they meant that.

## 6. Read the score

The score is not printed by `submit`. After the pull request merges, a workflow
in the submissions repository scores the answers and commits
`finals/LOGIN/result.json`:

```
https://github.com/Gecko-Academy/dev3pack-submissions/blob/main/finals/LOGIN/result.json
```

Read `score`, `passed` and `certificate_eligible` with the learner, and the
per-question verdicts in `results`. A new submission replaces the file. If the
pull request shows merged and the file is not there, tell the learner to
report it to the instructor rather than resubmit.

## When a command refuses

Every refusal says what to run next. Read it out, then do that. The common ones
are in the troubleshooting table at the end of `CAPSTONE.md`.

## Never

- Never write the learner's `agent.py`, and never write into a `TODO(you)` cell
  in the capstone notebook. Explain the idea, name the session page that teaches
  it, and let the learner write it. The defence is six minutes of explaining
  their own code.
- Never run `submit` without the learner reading the `1/3` output first.
- Never commit for the learner without showing them the diff.
- Never read, print or commit `.env`.
- Never open a `solutions/` directory.
