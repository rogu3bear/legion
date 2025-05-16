#!/usr/bin/env bash
# Generate random but clustered ports for local development
BASE=${BASE_PORT:-20000}
CLUSTER_SIZE=${CLUSTER_SIZE:-3}
echo "# Auto-generated ports" > ports.env
for i in $(seq 1 $CLUSTER_SIZE); do
  PORT=$((BASE + i * 10 + RANDOM % 5))
  echo "SERVICE_PORT_$i=$PORT" >> ports.env
done
echo "SERVICE_PORT=${SERVICE_PORT_1}" >> ports.env
echo "CHROMA_PORT=$((BASE + CLUSTER_SIZE * 10 + RANDOM % 5))" >> ports.env
echo "Generated ports:"
cat ports.env
