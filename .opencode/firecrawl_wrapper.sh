#!/bin/bash

# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

# 🔱 Firecrawl Sovereign Wrapper
# Enforces resource sovereignty, credit limits, and output standardization.

# Load API Key from environment or .env
if [ -z "$FIRECRAWL_API_KEY" ]; then
    if [ -f .env ]; then
        export $(grep -v '^#' .env | xargs)
    fi
fi

if [ -z "$FIRECRAWL_API_KEY" ]; then
    echo "Error: FIRECRAWL_API_KEY not set."
    exit 1
fi

# Ensure output directory exists
mkdir -p .firecrawl

# Helper: Standardize output
save_output() {
    local modality=$1
    local content=$2
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local hash=$(echo "$content" | sha256sum | cut -c1-8)
    local filename=".firecrawl/${timestamp}_${modality}_${hash}.json"
    echo "$content" > "$filename"
    echo "$filename"
}

case "$1" in
    search)
        shift
        # Auto-prompt for feedback after search
        result=$(firecrawl search "$@")
        echo "$result"
        save_output "search" "$result"
        ;;
    scrape)
        shift
        result=$(firecrawl scrape "$@")
        echo "$result"
        save_output "scrape" "$result"
        ;;
    map)
        shift
        # Sovereign Guard: Inject default limit if missing
        if [[ "$*" != *"--limit"* ]]; then
            set -- "$@" --limit 50
        fi
        result=$(firecrawl map "$@")
        echo "$result"
        save_output "map" "$result"
        ;;
    crawl)
        shift
        # Sovereign Guard: Inject default limit if missing
        if [[ "$*" != *"--limit"* ]]; then
            set -- "$@" --limit 50
        fi
        result=$(firecrawl crawl "$@")
        echo "$result"
        save_output "crawl" "$result"
        ;;
    interact)
        shift
        result=$(firecrawl interact "$@")
        echo "$result"
        save_output "interact" "$result"
        ;;
    agent)
        shift
        result=$(firecrawl agent "$@")
        echo "$result"
        save_output "agent" "$result"
        ;;
    parse)
        shift
        result=$(firecrawl parse "$@")
        echo "$result"
        save_output "parse" "$result"
        ;;
    escalate)
        shift
        url=$1
        echo "Escalating extraction for $url..."
        
        # 1. Try Scrape
        result=$(firecrawl scrape "$url" --only-main-content)
        if [[ "$result" == *"Loading..."* ]] || [[ "$result" == *"Enable JavaScript"* ]]; then
            echo "Scrape failed (JS wall). Trying Map..."
            # 2. Try Map to find better page
            map_result=$(firecrawl map "$url" --search "content")
            # (Simplified: just try interact if map is too complex for bash)
            echo "Attempting Interaction..."
            # 3. Try Interact (requires scrapeId from a previous scrape)
            # This part is tricky in bash, usually the agent handles the scrapeId.
            # For the wrapper, we'll just signal the need for interaction.
            echo "Sovereign Escalation: Manual Interaction Required."
        else
            echo "Successfully extracted via Scrape."
            echo "$result"
        fi
        ;;
    feedback)
        shift
        firecrawl search-feedback "$@"
        ;;
    *)
        echo "Usage: firecrawl_wrapper {search|scrape|map|crawl|interact|agent|parse|escalate|feedback} [args]"
        exit 1
        ;;
esac
