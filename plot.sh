#!/usr/bin/env bash
set -euo pipefail

# Default values
SPECIES="Mmus, Athal, Dmel, Hsap"
INTERACTIVE="on"

usage() {
    cat <<'EOT'
Usage: bash plot.sh [options]

Options:
  --species <name>      Species name to plot (e.g. Mmus, Dmel, Athal, Hsap). Default: Mmus
  --interactive <on|off> Show plot interactively. Default: off
  -h, --help            Show this help
EOT
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --species)
            SPECIES="$2"
            shift 2
            ;;
        --interactive)
            INTERACTIVE="$2"
            shift 2
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            echo "Unknown argument: $1" >&2
            usage
            exit 1
            ;;
    esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

# Split the SPECIES string by commas and optional spaces into an array
IFS=',' read -r -a species_array <<< "${SPECIES}"

for sp in "${species_array[@]}"; do
    # Trim whitespace
    sp="$(echo "${sp}" | xargs)"
    
    # Data is expected in IntronModel/data/${sp}/eval_score/*.txt
    DATA_DIR="${PROJECT_ROOT}/data/${sp}/eval_score"
    OUT_PNG="${SCRIPT_DIR}/${sp}_snpr.png"

    echo "----------------------------------------"
    echo "Plotting for species: ${sp}"
    echo "Interactive: ${INTERACTIVE}"
    echo "Data dir: ${DATA_DIR}"
    echo "Output PNG: ${OUT_PNG}"

    # Ensure data dir exists
    if [[ ! -d "${DATA_DIR}" ]]; then
        echo "Error: Data directory not found: ${DATA_DIR}" >&2
        continue
    fi

    if [[ "${INTERACTIVE}" == "on" ]]; then
        python3 "${SCRIPT_DIR}/scripts/plot_scores.py" \
            --species "${sp}" \
            --interactive "${INTERACTIVE}" \
            --data_dir "${DATA_DIR}" \
            --out_png "${OUT_PNG}" &
    else
        python3 "${SCRIPT_DIR}/scripts/plot_scores.py" \
            --species "${sp}" \
            --interactive "${INTERACTIVE}" \
            --data_dir "${DATA_DIR}" \
            --out_png "${OUT_PNG}"
    fi
done

if [[ "${INTERACTIVE}" == "on" ]]; then
    wait
    echo "All interactive plots closed."
fi
