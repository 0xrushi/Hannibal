TypeScript Sources

This repo contains TypeScript copies of the 0 A.D. AI runtime scripts:

- ts/mods/hannibal/simulation/ai/hannibal/hannibal.ts -> mods/hannibal/simulation/ai/hannibal/hannibal.js
- ts/source/simulation/ai/hannibal/culture.ts -> source/simulation/ai/hannibal/culture.js

Build (writes JS into the runtime paths):

  npm install
  npm run build:ai

Notes:

- 0 A.D. runs JavaScript, not TypeScript. The .js files remain the runtime outputs.
- The TS files currently use `// @ts-nocheck` so they can compile without needing to model
  the full engine-global surface area. You can remove that gradually as you add typings.
