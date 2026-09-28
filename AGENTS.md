# This repository, for coding assistants

This file tells a coding assistant what this repository is and how to help with it.

## Purpose

A student's own **capstone** for the Dev3Pack AI-Engineering bootcamp: a research
assistant that answers from the six documents in `data/corpus/`, cites the one it used,
and refuses what they do not support. It starts as a clone of a course-provided
repository and becomes the student's own public repository (suggested name
`my-capstone`). [CAPSTONE.md](CAPSTONE.md) is the complete tutorial; send the student
there before improvising.

- **What is judged:** `agent.py` (`YourAgent`), by the course's grader
  (`uv run bootcamp capstone grade` for practice, `uv run bootcamp capstone submit` for
  the final set) and by the session 15 defence. The grader comes from the course package
  pinned in `uv.lock`; never edit it, and never tune on anything from the private set.
- **The contract tests** in `tests/` pass as shipped and must stay green. An `xfail`
  that starts passing wants its marker removed, not a rewritten test.
- **The capstone notebook** (`cap01`) is in the student's course folder, not here. Its
  `cap01-e5` takes the top three rows of this repository's `docs/ISSUES.md`.
- **`projects/`** is an optional, unscored track (a store, the Gecko MCP, a buyer).
  Weekly challenge 2 is submitted from the course folder, not from here.
- If a student asks for a score: the practice score is `capstone grade` here; the final
  score is `finals/<github>/result.json` in `Gecko-Academy/dev3pack-submissions`.

Gecko, in the founder's words: how an agent moves money on Solana and proves it landed as
asked. Never describe it as an "API comprehension layer"; that line is retired.

## How to help

- **Explain before you write.** The projects teach something. An assistant that hands
  over a finished answer has removed the exercise. Explain what a step is asking for and
  point at the file.
- **Never write the answer to a check.** Say what the check guards and what its message
  means.
- **Say when you are unsure.** A run that did not happen is not evidence. Do not claim a
  command worked unless it ran.
- **No keys, ever.** Nothing in this repository needs a private key or an API key. If a
  step seems to, that is a bug to report, not to work around. Never create, paste or
  commit one.
- **Credit what is borrowed.** If you bring in code from somewhere, say where in the
  file.

## How to run it

Each project folder has its own README with its own commands. There is no repository-wide
build.

```bash
git pull upstream main                                      # the next day's project
python3 projects/01-read-the-menu/check.py                  # project 01's local self-check
```

`check.py` prints a local score only. It reaches no leaderboard and no grader.
