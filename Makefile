# Thursday (project 04). Every target runs from a clean clone.
.PHONY: hooks test lint scan recorded smoke smoke-recorded cards

hooks:            ## refuse commits that carry a key
	git config core.hooksPath .githooks

test:             ## the offline tests
	uv run pytest

lint:
	uv run ruff check . && uv run ruff format --check .

scan:             ## the key scan, over every tracked file
	python3 scripts/scan_secrets.py

recorded:         ## the five cases and the trap, offline
	GECKO_SOURCE=recorded uv run buyer --cases

smoke:            ## the five cases and the trap, LIVE on devnet: one lands, the rest refuse
	uv run buyer --cases --devnet --json smoke-report.json

smoke-recorded:   ## the rollback: the same smoke, on recorded answers
	GECKO_SOURCE=recorded uv run buyer --cases --json smoke-report.recorded.json

cards:            ## the four Friday cards, offline
	GECKO_SOURCE=recorded uv run buyer --cards
