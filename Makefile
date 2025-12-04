
.PHONY: install
install:
	uv sync
	uvx playwright install chromium
