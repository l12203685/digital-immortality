# Digital Immortality — local test targets
# Usage: make test        (run all tests)
#        make boot-test   (boot test only)

.PHONY: all test boot-test validate-exports cold-start-test

# Default target
all: test

# Run all tests — fails on first failure
test: boot-test validate-exports cold-start-test

# Boot test: consistency_test against the example DNA
boot-test:
	python consistency_test.py templates/example_dna.md --output-dir results

# Export validation: verify platform exports preserve source DNA
validate-exports:
	python validate_exports.py --verbose

# Cold start test: validate boot recovery sequence
cold-start-test:
	python cold_start_test.py
