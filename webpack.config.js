
const path = require("path");
const BunDleTracker = require('webpack-bundle-tracker');

module.exports = {
    mode: "development",
    entry: {imageswitcher: "./frontend/imageswitcher.js"},
    plugins: [new BunDleTracker({filename: './webpack-stats.json'})],
    output: {filename: '[name].bundle.js', path: path.resolve(__dirname, 'main/static/bundles')},
};