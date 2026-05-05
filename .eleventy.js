module.exports = function (eleventyConfig) {
  eleventyConfig.addFilter("assetUrl", function (assetPath) {
    if (!assetPath) {
      return "";
    }

    if (/^(https?:|mailto:|\/)/.test(assetPath)) {
      return assetPath;
    }

    return `/${assetPath}`;
  });

  eleventyConfig.addPassthroughCopy({
    ".well-known": ".well-known",
    "app-store.svg": "app-store.svg",
    "apple-app-site-association.json": "apple-app-site-association.json",
    "apple-touch-icon.png": "apple-touch-icon.png",
    "blindfold.png": "blindfold.png",
    "bubble-bop.png": "bubble-bop.png",
    "default.css": "default.css",
    "double-dozen.png": "double-dozen.png",
    "epac.png": "epac.png",
    "favicon.ico": "favicon.ico",
    "favicon-16.png": "favicon-16.png",
    "favicon-32.png": "favicon-32.png",
    "favicon-192.png": "favicon-192.png",
    "favicon-512.png": "favicon-512.png",
    "github.svg": "github.svg",
    "koneksa.webp": "koneksa.webp",
    "logo.png": "logo.png",
    "manifest.json": "manifest.json",
    "monogram.svg": "monogram.svg",
    "nether.jpeg": "nether.jpeg",
    "reach.png": "reach.png",
    "robots.txt": "robots.txt",
    "safari-pinned-tab.svg": "safari-pinned-tab.svg",
    "screenshots": "screenshots",
    "sonnio-app-icon.jpg": "sonnio-app-icon.jpg",
    "sonnio-logo.jpg": "sonnio-logo.jpg",
    "star.svg": "star.svg",
    "wordmark.png": "wordmark.png",
    "wordmark-product.png": "wordmark-product.png"
  });

  return {
    dir: {
      input: "src",
      output: "_site"
    },
    htmlTemplateEngine: "njk",
    markdownTemplateEngine: "njk"
  };
};
