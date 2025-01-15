module.exports = {
    networks: {
        development: {
            host: "ganache", // Ganacheのホスト
            port: 8545, // Ganacheのポート
            network_id: "*", // 任意のネットワークID
        },
    },
    compilers: {
        solc: {
            version: "0.8.0", // Solidityコンパイラのバージョン
        },
    },
};