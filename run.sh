#!/bin/bash

echo "📦 Running PromptBook Dev Workflow"

echo "🔄 Formatting code (isort + black)..."
poetry run isort .
poetry run black .

echo "🔍 Running static analysis (mypy)..."
poetry run mypy .

echo "🧪 Running tests..."
poetry run pytest --tb=short --disable-warnings

echo "📊 Running coverage..."
poetry run coverage run -m pytest
poetry run coverage report
