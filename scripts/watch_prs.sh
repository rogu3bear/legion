#!/usr/bin/env bash
while true; do
  gh pr list --state open --limit 20 \
    | grep -E "feat:( Doctor| agent handshake| metrics exporter)" \
    > /tmp/open_legion_prs.txt
  sleep 120
done 