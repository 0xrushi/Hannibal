/* eslint-disable no-console */
"use strict";

const assert = require("assert");
const fs = require("fs");
const path = require("path");
const vm = require("vm");

function extractFunction(source, name) {
  const re = new RegExp(
    String.raw`\b${name}\s*=\s*function\s*\([^)]*\)\s*\{[\s\S]*?\n\s*\};`
  );
  const m = source.match(re);
  if (!m)
    throw new Error(`Failed to extract ${name} from source`);
  return m[0];
}

const hannibalPath = path.join(
  __dirname,
  "..",
  "..",
  "mods",
  "hannibal",
  "simulation",
  "ai",
  "hannibal",
  "hannibal.js"
);

const src = fs.readFileSync(hannibalPath, "utf8");

// Basic static checks: ensure new-component fallbacks exist.
assert.ok(
  src.includes("template.Trainer") && src.includes("template.Researcher"),
  "Expected Trainer/Researcher fallback logic in hannibal.js"
);

// Evaluate just the helper functions in isolation.
const sandbox = {
  H: {
    replace: (s, a, b) => String(s).split(String(a)).join(String(b)),
  },
};

const code = [
  extractFunction(src, "H.saniTemplateName"),
  extractFunction(src, "H.tokenizeTokens"),
].join("\n");

vm.createContext(sandbox);
vm.runInContext(code, sandbox);

const { H } = sandbox;

// tokenizeTokens: handles newlines/indentation and trims.
{
  const tokens = H.tokenizeTokens(
    "structures/{civ}/civil_centre\n      structures/{civ}/house\n"
  );
  assert.deepStrictEqual(Array.from(tokens), [
    "structures/{civ}/civil_centre",
    "structures/{civ}/house",
  ]);
}

// tokenizeTokens: removes '-' tokens and strips leading '+'.
{
  const tokens = H.tokenizeTokens(
    "-structures/wallset_palisade +structures/rome/house structures/rome/storehouse"
  );
  assert.deepStrictEqual(Array.from(tokens), [
    "structures/rome/house",
    "structures/rome/storehouse",
  ]);
}

// saniTemplateName: matches Hannibal's dot normalization.
{
  assert.strictEqual(
    H.saniTemplateName("structures/rome/civil_centre"),
    "structures.rome.civil.centre"
  );
}

// Garrison-style negation is not a template; Hannibal must filter it.
{
  const raw = "!elephant +human -cavalry";
  const tokens = Array.from(H.tokenizeTokens(raw)).filter((t) => t[0] !== "!");
  assert.deepStrictEqual(tokens, ["human"]);
}

console.log("ok - hannibal token tests");
