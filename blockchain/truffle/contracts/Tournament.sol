// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract Tournament {
    // 試合情報を格納する構造体
    struct Match {
        uint256 matchNumber;
        uint256 winnerId;
        uint256 winnerScore;
        uint256 loserId;
        uint256 loserScore;
    }

    // 試合番号をキーにして試合情報を格納するマッピング
    mapping(uint256 => Match) public matches;

    // 記録された試合の総数
    uint256 public matchCount;

    // コントラクトの所有者のアドレス
    address public owner;

    // 新しい試合が記録されたときに発行されるイベント
    event MatchRecorded(
        uint256 matchNumber,
        uint256 winnerId,
        uint256 winnerScore,
        uint256 loserId,
        uint256 loserScore
    );

    // コントラクトの所有者のみが特定の関数を実行できるように制限
    modifier onlyOwner() {
        require(msg.sender == owner, "Caller is not the owner");
        _;
    }

    // コントラクトをデプロイするときに所有者を設定するコンストラクタ
    constructor() {
        owner = msg.sender;
    }

    // 新しい試合結果を記録する関数 
    function recordMatch(
        uint256 winnerId,
        uint256 winnerScore,
        uint256 loserId,
        uint256 loserScore
    ) public onlyOwner {
        matchCount++;
        matches[matchCount] = Match({
            matchNumber: matchCount,
            winnerId: winnerId,
            winnerScore: winnerScore,
            loserId: loserId,
            loserScore: loserScore
        });

        // MatchRecordedイベントを発行
        emit MatchRecorded(
            matchCount,
            winnerId,
            winnerScore,
            loserId,
            loserScore
        );
    }

    // 指定した試合番号の試合情報を取得する関数
    function getMatch(uint256 matchNumber) public view returns (
        uint256 winnerId,
        uint256 winnerScore,
        uint256 loserId,
        uint256 loserScore
    ) {
        Match memory m = matches[matchNumber];
        return (m.winnerId, m.winnerScore, m.loserId, m.loserScore);
    }
}
