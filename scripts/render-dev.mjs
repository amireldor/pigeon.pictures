/**
 * A helper script to test the template.
 * Run it from the `scripts` directory like so:
 * `node render-dev.mjs`
 */
import fs from "fs/promises";
import mustache from "mustache";
import path from "path";

const TEMPLATE_PATH = path.join(
  process.cwd(),
  "..",
  "src",
  "template",
  "pigeon.pictures.html.mustache"
);

const template = await fs.readFile(TEMPLATE_PATH, "utf-8");

// Tweak these
const startTime = new Date("2025-09-23T12:00:00+03:00");
const endTime = new Date("2025-09-23T13:30:00+03:00");

const view = {
  periodTime: 60,
  periodScale: "minutes",
  startTimeISO: startTime.toISOString(),
  endTimeISO: endTime.toISOString(),
};

const OUTPUT_PATH = path.join(process.cwd(), "..", "src", "rendered.html");

let rendered = mustache.render(template, view);

await fs.writeFile(OUTPUT_PATH, rendered);
