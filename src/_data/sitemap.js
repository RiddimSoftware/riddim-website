const fs = require("node:fs");
const path = require("node:path");
const { execFileSync } = require("node:child_process");

const SITE_URL = "https://riddimsoftware.com";
const repoRoot = path.resolve(__dirname, "../..");
const buildLastModified = new Date().toISOString();

function fileExists(relativePath) {
  return fs.existsSync(path.join(repoRoot, relativePath));
}

function gitLastModified(relativePaths) {
  const existingPaths = relativePaths.filter(fileExists);

  if (existingPaths.length === 0) {
    return buildLastModified;
  }

  try {
    const result = execFileSync(
      "git",
      ["log", "-1", "--format=%cI", "--", ...existingPaths],
      {
        cwd: repoRoot,
        encoding: "utf8",
        stdio: ["ignore", "pipe", "ignore"]
      }
    ).trim();

    return result || buildLastModified;
  } catch {
    return buildLastModified;
  }
}

function url(pathname) {
  return `${SITE_URL}${pathname}`;
}

function entry(pathname, sourcePaths) {
  return {
    loc: url(pathname),
    lastmod: gitLastModified(sourcePaths)
  };
}

module.exports = function () {
  const products = require("./products.json");
  const entries = [
    entry("/", ["src/index.html"]),
    ...products.map((product) =>
      entry(`/${product.slug}/`, [
        "src/products.njk",
        "src/_data/products.json",
        `src/${product.slug}/index.html`
      ])
    ),
    entry("/reach-privacy.html", ["src/reach-privacy.html"])
  ];

  if (fileExists("src/about.html")) {
    entries.push(entry("/about", ["src/about.html"]));
  } else if (fileExists("src/about/index.html")) {
    entries.push(entry("/about/", ["src/about/index.html"]));
  }

  return entries;
};
