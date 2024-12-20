const fs = require('fs');
const Tournament = artifacts.require("Tournament");

module.exports = async function(deployer) {
  await deployer.deploy(Tournament);
  const deployedInstance = await Tournament.deployed();
  const contractAddress = deployedInstance.address;
  console.log("Deployed contract address:", contractAddress);

  // アドレスをファイルに保存
  const addressData = {
    address: contractAddress
  };
  fs.writeFileSync('contract_address.json', JSON.stringify(addressData, null, 2));
};