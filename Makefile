# Makefile

.PHONY: lint format test figures stats paper build clean manifest verify-manifest quality

# Target to build artifacts
build:
	@echo "Building artifacts..."
	# Add build commands here

# Target to clean artifacts
clean:
	@echo "Cleaning artifacts..."
	# Add clean commands here

lint:
	ruff check .
	black --check .
	flake8 .
	mypy scripts --ignore-missing-imports

format:
	black .
	ruff check --fix .

test:
	pytest -q

stats:
	python scripts/validate_stats.py

figures:
	python scripts/generate_figures.py --theme light --format png --outdir paper/figures

paper: figures
	@echo "Figures generated. Compile LaTeX with:"
	@echo "cd paper && pdflatex rff_phi_mod_verification.tex"

manifest:
	python scripts/figure_manifest.py write --dir paper/figures --out paper/figures/manifest.sha256

verify-manifest:
	python scripts/figure_manifest.py verify --dir paper/figures --manifest paper/figures/manifest.sha256

quality: lint test stats figures manifest verify-manifest
