const TournamentData = artifacts.require("TournamentData");

module.exports = function (deployer) {
    deployer.deploy(TournamentData);
};