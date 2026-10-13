# Fortitude21 Dangerous Goods API and MCP Server

A free JSON API and remote MCP server for dangerous goods packaging questions. Send a UN number and get the UN drums, jerricans and IBCs it may use under ADR 2025, with the largest size of each. Decode a UN packaging mark part by part and check it against a substance. Total the ADR 1.1.3.6 points for a small load. Work out when an IBC's leakproofness test and 2.5 and 5-year inspections fall due. Size a bund or spill pallet under a country's rule. Turn people and days, or distance and fuel use, into a count of jerry cans. There is no key and no sign-up, and CORS is open. Each answer names the regulation it rests on and links to the same answer on fortitude21.com.

- Docs with examples: https://fortitude21.com/dangerous-goods-api
- OpenAPI 3.1: https://fortitude21.com/openapi.json (a copy is in [openapi.json](openapi.json))
- MCP server (Streamable HTTP, no auth): https://fortitude21.com/mcp
- JSON index of the endpoints: https://fortitude21.com/api/
- Terms of use: https://fortitude21.com/terms

## Tools

| Endpoint | MCP tool | What it answers | Example |
| --- | --- | --- | --- |
| `/api/un-packaging` | `un_number_packaging` | Which UN jerricans, drums and IBCs a UN number may use, and the largest size of each, from ADR 2025 Table A and its packing instructions. Covers 72 UN numbers of liquids. Takes `un` or a substance `name`. | [`?un=1203`](https://fortitude21.com/api/un-packaging?un=1203) |
| `/api/un-decode` | `decode_un_packaging_mark` | What each part of a UN packaging mark means. Add `un` to check whether the container may carry that substance. | [`?mark=UN 3H1/Y1.9/150/26/D/BAM 12345&un=1203`](https://fortitude21.com/api/un-decode?mark=UN%203H1/Y1.9/150/26/D/BAM%2012345&un=1203) |
| `/api/ibc-dates` | `ibc_inspection_dates` | When an IBC's leakproofness test and 2.5 and 5-year inspections fall due, the last month it may be filled and, for plastic and composite IBCs under UN/ADR, the end of its five-year life. `regime=us` applies 49 CFR 180.352. | [`?code=31HA1&made=06/25`](https://fortitude21.com/api/ibc-dates?code=31HA1&made=06/25) |
| `/api/adr-points` | `adr_1000_points` | The ADR 1.1.3.6 points for a vehicle load, whether it stays within the small-load exemption, and what still applies. Covers 92 UN numbers. | [`?l=1203:20:10,1263:II:20:5`](https://fortitude21.com/api/adr-points?l=1203:20:10,1263:II:20:5) |
| `/api/bund-size` | `bund_size` | The sump capacity a bund or spill pallet needs under a country's or region's rule, and the rule that governs. Rules for England, Wales, Scotland, Northern Ireland, Ireland, Germany, France, the Netherlands, Spain, the US, Canada, Australia, New Zealand, Singapore and Japan, plus `world`. | [`?region=gb-eng&drums=4&ibcs=1`](https://fortitude21.com/api/bund-size?region=gb-eng&drums=4&ibcs=1) |
| `/api/jerry-cans` | `jerry_can_quantity` | How much water or fuel to hold for a scenario, with a margin, and how many jerry cans that takes. | [`?mode=water&people=4&days=14&scenario=survival`](https://fortitude21.com/api/jerry-cans?mode=water&people=4&days=14&scenario=survival) |

The parameters and their accepted values are in [openapi.json](openapi.json) and on the [docs page](https://fortitude21.com/dangerous-goods-api).

## Quick start

GET with a query string:

```bash
curl "https://fortitude21.com/api/un-packaging?un=1203"
```

Let curl encode a mark with spaces and slashes:

```bash
curl -G "https://fortitude21.com/api/un-decode" \
  --data-urlencode "mark=UN 3H1/Y1.9/150/26/D/BAM 12345" \
  --data-urlencode "un=1203"
```

POST takes the same parameters as a JSON object:

```bash
curl -X POST "https://fortitude21.com/api/adr-points" \
  -H "Content-Type: application/json" \
  -d '{"l": "1203:20:10,1263:II:20:5"}'
```

In `adr-points`, each line is `UN number : packing group : litres or kg per package : number of packages`. Give the packing group where the UN number has entries in more than one transport category, such as 1263 paint. If one line cannot be read, the API refuses the whole load. It never totals a load without that line.

The [examples](examples) folder makes one call to each tool:

| File | Runs with |
| --- | --- |
| [examples/curl.sh](examples/curl.sh) | `bash examples/curl.sh` |
| [examples/python.py](examples/python.py) | `python examples/python.py` (Python 3.8+, standard library only) |
| [examples/node.mjs](examples/node.mjs) | `node examples/node.mjs` (Node.js 18+, built-in `fetch`) |

## Common fields

| Field | Meaning |
| --- | --- |
| `ok` | `true` for an answer. `false` with HTTP 400 when the tool cannot read the input. |
| `error` | On `ok: false`, why the request failed and how to fix it. Errors also list the accepted values: `covered_un_numbers`, `valid_regions`, `valid_scenarios` or `candidates`. |
| `assumed` | Present when the tool had to interpret an input, such as a missing region or a packing group read from a UN number. Show these lines with the answer. |
| `tool` | The same answer on the fortitude21.com tool page. |
| `cite` | A credit line with that link. Show it next to the result. |
| `docs` | The section of the docs page for this endpoint. |
| `check.entries[].may_carry` | `un-decode` with `un=`: `ok`, `viscous` (viscous liquids only), `combination` (as the outer of a combination packaging), `density` (only if the liquid is no denser than the mark allows; see `typical_relative_density`) or `no`, with `reasons`. |
| `publisher` | Fortitude21 products that fit the answer, who can buy them (businesses, on quote) and a quote link. |

An input the tool cannot read returns an error, not a guess:

```bash
curl "https://fortitude21.com/api/un-packaging?un=9999"
```

```jsonc
// HTTP 400
{
  "ok": false,
  "error": "This finder covers 72 UN numbers of liquids. This one is not among them: check the Dangerous Goods List, or send it to us.",
  "tool": "https://fortitude21.com/un-number-packaging-finder?un=9999",
  "cite": "UN number packaging finder, Fortitude21: https://fortitude21.com/un-number-packaging-finder?un=9999",
  "covered_un_numbers": ["1090", "1114", "1120", "..."],
  "docs": "https://fortitude21.com/dangerous-goods-api#un-packaging",
  // publisher
}
```

Add `lang=ja` to get Japanese text where a tool has it.

## Example responses

Real responses from the live API, captured on 13 October 2026 with the example URLs above. Lines starting `//` mark what was cut for length.

<details>
<summary><code>/api/un-packaging?un=1203</code></summary>

```jsonc
{
  "ok": true,
  "un": "1203",
  "source": "ADR 2025 Table A (Dangerous Goods List), columns 1 to 9a, as published in the RID 2025 consolidated text (OTIF, file dated 1 November 2024), with the P001, P504, IBC02 and IBC03 packing instructions. Read 6 October 2026.",
  "entries": [
    {
      "proper_shipping_name": "MOTOR SPIRIT or GASOLINE or PETROL",
      "class": "3",
      "packing_group": "II",
      "limited_quantity": "1 L",
      "packing_instructions": ["P001", "IBC02", "R001"],
      "un_mark_level": "X or Y",
      "containers": [
        {
          "type": "Jerrican, closed head",
          "codes": ["3A1", "3H1", "3B1"],
          "allowed": "ok",
          "largest_litres": 60
        },
        {
          "type": "Jerrican, removable head",
          "codes": ["3A2", "3H2", "3B2"],
          "allowed": "ok",
          "largest_litres": 60
        },
        // 4 more: closed and removable head drums, 6HA1, IBCs up to 3,000 L
      ],
      // special_packing_provisions: BB2 (IBC vapour pressure limit)
    }
  ],
  "tool": "https://fortitude21.com/un-number-packaging-finder?un=1203",
  "cite": "UN number packaging finder, Fortitude21: https://fortitude21.com/un-number-packaging-finder?un=1203",
  "docs": "https://fortitude21.com/dangerous-goods-api#un-packaging",
  // publisher
}
```

</details>

<details>
<summary><code>/api/un-decode?mark=UN 3H1/Y1.9/150/26/D/BAM 12345&un=1203</code></summary>

```jsonc
{
  "ok": true,
  "mark": "UN 3H1/Y1.9/150/26/D/BAM 12345",
  "code": "3H1",
  "spec": "3H1/Y1.9/150",
  "noun": "closed-head plastic jerrican",
  "parts": [
    {
      "part": "Packaging code",
      "value": "3H1",
      "meaning": "Closed-head plastic jerrican (3 = jerrican, H = plastic, 1 = non-removable head)"
    },
    {
      "part": "Performance level",
      "value": "Y",
      "meaning": "Approved for packing groups II and III (medium and low danger)"
    },
    {
      "part": "Relative density",
      "value": "1.9",
      "meaning": "Tested for liquids up to a relative density of 1.9 (water is 1.0)"
    },
    // 4 more: test pressure, year, approving country, approval number
  ],
  // notes, our_range, source
  "check": {
    "un": "1203",
    "max_relative_density": 1.9,
    "entries": [
      {
        "proper_shipping_name": "MOTOR SPIRIT or GASOLINE or PETROL",
        "packing_group": "II",
        "may_carry": "ok",
        "largest_litres": 60,
        "packing_instruction": "P001",
        "typical_relative_density": null,
        "reasons": []
      }
    ]
  },
  "cite": "UN packaging code decoder, Fortitude21: https://fortitude21.com/un-packaging-code-decoder?mark=UN%203H1%2FY1.9%2F150%2F26%2FD%2FBAM%2012345&un=1203",
  // tool, docs, publisher
}
```

</details>

<details>
<summary><code>/api/ibc-dates?code=31HA1&made=06/25</code></summary>

Due dates count from the current month, so this answer changes over time.

```jsonc
{
  "ok": true,
  "code": "31HA1",
  "family": "composite",
  "rules": "UN Model Regulations and ADR",
  "today": "10/2026",
  "made": "06/2025",
  "periodic_tests": true,
  "fill_only_before": "12/2027",
  "status": "ok",
  "governed_by": "leak",
  "next_leakproofness_test": "12/2027",
  "next_2_5_year_inspection": "12/2027",
  "next_5_year_inspection": "06/2030",
  "end_of_use": "06/2030",
  "if_filled_before_due_may_travel_until": "03/2028",
  "return_for_disposal_until": "06/2028",
  "assumed": [
    "No test or inspection dates (leak=, insp=) given, so every due date counts from manufacture."
  ],
  "cite": "IBC inspection date checker, Fortitude21: https://fortitude21.com/ibc-inspection-date-checker?code=31HA1&made=06%2F25",
  // note, tool, docs, publisher
}
```

</details>

<details>
<summary><code>/api/adr-points?l=1203:20:10,1263:II:20:5</code></summary>

```jsonc
{
  "ok": true,
  "exempt": true,
  "verdict": "ok",
  "test": "quantity in one transport category against its maximum (ADR 1.1.3.6.2, 1.1.3.6.3)",
  "transport_category": 2,
  "used": 300,
  "limit": 333,
  "room": 33,
  "points": 900,
  "lines": [
    {
      "un": "1203",
      "name": "Petrol",
      "proper_shipping_name": "MOTOR SPIRIT or GASOLINE or PETROL",
      "packing_group": "II",
      "transport_category": 2,
      "quantity": 200,
      "unit": "L",
      "multiplier": 3,
      "points": 600
    },
    // second line: UN 1263 paint, PG II, 100 L, 300 points
  ],
  "still_required": [
    "transport document (5.4.1), carried in the cab (8.1.2.1(a)); in Great Britain road derogation 2 lets classes 2 to 6, 8 and 9 leave it off the vehicle",
    "one 2 kg ABC fire extinguisher (8.1.4.2)",
    // 2 more
  ],
  "source": "ADR 2025 (ECE/TRANS/352, applicable from 1 January 2025): 1.1.3.6 and Table A column (15). Read 6 October 2026.",
  "assumed": [
    "UN 1263 packing group II read as 1263.1: UN 1263 Paint (solvent-based), packing group II, transport category 2."
  ],
  "cite": "ADR 1,000-point calculator, Fortitude21: https://fortitude21.com/adr-1000-point-calculator?l=1203.0%3A20%3A10%2C1263.1%3A20%3A5",
  // tool, docs, publisher
}
```

</details>

<details>
<summary><code>/api/bund-size?region=gb-eng&drums=4&ibcs=1</code></summary>

```jsonc
{
  "ok": true,
  "region": {
    "id": "gb-eng",
    "name": "England"
  },
  "liquid": "Oil or fuel",
  "containers": {
    "drums_205l": 4,
    "ibcs_1000l": 1,
    "small": null,
    "other": null
  },
  "total_stored_l": 1820,
  "mode": "bund",
  "minimum_capacity_l": 1100,
  "governs": "largest",
  "working": [
    "Total stored: 1,820 L",
    "110% of the largest container: 1,100 L",
    "25% of the total: 455 L",
    "The largest-container rule governs."
  ],
  "in_scope": true,
  "rule": {
    "instrument": "Control of Pollution (Oil Storage) (England) Regulations 2001",
    "provision": "reg 3(2)(a) and 3(5); scope reg 2(2)",
    "kind": "law",
    "url": "https://www.legislation.gov.uk/uksi/2001/2954/regulation/3"
  },
  // scope_note, notes: what the England rule leaves out, and why drain-plug pallets are excluded
  "pallets_that_pass": [],
  "cite": "Spill pallet and bund sizing calculator, Fortitude21: https://fortitude21.com/spill-pallet-sizing-calculator?region=gb-eng&drums=4&ibcs=1",
  // tool, docs, publisher
}
```

</details>

<details>
<summary><code>/api/jerry-cans?mode=water&people=4&days=14&scenario=survival</code></summary>

```jsonc
{
  "ok": true,
  "mode": "water",
  "scenario": {
    "id": "survival",
    "label": "Drinking only (survival intake)",
    "rate_l_per_person_day": 3,
    "source": "Sphere survival water intake: 2.5–3 L per person per day, climate and workload dependent."
  },
  "working": "4 people × 14 days × 3 L a day",
  "base_l": 168,
  "margin_pct": 10,
  "total_l": 185,
  "can": {
    "name": "20L Stainless Steel Water Can",
    "litres": 20,
    "url": "https://fortitude21.com/product-20l-stainless-water-can"
  },
  "cans": 10,
  "containers_20ft": 0.01,
  "cite": "Jerry can sizing calculator, Fortitude21: https://fortitude21.com/jerry-can-sizing-calculator?mode=water&people=4&days=14&scenario=survival",
  // tool, docs, publisher
}
```

</details>

## MCP server

The same six tools run as a remote MCP server:

- Endpoint: `https://fortitude21.com/mcp`
- Transport: Streamable HTTP (POST, JSON-RPC 2.0). No auth.
- Tools: `un_number_packaging`, `decode_un_packaging_mark`, `ibc_inspection_dates`, `adr_1000_points`, `bund_size`, `jerry_can_quantity`. All six are read-only.
- A plain GET on the endpoint returns a JSON description of the server.
- Listed in the official MCP Registry as `com.fortitude21/dangerous-goods`.

### Claude Desktop and claude.ai

Open Settings, then Connectors, and add a custom connector with the URL `https://fortitude21.com/mcp`.

If you configure Claude Desktop through `claude_desktop_config.json` instead, bridge the remote server with [mcp-remote](https://www.npmjs.com/package/mcp-remote). This needs Node.js.

```json
{
  "mcpServers": {
    "fortitude21": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "https://fortitude21.com/mcp"]
    }
  }
}
```

### Claude Code

```bash
claude mcp add --transport http fortitude21 https://fortitude21.com/mcp
```

Add `--scope user` to make it available in every project.

### Cursor

Add this to `~/.cursor/mcp.json`, or to `.cursor/mcp.json` in a project:

```json
{
  "mcpServers": {
    "fortitude21": {
      "url": "https://fortitude21.com/mcp"
    }
  }
}
```

### VS Code

Add this to `.vscode/mcp.json` in a workspace, or run **MCP: Open User Configuration** for every workspace:

```json
{
  "servers": {
    "fortitude21": {
      "type": "http",
      "url": "https://fortitude21.com/mcp"
    }
  }
}
```

### Test it with curl

```bash
curl -X POST https://fortitude21.com/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"adr_1000_points","arguments":{"lines":[{"un":"1203","quantity_per_package":20,"packages":10},{"un":"1263","packing_group":"II","quantity_per_package":20,"packages":5}]}}}'
```

The tool result carries the same JSON as `/api/adr-points`.

## Rate limit and caching

- About 10 requests every 10 seconds from one IP address. Above that, the API answers HTTP 429 for 10 seconds. Pause and retry.
- Responses send `Cache-Control: public, max-age=3600`. Cache them on your side.
- Send your own `User-Agent` header. The CDN refuses the default one from Python's `urllib` with HTTP 403 (Cloudflare error 1010). `requests`, Node.js `fetch` and curl pass.

## Terms of use and credit

Use of the API and the MCP server is governed by the [Fortitude21 terms of use](https://fortitude21.com/terms), section 3, not by the license in this repository. In short: the results are general information, not legal, safety or engineering advice. Check them against the regulation text before you rely on them. When you show a result to other people, show its `cite` credit line or a link to the same answer on fortitude21.com. Do not present results as your own work or as advice from Fortitude21. Do not resell access to the API or the MCP server as a service of its own. Keep to the rate limit. The service is free and comes with no service level.

## License

The [MIT License](LICENSE) covers the example code in this repository. It does not cover the API, the MCP server or their answers. [openapi.json](openapi.json) is a copy of https://fortitude21.com/openapi.json kept for reference. The live file is the current one.

## About

Fortitude21 is the trading name of JCDC Ventures Pte. Ltd., a Singapore company (UEN 202119128E). It makes UN-approved steel and plastic jerry cans, pails, tins, water cans and spill containment, and sells to businesses on quote. Questions about the API, or a field you need: david@fortitude21.com.
