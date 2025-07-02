.DEFAULT_GOAL := help

.PHONY: help
help: ## Print Makefile help
	@grep -Eh '^[a-z.A-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[1;36m%-20s\033[0m %s\n", $$1, $$2}'

.PHONY: update-requirements
update-requirements: ## Update requirements in uv.lock, tests/functionaltests/requirement.txt
	uv lock --upgrade
	uv pip compile --quiet --upgrade tests/functionaltests/requirement.in --output-file tests/functionaltests/requirement.txt
	-pre-commit run requirements-txt-fixer --show-diff-on-failure --files tests/functionaltests/requirement.txt
