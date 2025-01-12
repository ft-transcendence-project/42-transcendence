const Tournament = artifacts.require("Tournament");

module.exports = function (deployer) {
    deployer.deploy(Tournament);
};