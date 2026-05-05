const products = require("./products.json");

module.exports = products.filter((product) => product.slug !== "bubble-bop");
