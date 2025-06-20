.DEFAULT_GOAL := help

.PHONY: help
help: ## Print Makefile help
	@grep -Eh '^[a-z.A-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[1;36m%-20s\033[0m %s\n", $$1, $$2}'

.PHONY: update-requirements
update-requirements: ## Update requirements.txt
	uv pip compile --quiet --upgrade requirements.in --output-file requirements.txt
	for FILE in requirements.in tests/functionaltests/requirement.in ; do uv pip compile --quiet --allow-unsafe --upgrade $${FILE} --output-file $${FILE%.in}.txt ; done ;
	-pre-commit run requirements-txt-fixer --all-files --show-diff-on-failure
