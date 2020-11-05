#!/bin/sh
set -e
echo ":: Deploying Pathfinder..."
SLS_DEBUG=* serverless deploy > serverless_deploy.log
echo ":: Invoking set_webhook function..."
webhook="$(grep -oE 'https\://.*\.execute-api\.eu-west-3\.amazonaws\.com/dev' serverless_deploy.log | head -1)"
curl -fsSL -X POST "$webhook/set_webhook" >> serverless_deploy.log
echo ":: Done! Webhook set -> $webhook"
