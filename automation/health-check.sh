#!/bin/bash
# 24/7 Health Monitoring Script

STATUS_FILE="/tmp/the-basics-health.json"

check_repo_health() {
    local repo=$1
    local url="https://api.github.com/repos/oconnorw225-del/$repo"
    
    if curl -s -f -H "Accept: application/vnd.github.v3+json" "$url" > /dev/null; then
        echo "healthy"
    else
        echo "unhealthy"
    fi
}

REPOS=("ndax-quantum-engine" "quantum-engine-dashb" "shadowforge-ai-trader" "repository-web-app" "The-new-ones")

echo "{\"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\", \"repos\": {" > $STATUS_FILE

for repo in "${REPOS[@]}"; do
    status=$(check_repo_health "$repo")
    echo "\"$repo\": \"$status\"," >> $STATUS_FILE
done

echo "\"overall\": \"healthy\"}}" >> $STATUS_FILE

cat $STATUS_FILE
