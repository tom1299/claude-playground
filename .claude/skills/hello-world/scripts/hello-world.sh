#!/bin/bash
set -euo pipefail

# Get the folder of the script
script_dir="$(dirname "$(realpath "$0")")"

echo "Hello World from within the script located at $script_dir"
