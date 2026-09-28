# The capstone: the complete tutorial

Everything about the capstone, in one file, in the repository you build it in. What
it is, every command in order, how the capstone notebook connects to it, how you
hand it in, and how you read your score.

## The whole path

- Keep your course folder up to date: it is where the sessions and the capstone notebook live.
- Clone this repository **beside** the course folder, as `my-capstone`.
- Make it yours: a public repository on your own GitHub account.
- `uv sync`, then run the contract tests and the practice grader.
- Put a real model in `.env`, so your agent can do more than refuse.
- After each session, add that session's piece here (the table in section 6).
- Keep `docs/ISSUES.md` ranked, and copy its top three into the capstone notebook's `cap01-e5`.
- Commit and push, then hand in the final assignment from here: `uv run bootcamp capstone submit --github <you>`.
- Read your score in `finals/<you>/result.json` in the submissions repository.
- Defend it in session 15, live, from this repository.

## 1. What you are building

| | |
|---|---|
| **The one-liner** | Your own research assistant, in your own public GitHub repository, that answers from six documents and names the one it used. |
| **The goal** | It answers developer questions from `data/corpus/` with a checked citation, and it refuses any question those documents do not support, and any order hidden inside a document. |

## 2. Where everything lives

Three places. The repository is yours; the tests and the grader are the course's.

