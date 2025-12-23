#!/bin/bash

# Run pytest with coverage
coverage run -m pytest

# Generate a coverage report
coverage report

# Optionally, generate an HTML report
coverage html
