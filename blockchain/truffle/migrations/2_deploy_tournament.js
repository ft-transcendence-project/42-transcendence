const fs = require('fs');
const TournamentData = artifacts.require("TournamentData");

module.exports = async function(deployer) {
  await deployer.deploy(TournamentData);
  const deployedInstance = await TournamentData.deployed();
  const contractAddress = deployedInstance.address;
  console.log("Deployed contract address:", contractAddress);

  // アドレスをファイルに保存
  const addressData = {
    address: contractAddress
  };
  fs.writeFileSync('build/contracts/contract_address.json', JSON.stringify(addressData, null, 2));
};