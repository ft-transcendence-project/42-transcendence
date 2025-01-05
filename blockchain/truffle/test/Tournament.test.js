const Tournament = artifacts.require("Tournament");

contract("Tournament", (accounts) => {
    let tournamentInstance;
    const owner = accounts[0];
    const nonOwner = accounts[1];

    beforeEach(async () => {
        tournamentInstance = await Tournament.new({ from: owner });
    });

    it("should create a player", async () => {
        const playerName = "Player1";
        await tournamentInstance.createPlayer(playerName, { from: owner });
        const player = await tournamentInstance.players(1);
        assert.equal(player.name, playerName, "Player name should be recorded correctly");
    });

    it("should create a tournament", async () => {
        const tournamentName = "Tournament1";
        const date = Date.now();
        await tournamentInstance.createTournament(tournamentName, date, { from: owner });
        const tournamentData = await tournamentInstance.tournaments(1);
        assert.equal(tournamentData.name, tournamentName, "Tournament name should be recorded correctly");
        assert.equal(tournamentData.date.toNumber(), date, "Tournament date should be recorded correctly");
    });

    it("should record a match by owner", async () => {
        const round = 1;
        const matchNumber = 1;
        const timestamp = Date.now();
        const player1Id = 1;
        const player2Id = 2;
        const player1Score = 10;
        const player2Score = 8;

        await tournamentInstance.createPlayer("Player1", { from: owner });
        await tournamentInstance.createPlayer("Player2", { from: owner });
        await tournamentInstance.createTournament("Tournament1", timestamp, { from: owner });

        await tournamentInstance.recordMatch(
            1,
            round,
            matchNumber,
            timestamp,
            player1Id,
            player2Id,
            player1Score,
            player2Score,
            { from: owner }
        );

        const match = await tournamentInstance.getMatch(1, matchNumber);
        assert.equal(match.round, round, "Round should be recorded correctly");
        assert.equal(match.player1Id, player1Id, "Player 1 ID should be recorded correctly");
        assert.equal(match.player2Id, player2Id, "Player 2 ID should be recorded correctly");
        assert.equal(match.player1Score, player1Score, "Player 1 score should be recorded correctly");
        assert.equal(match.player2Score, player2Score, "Player 2 score should be recorded correctly");
    });

    it("should not allow non-owner to record a match", async () => {
        try {
            await tournamentInstance.recordMatch(1, 1, 1, Date.now(), 1, 2, 10, 8, { from: nonOwner });
            assert.fail("Non-owner should not be able to record a match");
        } catch (error) {
            assert(error.message.includes("Caller is not the owner"), "Expected 'Caller is not the owner' error");
        }
    });

    it("should emit MatchRecorded event when a match is recorded", async () => {
        const round = 1;
        const matchNumber = 1;
        const timestamp = Date.now();
        const player1Id = 1;
        const player2Id = 2;
        const player1Score = 10;
        const player2Score = 8;

        await tournamentInstance.createPlayer("Player1", { from: owner });
        await tournamentInstance.createPlayer("Player2", { from: owner });
        await tournamentInstance.createTournament("Tournament1", timestamp, { from: owner });

        const result = await tournamentInstance.recordMatch(
            1,
            round,
            matchNumber,
            timestamp,
            player1Id,
            player2Id,
            player1Score,
            player2Score,
            { from: owner }
        );

        assert.equal(result.logs.length, 1, "One event should have been emitted");
        assert.equal(result.logs[0].event, "MatchRecorded", "Event should be 'MatchRecorded'");
        assert.equal(result.logs[0].args.round, round, "Round should be correct in event");
        assert.equal(result.logs[0].args.matchNumber, matchNumber, "Match number should be correct in event");
        assert.equal(result.logs[0].args.player1Id, player1Id, "Player 1 ID should be correct in event");
        assert.equal(result.logs[0].args.player2Id, player2Id, "Player 2 ID should be correct in event");
        assert.equal(result.logs[0].args.player1Score, player1Score, "Player 1 score should be correct in event");
        assert.equal(result.logs[0].args.player2Score, player2Score, "Player 2 score should be correct in event");
    });

    it("should increment matchCount when a match is recorded", async () => {
        const initialMatchCount = await tournamentInstance.matchCount();
        assert.equal(initialMatchCount.toNumber(), 0, "Initial match count should be 0");

        await tournamentInstance.createPlayer("Player1", { from: owner });
        await tournamentInstance.createPlayer("Player2", { from: owner });
        await tournamentInstance.createTournament("Tournament1", Date.now(), { from: owner });

        await tournamentInstance.recordMatch(1, 1, 1, Date.now(), 1, 2, 10, 8, { from: owner });
        const newMatchCount = await tournamentInstance.matchCount();
        assert.equal(newMatchCount.toNumber(), 1, "Match count should be incremented to 1");

        await tournamentInstance.recordMatch(1, 1, 2, Date.now(), 1, 2, 10, 8, { from: owner });
        const finalMatchCount = await tournamentInstance.matchCount();
        assert.equal(finalMatchCount.toNumber(), 2, "Match count should be incremented to 2");
    });
});