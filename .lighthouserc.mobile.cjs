const baseUrl = process.env.LIGHTHOUSE_BASE_URL || "http://127.0.0.1:8080";
const chromePath = process.env.CHROME_PATH;

module.exports = {
  ci: {
    collect: {
      numberOfRuns: 1,
      url: [`${baseUrl}/`, `${baseUrl}/sonnio/`],
      settings: {
        chromeFlags: "--no-sandbox"
      },
      ...(chromePath ? { chromePath } : {})
    },
    assert: {
      assertions: {
        "categories:performance": ["error", { minScore: 0.9 }],
        "categories:accessibility": ["error", { minScore: 0.95 }],
        "categories:best-practices": ["error", { minScore: 0.95 }],
        "categories:seo": ["error", { minScore: 0.95 }]
      }
    },
    upload: {
      target: "filesystem",
      outputDir: "artifacts/lighthouse/mobile"
    }
  }
};
