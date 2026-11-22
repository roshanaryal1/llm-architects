# ---------------------------------------------------------------------------
# Makefile — repo maintenance tasks. Everything here must run with only
# Python 3.10+ stdlib (plus optional markdownlint-cli for `make lint`).
# ---------------------------------------------------------------------------

PY := python3
RESPONSES := data/responses
MATRIX := data/decisions-matrix.csv

.DEFAULT_GOAL := help

.PHONY: help
help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'

.PHONY: validate
validate: ## Lint decisions-matrix.csv (shape, required rows, anchor column filled)
	$(PY) analysis/scripts/validate_matrix.py $(MATRIX)

.PHONY: budget
budget: ## Run the 32 GB memory-budget estimator (default: Claude's model set)
	$(PY) analysis/scripts/memory_budget.py --preset claude

.PHONY: sensitivity
sensitivity: ## Sensitivity + bootstrap analyses; writes analysis/sensitivity/*.csv
	$(PY) analysis/scripts/sensitivity.py --csv analysis/sensitivity

.PHONY: figures
figures: sensitivity ## Draw the manuscript figures as SVG in paper/figures/
	$(PY) analysis/scripts/figures.py

# Optional: rasterise the SVGs at 3x for journal upload. Needs a Chrome binary.
CHROME ?= /Applications/Google Chrome.app/Contents/MacOS/Google Chrome
.PHONY: figures-png
figures-png: figures ## Render paper/figures/*.svg to PNG with headless Chrome (optional)
	@set -e; cd paper/figures && for f in *.svg; do \
		h=$$(grep -o 'height="[0-9]*"' "$$f" | head -1 | tr -dc 0-9); \
		"$(CHROME)" --headless --disable-gpu --hide-scrollbars --force-device-scale-factor=3 \
			--window-size=900,$$h --screenshot="$$PWD/$${f%.svg}.png" "file://$$PWD/$$f" 2>/dev/null \
			|| { echo "figures-png: Chrome failed on $$f" >&2; exit 1; }; \
		echo "  $${f%.svg}.png"; \
	done

.PHONY: responses
responses: ## List captured responses and their trust_rating
	@for f in $(RESPONSES)/*.md; do \
		case "$$f" in *_TEMPLATE.md) continue;; esac; \
		name=$$(grep -m1 '^ai_name:' "$$f" | sed 's/ai_name: *//'); \
		trust=$$(grep -m1 '^trust_rating:' "$$f" | sed 's/trust_rating: *//'); \
		printf "  %-28s %s\n" "$$name" "$$trust"; \
	done

.PHONY: lint
lint: ## Run markdownlint if installed (optional)
	@command -v markdownlint >/dev/null 2>&1 \
		&& markdownlint '**/*.md' --ignore node_modules \
		|| echo "markdownlint not installed — skipping (npm i -g markdownlint-cli)"

.PHONY: check
check: validate lint ## Everything CI runs
