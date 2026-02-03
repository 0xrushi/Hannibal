"use strict";

const fs = require("fs");
const path = require("path");

function copyFile(src, dst) {
  fs.mkdirSync(path.dirname(dst), { recursive: true });
  fs.copyFileSync(src, dst);
}

function main() {
  const repo = process.cwd();

  const mappings = [
    [
      path.join(repo, "ts-build", "mods", "hannibal", "simulation", "ai", "hannibal", "hannibal.js"),
      path.join(repo, "mods", "hannibal", "simulation", "ai", "hannibal", "hannibal.js"),
    ],
    [
      path.join(repo, "ts-build", "source", "simulation", "ai", "hannibal", "culture.js"),
      path.join(repo, "source", "simulation", "ai", "hannibal", "culture.js"),
    ],
    [
      path.join(repo, "ts-build", "source", "simulation", "ai", "hannibal", "rpc.js"),
      path.join(repo, "source", "simulation", "ai", "hannibal", "rpc.js"),
    ],
  ];

  for (const [src, dst] of mappings) {
    if (!fs.existsSync(src))
      throw new Error(`Missing build output: ${src}`);
    copyFile(src, dst);
  }
}

main();
