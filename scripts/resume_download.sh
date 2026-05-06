#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 3 ]]; then
  echo "Usage: $0 <url> <output_path> <expected_bytes> [sleep_seconds]" >&2
  exit 2
fi

URL=$1
OUTPUT_PATH=$2
EXPECTED_BYTES=$3
SLEEP_SECONDS=${4:-5}
SPEED_TIME=${SPEED_TIME:-20}
SPEED_LIMIT=${SPEED_LIMIT:-65536}

mkdir -p "$(dirname "$OUTPUT_PATH")"
LOCK_PATH=${OUTPUT_PATH}.lock
exec 9>"$LOCK_PATH"
flock 9

HEADER_PATH_IN_PROGRESS=""
cleanup_interrupted() {
  if [[ -n "${HEADER_PATH_IN_PROGRESS:-}" ]]; then
    rm -f "$HEADER_PATH_IN_PROGRESS"
  fi
}
trap 'cleanup_interrupted; exit 130' INT TERM HUP

attempt=0
while true; do
  current_size=0
  if [[ -f "$OUTPUT_PATH" ]]; then
    current_size=$(stat -c '%s' "$OUTPUT_PATH")
  fi

  if [[ "$current_size" -eq "$EXPECTED_BYTES" ]]; then
    echo "download_complete size=$current_size"
    break
  fi
  if [[ "$current_size" -gt "$EXPECTED_BYTES" ]]; then
    echo "download_oversized size=$current_size target=$EXPECTED_BYTES path=$OUTPUT_PATH" >&2
    exit 1
  fi

  attempt=$((attempt + 1))
  echo "attempt=$attempt size=$current_size target=$EXPECTED_BYTES"

  header_path=${OUTPUT_PATH}.headers
  rm -f "$header_path"
  HEADER_PATH_IN_PROGRESS=$header_path

  curl_exit=0
  curl \
    -L \
    --fail \
    --connect-timeout 30 \
    --no-progress-meter \
    --show-error \
    --speed-time "$SPEED_TIME" \
    --speed-limit "$SPEED_LIMIT" \
    -D "$header_path" \
    -C - \
    -o "$OUTPUT_PATH" \
    "$URL" || curl_exit=$?
  echo "curl_exit=$curl_exit"

  http_status=""
  content_range=""
  content_start=""
  if [[ -f "$header_path" ]]; then
    http_status=$(awk '/^HTTP/{code=$2} END{print code}' "$header_path" | tr -d '\r')
    content_range=$(awk 'BEGIN{IGNORECASE=1} /^Content-Range: bytes /{line=$0} END{print line}' "$header_path" | tr -d '\r')
  fi
  if [[ "$content_range" =~ bytes[[:space:]]+([0-9]+)- ]]; then
    content_start=${BASH_REMATCH[1]}
  fi

  echo "http_status=${http_status:-unknown} content_start=${content_start:-none}"
  rm -f "$header_path"

  current_size=0
  if [[ -f "$OUTPUT_PATH" ]]; then
    current_size=$(stat -c '%s' "$OUTPUT_PATH")
  fi
  echo "post_attempt_size=$current_size"
  HEADER_PATH_IN_PROGRESS=""

  if [[ "$current_size" -eq "$EXPECTED_BYTES" ]]; then
    echo "download_complete size=$current_size"
    break
  fi
  if [[ "$current_size" -gt "$EXPECTED_BYTES" ]]; then
    echo "download_oversized size=$current_size target=$EXPECTED_BYTES path=$OUTPUT_PATH" >&2
    exit 1
  fi

  sleep "$SLEEP_SECONDS"
done
