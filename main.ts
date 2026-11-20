// news-image-20261120: writes the entry image for make.fun's
// "Sum up 20 November's world news in one image" bounty.
//
// The image is drawn by tools/make_image.py (Pillow) from news stories
// verified against reports of Friday 20 November 2026, and shipped here as
// entry.png. This program copies it to the output directory the grader
// reads, so the run needs no network and writes the same bytes every time.
//
// Run it: mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, mkdirSync, readFileSync } from "node:fs";
import { join } from "node:path";

const ASSET = new URL("./entry.png", import.meta.url);
const OUT_DIR = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
const OUT_FILE = join(OUT_DIR, "entry.png");

mkdirSync(OUT_DIR, { recursive: true });
copyFileSync(ASSET, OUT_FILE);

// Self-check: the run only counts if the bytes on disk are the asset's.
const written = readFileSync(OUT_FILE);
const source = readFileSync(ASSET);
if (!written.equals(source)) {
  throw new Error("entry.png was not copied byte for byte");
}
console.log(`wrote ${OUT_FILE} (${written.length} bytes)`);
