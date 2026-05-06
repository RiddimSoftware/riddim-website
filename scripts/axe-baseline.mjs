import fs from "node:fs/promises";
import path from "node:path";
import { chromium } from "playwright";
import axe from "axe-core";

const baseUrl = process.env.LIGHTHOUSE_BASE_URL || "http://127.0.0.1:8080";
const chromePath = process.env.CHROME_PATH || chromium.executablePath();
const pages = [
  { label: "Homepage", path: "/" },
  { label: "Sonnio product page", path: "/sonnio/" }
];
const tags = ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22a", "wcag22aa"];
const outputDir = path.join(process.cwd(), "artifacts", "accessibility");
const outputPath = path.join(outputDir, "axe-baseline.json");
const summaryPath = path.join(outputDir, "axe-summary.md");

await fs.mkdir(outputDir, { recursive: true });

const browser = await chromium.launch({
  executablePath: chromePath,
  headless: true
});

const results = [];

try {
  const page = await browser.newPage({
    viewport: { width: 1440, height: 1080 }
  });

  for (const pageConfig of pages) {
    const url = new URL(pageConfig.path, baseUrl).toString();
    await page.goto(url, { waitUntil: "networkidle" });
    await page.addScriptTag({ content: axe.source });
    const run = await page.evaluate(async axeTags => {
      // eslint-disable-next-line no-undef
      return await axe.run(document, {
        runOnly: {
          type: "tag",
          values: axeTags
        }
      });
    }, tags);

    results.push({
      label: pageConfig.label,
      path: pageConfig.path,
      url,
      violationCount: run.violations.length,
      violations: run.violations.map(violation => ({
        id: violation.id,
        impact: violation.impact,
        description: violation.description,
        help: violation.help,
        helpUrl: violation.helpUrl,
        tags: violation.tags,
        nodes: violation.nodes.map(node => ({
          target: node.target,
          html: node.html,
          failureSummary: node.failureSummary
        }))
      }))
    });
  }
} finally {
  await browser.close();
}

await fs.writeFile(
  outputPath,
  `${JSON.stringify({ generatedAt: new Date().toISOString(), standard: "WCAG 2.2 AA tags via axe-core", results }, null, 2)}\n`
);

const summaryLines = [
  "# Accessibility baseline",
  "",
  `Generated: ${new Date().toISOString()}`,
  "",
  "Automated ruleset: axe-core tags `wcag2a`, `wcag2aa`, `wcag21a`, `wcag21aa`, `wcag22a`, `wcag22aa`.",
  ""
];

for (const result of results) {
  summaryLines.push(`## ${result.label} (${result.path})`);
  if (result.violations.length === 0) {
    summaryLines.push("", "- No automated WCAG A/AA violations found.", "");
    continue;
  }

  summaryLines.push("", `- ${result.violations.length} violation(s) found.`, "");
  for (const violation of result.violations) {
    const selectors = violation.nodes
      .flatMap(node => node.target)
      .slice(0, 3)
      .map(selector => `\`${selector}\``)
      .join(", ");
    summaryLines.push(
      `- \`${violation.id}\` (${violation.impact || "unknown impact"}) — ${violation.help}${selectors ? `; sample target(s): ${selectors}` : ""}`
    );
  }
  summaryLines.push("");
}

const summary = `${summaryLines.join("\n")}\n`;
await fs.writeFile(summaryPath, summary);
process.stdout.write(summary);

if (process.env.GITHUB_STEP_SUMMARY) {
  await fs.appendFile(process.env.GITHUB_STEP_SUMMARY, `${summary}\n`);
}
