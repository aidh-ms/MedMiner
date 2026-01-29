#!/bin/bash
set -e

source $VENV_PATH/bin/activate



ls -la /app/.venv/bin/ | grep medminer -i
whoami

medminer extract medication_extraction_workflow /app/data --base-dir /app/data
