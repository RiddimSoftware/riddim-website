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
    "assets": "assets",
    "blindfold.png": "blindfold.png",
    "bubble-bop.png": "bubble-bop.png",
    "default.css": "default.css",
    "double-dozen.png": "double-dozen.png",
    "double-dozen-screenshot-1.webp": "double-dozen-screenshot-1.webp",
    "epac.png": "epac.png",
    "favicon.ico": "favicon.ico",
    "github.svg": "github.svg",
    "koneksa.webp": "koneksa.webp",
    "logo.png": "logo.png",
    "mac-app-store.svg": "mac-app-store.svg",
    "nether.jpeg": "nether.jpeg",
    "portal-door-demo.svg": "portal-door-demo.svg",
    "portal-door-icon.jpeg": "portal-door-icon.jpeg",
    "reach.png": "reach.png",
    "robots.txt": "robots.txt",
    "screenshots": "screenshots",
    "sonnio-app-icon.jpg": "sonnio-app-icon.jpg",
    "sonnio-logo.jpg": "sonnio-logo.jpg",
    "star.svg": "star.svg",
    "wordmark.png": "wordmark.png",
    "wordmark-product.png": "wordmark-product.png",
    "wordmark-product.webp": "wordmark-product.webp"
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
