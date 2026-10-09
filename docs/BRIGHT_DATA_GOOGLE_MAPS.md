# Bright Data Google Maps collector

The Maps collector uses Bright Data’s dataset API. Keep the account key in the
ignored local `.env` file as `BRIGHT_DATA_API_KEY`; never put a real key in
`.env.example`, source code, shell history, or committed files.

## Configuration

Copy `.env.example` to `.env` if needed, then set `BRIGHT_DATA_API_KEY` in
`.env`. The real key is already configured in this checkout’s ignored `.env`.
To load it for a local shell without echoing the value:

```bash
set -a
. ./.env
set +a
```

## Discover places by location

Maps discovery is asynchronous. Trigger a capped batch, save the returned
`snapshot_id`, poll until it is ready, then download the JSON snapshot. The
Maps dataset ID is `gd_m8ebnr0q2qlklc02fz`. A minimal location input looks like:

```json
[{
  "location": "39.4143,-77.4105,13",
  "keyword": "coffee",
  "limit_per_input": 3
}]
```

Submit the input to `/datasets/v3/trigger` with query parameters
`dataset_id=gd_m8ebnr0q2qlklc02fz`, `type=discover_new`, and
`discover_by=location`, using `Authorization: Bearer $BRIGHT_DATA_API_KEY` and
JSON content type. For example, after saving the input above as
`/tmp/maps-input.json`:

```bash
curl --fail-with-body --silent --show-error \
  -H "Authorization: Bearer $BRIGHT_DATA_API_KEY" \
  -H 'Content-Type: application/json' \
  --data-binary @/tmp/maps-input.json \
  'https://api.brightdata.com/datasets/v3/trigger?dataset_id=gd_m8ebnr0q2qlklc02fz&type=discover_new&discover_by=location'
```

The response includes a `snapshot_id`. Poll the progress endpoint until its
status is `ready`:

```bash
curl --fail-with-body --silent --show-error \
  -H "Authorization: Bearer $BRIGHT_DATA_API_KEY" \
  'https://api.brightdata.com/datasets/v3/progress/SNAPSHOT_ID'
```

Then retrieve the results:

```bash
curl --fail-with-body --silent --show-error \
  -H "Authorization: Bearer $BRIGHT_DATA_API_KEY" \
  'https://api.brightdata.com/datasets/v3/snapshot/SNAPSHOT_ID?format=json'
```

Replace `SNAPSHOT_ID` with the returned ID. Do not use a short synchronous
`/scrape` deadline for discovery: it can cancel the job before records are
collected. Start with a small `limit_per_input`, check progress and returned
errors, then scale only after reviewing a representative result. A prior small
Frederick City request was accepted and remained `running` during checks at
about 8, 40, and 78 seconds, so allow for asynchronous completion.

This describes the observed collector workflow; check Bright Data’s current
API documentation and account status if the API schema or collector behavior
changes.
