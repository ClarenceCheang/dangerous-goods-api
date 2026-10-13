#!/usr/bin/env bash
# One call to each of the six Fortitude21 dangerous goods endpoints.
# No key needed. The API allows about 10 requests per 10 seconds per IP,
# so the script pauses between calls.
#
# Usage: bash examples/curl.sh
# Terms of use: https://fortitude21.com/terms

set -u
BASE="https://fortitude21.com/api"
PAUSE=1.5

call() {
  local label="$1"; shift
  echo "== $label"
  # -G sends the --data-urlencode values as a query string on a GET request.
  curl -sS -G "$@" -w '\nHTTP %{http_code}\n'
  echo
  sleep "$PAUSE"
}

# 1. UN number to permitted UN packaging (ADR 2025 Table A)
call "un-packaging" "$BASE/un-packaging" \
  --data-urlencode "un=1203"

# 2. Decode a UN packaging mark and check it against a UN number
call "un-decode" "$BASE/un-decode" \
  --data-urlencode "mark=UN 3H1/Y1.9/150/26/D/BAM 12345" \
  --data-urlencode "un=1203"

# 3. IBC test and inspection due dates
call "ibc-dates" "$BASE/ibc-dates" \
  --data-urlencode "code=31HA1" \
  --data-urlencode "made=06/25"

# 4. ADR 1.1.3.6 points. Each line is UN number : packing group (where
#    needed) : quantity per package : number of packages.
call "adr-points" "$BASE/adr-points" \
  --data-urlencode "l=1203:20:10,1263:II:20:5"

# 5. Bund or spill pallet capacity under a region's rule
call "bund-size" "$BASE/bund-size" \
  --data-urlencode "region=gb-eng" \
  --data-urlencode "drums=4" \
  --data-urlencode "ibcs=1"

# 6. Water or fuel quantity in jerry cans
call "jerry-cans" "$BASE/jerry-cans" \
  --data-urlencode "mode=water" \
  --data-urlencode "people=4" \
  --data-urlencode "days=14" \
  --data-urlencode "scenario=survival"
