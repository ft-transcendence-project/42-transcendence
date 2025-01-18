// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract TournamentData {
    struct Player {
        uint256 id;
        string name;
    }

    struct Match {
        uint256 round;
        uint256 matchNumber;
        uint256 timestamp;
        uint256 player1Id;
        uint256 player2Id;
        uint256 player1Score;
        uint256 player2Score;
        uint256 winnerId;
    }

    struct Tournament {
        uint256 id;
        string name;
        uint256 date;
        bool isOver;
        uint256 winnerId;
    }

    // 試合情報を格納するマッピング
    mapping(uint256 => Player) public players;
    mapping(uint256 => Tournament) public tournaments;
    mapping(uint256 => mapping(uint256 => Match)) public matches; // tournamentId => matchNumber => Match

    uint256 public playerCount;
    uint256 public tournamentCount;
    uint256 public matchCount;

    address public owner;

    event PlayerCreated(uint256 id, string name);
    event TournamentCreated(uint256 id, string name, uint256 date);
    event MatchRecorded(
        uint256 tournamentId,
        uint256 round,
        uint256 matchNumber,
        uint256 timestamp,
        uint256 player1Id,
        uint256 player2Id,
        uint256 player1Score,
        uint256 player2Score,
        uint256 winnerId
    );

    // オーナーのみが呼び出せる修飾子
    modifier onlyOwner() {
        require(msg.sender == owner, "Caller is not the owner");
        _;
    }

    // コントラクトのオーナーを設定
    constructor() {
        owner = msg.sender;
    }

    function createPlayer(string memory name) public onlyOwner {
        playerCount++;
        players[playerCount] = Player(playerCount, name);
        emit PlayerCreated(playerCount, name);
    }

    function createTournament(string memory name, uint256 date) public onlyOwner {
        tournamentCount++;
        tournaments[tournamentCount] = Tournament(tournamentCount, name, date, false, 0);
        emit TournamentCreated(tournamentCount, name, date);
    }

    function createNextRoundMatches(
        uint256 tournamentId,
        uint256 currentRound,
        uint256 matchNumber,
        uint256 timestamp
    ) private {
        uint256 nextRound = currentRound + 1;
        uint256 numMatches = matchNumber / 2;

        for (uint256 i = 1; i <= numMatches; i++) {
            uint256 newMatchNumber = (nextRound - 1) * 4 + i;
            uint256 winner1 = matches[tournamentId][i * 2 - 1].winnerId;
            uint256 winner2 = matches[tournamentId][i * 2].winnerId;

            matches[tournamentId][newMatchNumber] = Match(
                nextRound,
                newMatchNumber,
                timestamp,
                winner1,
                winner2,
                0,
                0,
                0
            );
        }
    }

    function recordMatch(
        uint256 tournamentId,
        uint256 round,
        uint256 matchNumber,
        uint256 timestamp,
        uint256 player1Id,
        uint256 player2Id,
        uint256 player1Score,
        uint256 player2Score
    ) public onlyOwner {
        require(tournaments[tournamentId].id == tournamentId, "Tournament does not exist");
        matchCount++;
        uint256 winnerId = player1Score > player2Score ? player1Id : player2Id;

        matches[tournamentId][matchNumber] = Match(
            round,
            matchNumber,
            timestamp,
            player1Id,
            player2Id,
            player1Score,
            player2Score,
            winnerId
        );

        emit MatchRecorded(
            tournamentId,
            round,
            matchNumber,
            timestamp,
            player1Id,
            player2Id,
            player1Score,
            player2Score,
            winnerId
        );

        if (checkRoundComplete(tournamentId, matchNumber)) {
            if (matchNumber >= 2) {
                createNextRoundMatches(tournamentId, round, matchNumber, timestamp);
            } else {
                tournaments[tournamentId].isOver = true;
                tournaments[tournamentId].winnerId = winnerId;
            }
        }
    }

    function checkRoundComplete(uint256 tournamentId, uint256 matchNumber) private view returns (bool) {
        for (uint256 i = 1; i <= matchNumber / 2; i++) {
            if (matches[tournamentId][i].winnerId == 0) {
                return false;
            }
        }
        return true;
    }

    function getMatch(uint256 tournamentId, uint256 matchNumber) public view returns (
        uint256 round,
        uint256 matchNumber_,
        uint256 timestamp,
        uint256 player1Id,
        uint256 player2Id,
        uint256 player1Score,
        uint256 player2Score,
        uint256 winnerId
    ) {
        Match memory m = matches[tournamentId][matchNumber];
        return (m.round, m.matchNumber, m.timestamp, m.player1Id, m.player2Id, m.player1Score, m.player2Score, m.winnerId);
    }
}
