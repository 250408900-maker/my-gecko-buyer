# intents/

One file per run, written by the pin step BEFORE `prepare_purchase` is called. The runner
refuses to prepare until the file is on disk and says what `run.intent` says. Each file is
an `IntentRecord` (`buyer/intent.py`); its `pinned_at` is earlier than the prepare.

Commit the ones behind your receipts and refusals. Recorded runs never write here; they go
to `.recorded/`.