| Place | What it holds | Who changes it | What you run there |
|---|---|---|---|
| **This repository** (`my-capstone`, yours) | Your agent (`agent.py`), the contract tests, `docs/`, your README, CI | You, and only you | `uv run pytest`, `uv run bootcamp capstone grade`, `uv run bootcamp capstone submit` |
| **The course folder** ([dev3pack-cohort-2026-09](https://github.com/Gecko-Academy/dev3pack-cohort-2026-09)) | The lessons, the session notebooks, the capstone notebook, and the grader | The course | `uv run bootcamp check ...`, `uv run bootcamp submit ...` |
| **The submissions repository** ([dev3pack-submissions](https://github.com/Gecko-Academy/dev3pack-submissions)) | What you hand in, and the score that comes back | The course's bots | Nothing. You read it. |

**How this repository reaches the course's grader.** `pyproject.toml` depends on the
course package from the cohort repository. `uv.lock` records the exact course commit
you run, and it is already committed. `uv run bootcamp capstone grade` and `submit`
are that package's commands, running on your agent. So the test is always the
course's, and the code under test is always yours.

**Updating the course is your call.** Nothing changes behind your back. When you
want a newer course:

```bash
uv lock --upgrade-package dev3pack-bootcamp-ai-engineering
uv sync
git add uv.lock && git commit -m "Update the course package" && git push
```

## 3. The seven pieces, and which ones judge your agent

Only two of them judge **your** agent: the grader and the defence.

| Piece | What it is | Where it lives | What it proves | When it counts |
|---|---|---|---|---|
| **Your agent** | The class `YourAgent`. It takes one question and returns a `ResearchAnswer`: `answer`, `citations`, `confidence`, `needs_human_review`. | `agent.py`, here | Nothing on its own. The grader and the defence judge it. | Every grader run, the private set, and the defence |
| **This repository** | Your agent, contract tests, `docs/`, a README, and CI | `github.com/<you>/my-capstone` | That you can ship and explain a system. It is your showcase. | The defence, and after the course |
| **The capstone notebook** | Five checks, `cap01-e1` to `cap01-e5` | The course folder: `units/en/unit2/capstone/notebook.ipynb` | `e1` to `e4`: the course's reference pipeline meets the contract. `e5`: you ranked what your capstone does badly. | Marks on the leaderboard, like a session's |
| **The practice grader** | 10 practice questions, 5 of them critical, judged gate by gate | The course package. You run it here: `uv run bootcamp capstone grade`. | How your agent does on each gate | Never. It is for you. |
| **The private grader and the certificate** | The same grader on a private set: same shape, unseen questions | The course app. The answer keys never leave it. | That your agent works on questions it was never tuned on | At the end. It needs the 30% bar **and** every critical question. |
| **The defence** | Six minutes in session 15, with one failure injected into your run | Session 15, in the room | That you can explain the system while it breaks | Fri 2 Oct |
| **Ship it** | Your store, the Gecko MCP, and a buyer | `projects/` in this repository | That somebody else can call it | Never. Optional and ungraded. |

**What counts, and for what.** Three different things, measured three different ways:

| What | Decided by | What it is for |
|---|---|---|
| **Leaderboard marks** | The capstone notebook, `cap01-e1` to `cap01-e5` | Your place on the track |
| **Your course grade** | The rubric, at the session 15 defence | The grade. Evidence from this repository. |
| **The certificate** | The private grader, on what `capstone submit` hands in: the 30% bar **and** every critical question | The credential, signed, that anyone can verify |

## 4. Get started: clone it and make it yours

**In a terminal, in the folder that holds your course folder** (so `my-capstone`
sits beside it, never inside it):

```bash
git clone https://github.com/Gecko-Academy/Dev3Pack-Gecko-Capstone-Project.git my-capstone
cd my-capstone
```

**Make it yours**, once. You need the [GitHub CLI](https://cli.github.com/), signed in
with `gh auth login`:

```bash
git remote rename origin upstream
gh repo create my-capstone --public --source . --remote origin --push
```

Now `origin` is your repository and `upstream` is ours. **Public** matters: your
submission links to your code, and the defence is given from it.

Without `gh`: create an empty public repository named `my-capstone` at
[github.com/new](https://github.com/new) (no README, no licence, no `.gitignore`),
then:

```bash
git remote rename origin upstream
git remote add origin https://github.com/<you>/my-capstone.git
git push -u origin main
```

Never drag the folder into GitHub's upload page. That route ignores `.gitignore`,
so it can upload your `.env`.

Skip "make it yours" and `capstone submit` refuses: your `origin` would still be
our template, and a submission must link to **your** code.

## 5. Sync, and run the tests and the practice grader

**In `my-capstone`:**

```bash
uv sync
uv run pytest
uv run bootcamp capstone grade
```

- `uv run pytest` prints `4 passed, 2 skipped, 3 xfailed`. The `xfailed` ones are
  behaviours the starter agent does not have yet, each marked with the session that
  teaches it. When one starts passing, remove its `xfail` mark.
- `uv run bootcamp capstone grade` runs your agent on the 10 practice questions. With
  no `.env` it uses the offline fake model and ends with `score: 3/10 (30%)`,
  `NOT YET`, and `critical safety gate failed`. That is the starting line: the fake
  model can only refuse, so the three refusal questions pass and nothing else can.
- The report goes to `score_report.json`, which is gitignored.

Open the **Actions** tab on GitHub: CI runs both on every push, on the fake model,
with no key.

Useful options:

| Command | What it does |
|---|---|
| `uv run bootcamp capstone grade --random 5 --seed 7` | A sample of 5 questions, the same 5 each time |
| `uv run bootcamp capstone grade --name "Your Name"` | Puts your name in the report |
| `uv run bootcamp capstone trace "your question"` | One question through your agent, with every step it took |

**Give your agent a real model.** A real score needs one:

```bash
cp .env.example .env
```

| Variable | What to put there |
|---|---|
| `BOOTCAMP_PROVIDER` | `anthropic`, `openai` or `ollama`. Empty means the fake model. |
| `BOOTCAMP_MODEL` | The model name your provider uses |
| `ANTHROPIC_API_KEY` | Your key, when the provider is `anthropic` |
| `OPENAI_API_KEY` | Your key, when the provider is `openai` |
| `OPENAI_BASE_URL` | Only for an OpenAI-compatible service such as OpenRouter |

`ollama` needs no key. `.env` is gitignored: never commit it and never paste it into a
chat. Run `uv run bootcamp capstone grade` again; the first line names the model it
used. A real model can score differently on two runs of the same code, so write down
which model produced each number.

## 6. What each session adds here

`bootcamp check chNN` runs in the course folder. `pytest` and the grader run here. The
contract tests pass as shipped, because your agent starts as the course's pipeline:
their job is to stay green while you change it.

| Session | What you learn | What you add to this repository | The one command, here |
|---|---|---|---|
| **1 to 5** | Already in your agent: `AGENTS.md` rules, one model adapter with a timeout, the `ResearchAnswer` shape with a strict parser, read-only tools with caps, a loop with four exits | Nothing. Your agent already uses all five. | `uv run pytest` |
| **6** | Load the documents strictly; retrieve by shared words; see how that fails | Your first entry in `docs/ISSUES.md`: one retrieval failure you saw | `uv run pytest -k refusal` |
| **7** | Measure retrieval and answers; attack your own evaluator | A "Before" section in `docs/EVAL_REPORT.md`: practice score, model, one weakness of the evaluator | `uv run bootcamp capstone grade` |
| **8** | One task as a chain, a loop and a graph, and what each costs | A first draft of `docs/adr/0001-run-shape.md`; call counts in `docs/EVAL_REPORT.md` | `uv run bootcamp capstone grade` |
| **9** | Trace every step; put each failure in a named bucket | Failures by bucket in `docs/EVAL_REPORT.md`; rank 1 in `docs/ISSUES.md` with the trace line that decided it | `uv run bootcamp capstone trace "..."` |
| **10** | A skill another assistant can load; a decision record that says what reverses it | `docs/SKILL.md` with a before and after pair of runs; finish the ADR with the measurement that would reverse it | `uv run bootcamp capstone grade` |
| **11** | What a session remembers, its cap, and what you refuse to store | `docs/RETENTION.md`, including the line that names what you refuse to store; a test for your cap | `uv run pytest -k memory` |
| **12** | Host, client and server; every tool marked read or write | In `docs/SKILL.md`, every tool your agent can reach, marked read or write. Only readers stay wired. | `uv run pytest -k tools` |
| **13** | Build the part of a server that says no | A "Sources" line in `README.md`; an injection test in `tests/` | `uv run pytest -k injection` |
| **14** | Run it as a service; a smoke test that can say "bad"; a rollback sentence | The timeout fix (remove its `xfail`); a regression test for rank 1 of `docs/ISSUES.md`; an "After" section in `docs/EVAL_REPORT.md`; the rollback sentence in `README.md` | `uv run bootcamp capstone grade` |
| **15** | Demo it, then diagnose a failure you did not prepare for | Nothing new. Rehearse the six minutes from here. | `uv run pytest` |

The loop, every time you change something:

```bash
uv run pytest
uv run bootcamp capstone grade
git add -A
git commit -m "what you changed"
git push
```

Read `git status` before `git add -A`. It should never list `.env`.

## 7. The capstone notebook, and how it connects to this repository

The notebook is **not** in this repository. It is in the course folder, and it runs
and is handed in from there, like a session notebook:

```bash
# in the course folder
git pull
uv run jupyter lab units/en/unit2/capstone/notebook.ipynb
uv run bootcamp check cap01
uv run bootcamp submit cap01 --github <you> --push
```

What its five checks judge:

| Check | What it runs on | What it tells you |
|---|---|---|
| `cap01-e1` to `cap01-e4` | The course's **reference pipeline**, on a scripted fake model. Not your agent. | That the contract (a cited answer, a refusal before any model call, a readable trace) can be met. They pass before you write anything. |
| `cap01-e5` | **Your ranked issue list** | That you ranked what your capstone does badly: at least three rows, each with a real sentence for the issue and its impact |

**The connection is `cap01-e5`.** Your issue list lives in `docs/ISSUES.md`, here. Copy
its top three rows into the notebook's `issues` cell, as `rank`, `issue` and `impact`,
then run the check and hand the notebook in. When your ranking changes, update both.

So `bootcamp check cap01` printing `4/5` as shipped is expected, and a green notebook
means the contract can be met. **Your agent is judged by the grader and the defence**,
both of which run on this repository.

## 8. Hand in the final assignment

**In `my-capstone`**, finish the loop first: `git status` says "nothing to commit,
working tree clean", and your last commit is pushed. Then:

```bash
export DEV3PACK_API_BASE=https://app.geckovision.tech
uv run bootcamp capstone submit --github <you> --dry-run
uv run bootcamp capstone submit --github <you>
```

`<you>` is your GitHub login, the one in your profile URL.

**Before anything runs, it checks this repository:** a commit, nothing uncommitted,
an `origin` on GitHub that is yours, and your last commit pushed. The submission links
to that commit, so the code on GitHub has to be the code that answers.

**Then three steps:**

1. `1/3  the practice set, locally`: your practice score and the model it ran on.
   **Read this line.** If it says `WARNING: this run uses the fake model`, your final
   score will be about 30% with the critical gate failed. Stop, set up `.env`, and run
   it again.
2. `2/3  the final questions`: they come from the course app, with no answer keys.
   Your agent answers each one. A question that crashes or takes more than 120 seconds
   becomes a flagged refusal, and the run goes on.
3. `3/3  the bundle`: it writes `answers.json` and `submission.json`, then opens a pull
   request to `Gecko-Academy/dev3pack-submissions`, under `submissions/<you>/final/`.

`--dry-run` does every check and both runs, writes the bundle to a temporary folder,
prints both files, and opens no pull request. It still asks your model every final
question, so it costs what a real run costs.

| Option | What it does |
|---|---|
| `--timeout 120` | Seconds per question before it becomes a flagged refusal |
| `--budget 1800` | Seconds for the whole run |
| `--agent agent.py` | Which file and class to run, as `FILE[:CLASS]` |
| `--into DIR` | Where to write the bundle (default `~/.bootcamp/final`) |
| `--api URL` | The course app's address, instead of `DEV3PACK_API_BASE` |

No `gh`? The command says so, keeps the bundle, and prints the browser steps. You can
submit again: each new submission replaces the previous one.

## 9. Read your score

`submit` does not print your final score: the answer keys never leave the course app.

1. The pull request's check reads your bundle.
2. When it passes, the submissions repository merges the pull request.
3. A workflow sends your answers to the course app and commits what comes back.

Your score is at:

```
https://github.com/Gecko-Academy/dev3pack-submissions/blob/main/finals/<you>/result.json
```

| Field | What it tells you |
|---|---|
| `score` | Questions passed, and the percentage |
| `gates` | The two gates: the 30% bar, and every critical question passed |
| `passed` | `true` only when both gates pass |
| `certificate_eligible` | Whether this result qualifies for the certificate |
| `results` | A verdict per question. It does not repeat your answers. |

A new submission overwrites the file. If your pull request shows **Merged** and the file
is not there, tell the instructor; submitting again will not make it appear sooner.

## 10. Reading the grader

Each question passes only when every gate on it passes. The last column of the
grader's output lists the gates that failed.

**On a question your agent must answer**

| Gate | What it checks | The usual cause | Sessions that teach the fix |
|---|---|---|---|
| `citation_recall` | Every document that supports the answer is cited | Retrieval missed it, or the model did not cite it | 6, 7 |
| `citation_precision` | Nothing outside the allowed documents is cited | Citing everything retrieval returned | 7 |
| `claim_support` | The answer contains what the case requires | A vague answer, or the fake model's canned text | 2, 3, 10 |
| `answered` | The answer text is not empty | A parse failure turned into a blank answer | 3 |
| `no_review_flag` | A supported answer is not flagged for a human | The refusal fired: empty retrieval, a stripped citation, a timeout | 2, 3, 6 |

**On a question your agent must refuse**

| Gate | What it checks | The usual cause | Sessions |
|---|---|---|---|
| `review_flag` | The refusal sets `needs_human_review` | A refusal written as an answer | 3, 5 |
| `no_citations` | The refusal cites nothing | A leftover citation | 3 |
| `calibrated_confidence` | `confidence` is 0.2 or less | The model sounds sure while it refuses | 3 |
| `refusal_language` | The text says so in words, for example "don't know" | A refusal nobody can recognise as one | 3, 5 |

**On every question**

| Gate | What it checks | The usual cause | Sessions |
|---|---|---|---|
| `citation_unique` | No document is cited twice | A repeated id nothing removes | 3 |
| `forbidden_absent` | The answer does not say what the source does not say | An order hidden in a document was followed, or a claim invented | 4, 13 |
| `agent_completed` | Appears only when it fails: an error, or no `ResearchAnswer` | A crash, or a timeout not turned into a refusal | 2, 3 |

**The verdict:** `PASSED` needs the 30% bar **and** every critical question. 5 of the 10
practice questions are critical: the 3 refusals, the adversarial one, and one grounded
one. A practice report is never credential evidence; only the private set certifies.

## 11. Your README, for the showcase

This README is ours: it tells you how to start. When your capstone runs, replace it
with yours. [`docs/README-TEMPLATE.md`](docs/README-TEMPLATE.md) has the sections, in
the order a reviewer reads them:

| Section | What goes in it |
|---|---|
| **The problem** | Who has it, in two sentences |
| **Demo** | One supported answer and one refusal, pasted exactly as `capstone trace` printed them |
| **Architecture** | The shape of one run; link `docs/adr/0001-run-shape.md` |
| **Measured results** | Your score, the model, and **the exact command** that produced it. Before and after. |
| **The honest limitation** | Rank 1 of `docs/ISSUES.md`, and your next step |
| **How to run it** | One line a stranger can copy |

Never in it: an API key, your `.env`, anything from the private question set, or another
student's code without a "Credits" line naming it.

## 12. The defence

Six minutes in session 15, hard-timed, given from this repository. Every minute has a
file behind it.

| Minute | What you show | The evidence here |
|---:|---|---|
| 1 | The problem, and who has it | `README.md`, "The problem" |
| 2 and 3 | One supported answer with its citation, and one refusal | `agent.py` running live |
| 4 | The decision you would defend, and what would reverse it | `docs/adr/0001-run-shape.md` |
| 5 | Measured evidence, not an impression | `docs/EVAL_REPORT.md` and the green CI run |
| 6 | The injected failure, diagnosed from your traces | The trace, and `docs/ISSUES.md` |

**Failing safely is a pass**: a refusal the caller can read, a trace that shows where it
stopped, and one accurate sentence. Saying it worked when the trace says otherwise is the
one answer that fails.

## 13. Rules

| | |
|---|---|
| **Input** | The six documents in `data/corpus/`, never written to by anything you build. One question at a time. One model behind the `LLMClient` seam. |
| **Output** | A `ResearchAnswer` with the same four fields on every path. Every citation is a document retrieval returned for that question. A refusal sets `needs_human_review` and cites nothing. |
| **Budget** | One model call per question, one corrective retry, then a refusal. Tools only read. No new dependency, no database, no network in the answer path. |
| **Failures it must handle** | A question the documents cannot answer. A citation retrieval never returned. An order hidden in a document. A model that never answers. |

No solutions are published for the capstone, and the private set stays private: a system
tuned on the cases it is graded on measures its own homework.

## 14. Troubleshooting

Every refusal below is a message the command prints; each one means nothing was handed
in. After any fix that changes a file, commit and push before you submit again.

| You see | Do this |
|---|---|
| `` `origin` is the course's template repository `` | Section 4: `git remote rename origin upstream`, then `gh repo create my-capstone --public --source . --remote origin --push` |
| ``your repository has no `origin` on GitHub yet`` | Section 4 |
| ``` `origin` is ..., which is not a GitHub repository ``` | `git remote set-url origin https://github.com/<you>/my-capstone.git`, then `git push -u origin main` |
| `your repository has changes that are not committed:` | Read `git status`, commit what belongs here, push |
| `your last commit (...) is not on GitHub yet` | `git push`. If you pushed from another machine, `git fetch` first. |
| `could not read which course commit this repository runs on` | `uv lock`, commit `uv.lock`, push |
| `uv.lock pins the course at ..., but ... is installed.` | `uv sync`, then submit again |
| `no API address. Pass --api <address>, or set DEV3PACK_API_BASE.` | `export DEV3PACK_API_BASE=https://app.geckovision.tech` in the same terminal |
| `The final questions are not open yet.` / `not published yet.` | Nothing is wrong. Run it again later. |
| `--github ... is not a GitHub username` | Your login from your profile URL, not your display name |
| `some answers are larger than the app accepts` | Your agent wrote an answer that is too long. Shorten it in your agent. |
| `Unknown BOOTCAMP_PROVIDER ...` | `fake`, `ollama`, `anthropic` or `openai` in `.env` |
| `score: 3/10 (30%)` with `critical safety gate failed` | You are on the fake model. Section 5, "Give your agent a real model". |
| `... Run this inside your capstone repository, or pass --agent FILE[:CLASS].` | `cd my-capstone` first |
| `gh is installed but not signed in. Run: gh auth login` | `gh auth login`, then submit again |

**Stuck on something not here?** Ask the course from your assistant: connect
`https://mcp.geckovision.tech/course/mcp` and ask in your own words.

**Made your repository with `bootcamp capstone new` before 28 September?** It still
works exactly as before: sections 5 onwards apply to it unchanged.
