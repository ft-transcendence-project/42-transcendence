const Tournament = artifacts.require("Tournament");

contract("Tournament", (accounts) => {
    let tournament;
    const owner = accounts[0];
    const nonOwner = accounts[1];

    beforeEach(async () => {
        tournament = await Tournament.new({ from: owner });
    });

    // 試合結果を記録できるかどうかのテスト
    it("should record a match", async () => {
        const winnerId = 1;
        const winnerScore = 10;
        const loserId = 2;
        const loserScore = 8;

        await tournament.recordMatch(
            winnerId,
            winnerScore,
            loserId,
            loserScore,
            { from: owner }
        );

        const match = await tournament.getMatch(1);
        assert.equal(match.winnerId, winnerId, "Winner ID should be recorded correctly");
        assert.equal(match.winnerScore, winnerScore, "Winner score should be recorded correctly");
        assert.equal(match.loserId, loserId, "Loser ID should be recorded correctly");
        assert.equal(match.loserScore, loserScore, "Loser score should be recorded correctly");
    });

    // 所有者以外が試合結果を記録しようとした場合のテスト
    it("should not allow non-owner to record a match", async () => {
        try {
            await tournament.recordMatch(1, 10, 2, 8, { from: nonOwner });
            assert.fail("Non-owner should not be able to record a match");
        } catch (error) {
            assert(error.message.includes("Caller is not the owner"), "Expected 'Caller is not the owner' error");
        }
    });

    // 複数の試合結果を連続して記録できるかどうかのテスト
    it("should record multiple matches", async () => {
        for (let i = 1; i <= 5; i++) {
            await tournament.recordMatch(i, 10 + i, i + 1, 8 + i, { from: owner });
            const match = await tournament.getMatch(i);
            assert.equal(match.winnerId, i, `Match ${i}: Winner ID should be recorded correctly`);
        }
        const matchCount = await tournament.matchCount();
        assert.equal(matchCount.toNumber(), 5, "Match count should be 5");
    });
});
