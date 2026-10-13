// One call to each of the six Fortitude21 dangerous goods endpoints.
//
// Node.js 18 or later (built-in fetch). No key needed. The same code runs in
// a browser: the API sends Access-Control-Allow-Origin: *.
// The API allows about 10 requests per 10 seconds per IP, so the script
// pauses between calls and waits 10 seconds if it gets HTTP 429.
//
// Usage: node examples/node.mjs
// Terms of use: https://fortitude21.com/terms

const BASE = "https://fortitude21.com/api";
const PAUSE_MS = 1500;
const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

async function call(endpoint, params) {
  const url = `${BASE}/${endpoint}?${new URLSearchParams(params)}`;
  for (let attempt = 0; attempt < 2; attempt++) {
    const res = await fetch(url, { headers: { Accept: "application/json" } });
    if (res.status === 429 && attempt === 0) {
      await sleep(10_000); // the limit resets after 10 seconds
      continue;
    }
    // A 400 still carries JSON: ok is false and error says why.
    return { status: res.status, data: await res.json() };
  }
  throw new Error("rate limited twice");
}

const calls = [
  ["un-packaging", { un: "1203" }, (d) => {
    const e = d.entries[0];
    const sizes = e.containers.slice(0, 3).map((c) => `${c.type} up to ${c.largest_litres} L`).join(", ");
    return `${e.proper_shipping_name} (PG ${e.packing_group}): ${sizes}`;
  }],
  ["un-decode", { mark: "UN 3H1/Y1.9/150/26/D/BAM 12345", un: "1203" },
    (d) => `${d.noun}; may carry UN ${d.check.un}: ${d.check.entries[0].may_carry}`],
  ["ibc-dates", { code: "31HA1", made: "06/25" },
    (d) => `status ${d.status}, fill only before ${d.fill_only_before}, end of use ${d.end_of_use}`],
  ["adr-points", { l: "1203:20:10,1263:II:20:5" },
    (d) => `exempt=${d.exempt}, used ${d.used} of ${d.limit} (${d.test})`],
  ["bund-size", { region: "gb-eng", drums: 4, ibcs: 1 },
    (d) => `minimum ${d.minimum_capacity_l} L under ${d.rule.instrument}`],
  ["jerry-cans", { mode: "water", people: 4, days: 14, scenario: "survival" },
    (d) => `${d.total_l} L = ${d.cans} x ${d.can.name}`],
];

for (const [endpoint, params, summary] of calls) {
  const { status, data } = await call(endpoint, params);
  console.log(`== ${endpoint}: HTTP ${status}, ok=${data.ok}`);
  console.log("  " + (data.ok ? summary(data) : `error: ${data.error}`));
  for (const line of data.assumed ?? []) console.log(`  assumed: ${line}`);
  // Show the credit line wherever you show a result (terms, section 3).
  console.log(`  cite: ${data.cite}\n`);
  await sleep(PAUSE_MS);
}
