# Script used to centralize commands related to package administration
# and CI/CD integration

.PHONY: test flake run

test: 
	pytest

flake: 
	flake8

run:
	python -m finops_report_automation.main
