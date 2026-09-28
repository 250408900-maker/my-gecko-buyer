# Dev3Pack capstone

![Python](https://img.shields.io/badge/python-3.11+-blue)
![uv](https://img.shields.io/badge/uv-managed-6e56cf)
![License](https://img.shields.io/badge/license-MIT-blue)
![Claude Code](https://img.shields.io/badge/Claude_Code-ready-orange)

Your capstone, in one repository that becomes **yours**: a research assistant that
answers from six documents, cites the one it used, and refuses what they do not
support. You build it here, grade it here, hand it in from here, and defend it from
here in session 15.

**[CAPSTONE.md](CAPSTONE.md) is the complete tutorial**: what it is, every command in
order, how the capstone notebook connects to it, how you hand it in, and how you read
your score.

The tests and the grader are the course's. They come from the
[cohort repository](https://github.com/Gecko-Academy/dev3pack-cohort-2026-09) as a
package, pinned in `uv.lock`. The code they judge is yours.

## Contents

- [Start here](#start-here)
- [Make it yours](#make-it-yours)
- [The optional track: your store, the MCP, a buyer](#the-optional-track-your-store-the-mcp-a-buyer)
- [Get each day's project](#get-each-days-project)
- [Repository map](#repository-map)
- [For coding assistants](#for-coding-assistants)
- [Commands](#commands)
- [Safety](#safety)

## Start here

In the folder that holds your course folder, so the two sit side by side:

```bash
git clone https://github.com/Gecko-Academy/Dev3Pack-Gecko-Capstone-Project.git my-capstone
cd my-capstone
uv sync
uv run pytest                     # 4 passed, 2 skipped, 3 xfailed
uv run bootcamp capstone grade    # 3/10 on the offline fake model: the starting line
```

**Windows:** run these in **Git Bash** or WSL2, not PowerShell.

## Make it yours

Once, before your first commit. You need the [GitHub CLI](https://cli.github.com/),
signed in with `gh auth login`.

```bash
git remote rename origin upstream                                          # ours
gh repo create my-capstone --public --source . --remote origin --push      # yours
```

**Public**, because your submission links to your code and you defend from it. It is
not a fork, on purpose: it is a repository in its own right that started from ours.
`capstone submit` refuses while `origin` still points at this template.

## The optional track: your store, the MCP, a buyer

`projects/` holds one small project per day of week 3: a store, the Gecko MCP, and a
buyer. It is your portfolio piece for the optional showcase on Saturday 3 October.
**Nothing in `projects/` is scored.** Weekly challenge 2 (your store and a buyer) is
still done and submitted from the **course folder**; see
[project 00](projects/00-your-store-and-buyer/README.md).

## Get each day's project

We push one project per day of week 3. To pick up the next one:

```bash
git pull upstream main
```

Projects land in `projects/`. Your own work lives wherever you put it and is not
touched. If a pull stops because you changed the same file we did, git names the file
and nothing is lost.

| Day | Session | Project | Status |
|---|---|---|---|
| Monday 28 | 11: state and memory | [01: read the menu, prepare, refuse](projects/01-read-the-menu/README.md) | here |
| Tuesday 29 | 12: MCP architecture | | arrives Tuesday |
| Wednesday 30 | 13: build and secure an MCP server | | arrives Wednesday |
| Thursday 1 | 14: deploy and operate | | arrives Thursday |

## Repository map

| Path | What is in it |
|---|---|
| `CAPSTONE.md` | the complete capstone tutorial |
| `agent.py` | your agent, `YourAgent`: what the grader and the defence judge |
| `tests/` | the contract tests: green as shipped, and they must stay green |
| `data/corpus/` | the six documents your agent answers from. Never write to them. |
| `docs/` | `ISSUES.md`, `EVAL_REPORT.md`, `RETENTION.md`, `SKILL.md`, `adr/`, and `README-TEMPLATE.md` for your showcase README |
| `pyproject.toml`, `uv.lock` | the course package, and the exact course commit you run |
| `.github/workflows/check.yml` | CI: the tests and the practice grader on every push, no keys |
| `projects/` | the optional track, one folder per day, each with its own README |
| `PRD.md` | the product note for the optional track: the problem, the scope, the journey, the success numbers |
| `.claude/` | skills and agents Claude Code loads in this folder: `ship-my-capstone` for the capstone, `gecko-connect-mcp` and `gecko-solana-read` for the optional track |
| `docs/working-with-claude.md` | prompts and habits for working with an assistant |
| `workflows/` | `survey.py` grades several candidate APIs in parallel and refuses the ones that are not ready; sample specs and recorded output included |
| `AGENTS.md` | what a coding assistant should know about this repository |
| `README.md` | this page |
| `LICENSE` | MIT. Yours is yours; credit what you borrow |

Everything else is yours to add. There is no layout you have to follow.

## What you ship

One thing that runs, and a README that shows it running. By the end somebody should be
able to read this repository without you in the room and know:

- what it does, in a sentence;
- the exact command to run it, and what that command printed when **you** ran it;
- one thing it refuses to do, and why that refusal is the interesting part.

A demo that only works on the happy path is worth less than one with a failure you can
explain. Break it on purpose before somebody else does.

The README sections, in order, are in [CAPSTONE.md, section 11](CAPSTONE.md#11-your-readme-for-the-showcase),
and the six minutes of the defence in [section 12](CAPSTONE.md#12-the-defence).

## For coding assistants

`AGENTS.md` tells an assistant what this repository is and how to help with it. Claude
Code reads it by itself when you start it in this folder:

```bash
claude
```

Ask it to explain a project before you ask it to write one. It is faster at reading than
you are, and slower at knowing what you meant.

## Commands

| Command | What it does |
|---|---|
| `uv run pytest` | the contract tests |
| `uv run bootcamp capstone grade` | your agent on the 10 practice questions |
| `uv run bootcamp capstone trace "..."` | one question, every step your agent took |
| `uv run bootcamp capstone submit --github <you>` | hand in the final assignment (CAPSTONE.md, section 8) |
| `git pull upstream main` | fetch the next day's optional project |
| `git push` | push your own work to your own repository |
| `gh repo view --web` | open your repository in a browser |

## Safety

Same lanes as the course.

| Lane | What it means |
|---|---|
| Offline | recorded responses. No key, no network, no money. This is where you build. |
| Read-only | reading a real catalogue over the network. Still no key, still nothing spent. |
| Fork | a rehearsal on a throwaway copy of mainnet, run by the instructor. Optional. |
| Mainnet | never part of anything required, and never with your own key. |

**Your code holds no keys and signs nothing.** If a step looks like it needs a private
key in this repository, that step is wrong. Ask before working around it. `.gitignore`
already refuses the usual ones, and that is a seatbelt, not a reason to have them here.

Credit what you borrow. Public code is the point; taking a function or a prompt and
saying where it came from makes a reader trust the repository more, not less.
