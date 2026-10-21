.PHONY: assess-data setup test pilot experiment analyze prepare
PYTHON ?= python
DATASET ?= commercial
assess-data:
	$(PYTHON) scripts/assess_datasets.py
prepare:
	$(PYTHON) scripts/prepare_dataset.py --dataset $(DATASET)
setup: prepare
	$(PYTHON) scripts/setup_database.py --dataset $(DATASET)
test:
	$(PYTHON) -m pytest -q
pilot:
	$(PYTHON) scripts/run_pilot.py --dataset $(DATASET)
experiment:
	$(PYTHON) scripts/run_experiment.py --dataset $(DATASET)
analyze:
	$(PYTHON) scripts/analyze_results.py
