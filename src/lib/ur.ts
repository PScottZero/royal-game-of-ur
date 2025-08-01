/*
BOARD TILES
+---+---+---+---+       +---+---+
| 0 | 1 | 2 | 3 | 4   5 | 6 | 7 |
+---+---+---+---+---+---+---+---+
| 8 | 9 | 10| 11| 12| 13| 14| 15|
+---+---+---+---+---+---+---+---+
| 16| 17| 18| 19| 20  21| 22| 23|
+---+---+---+---+       +---+---+

DIE ROLL OUTCOMES
						[0]            |            [1]
		0        1        1    |    1        0        0
	/ 0 \    / 0 \    / 0 \  |  / 1 \    / 1 \    / 1 \
1 --- 1  0 --- 1  1 --- 0 | 0 --- 0  1 --- 0  0 --- 1
	(0)      (1)      (2)   |   (3)      (4)      (5)
*/

export const NUM_PIECES = 7;
const NUM_DICE = 4;

const P1 = true;
const P2 = false;

const P1_PATH = [4, 3, 2, 1, 0, 8, 9, 10, 11, 12, 13, 14, 15, 7, 6, 5];
const P2_PATH = [
	20, 19, 18, 17, 16, 8, 9, 10, 11, 12, 13, 14, 15, 23, 22, 21
];

const ROSETTE_TILES = [0, 6, 11, 16, 22];
const SAFE_ROSETTE_TILE = 11;

export class RoyalGameOfUr {
	p1Pieces: number[];
	p2Pieces: number[];
	dice: number[];
	turn: boolean;

	constructor() {
		this.p1Pieces = new Array(NUM_PIECES).fill(P1_PATH[0]);
		this.p2Pieces = new Array(NUM_PIECES).fill(P2_PATH[0]);
		this.dice = [0, 0, 0, 0];
		this.turn = P1;
	}

	reset() {
		this.p1Pieces.fill(P1_PATH[0]);
		this.p2Pieces.fill(P2_PATH[0]);
		this.dice = [0, 0, 0, 0];
		this.turn = P1;
	}

	move(pieceIdx: number): void {
		const pieces = this.getPieces();
		const path = this.getPath();

		const tile = pieces[pieceIdx];
		const pathIdx = path.findIndex((t) => tile === t);
		const nextIdx = pathIdx + this.getRollValue();
		const nextTile = path[nextIdx];
		pieces[pieceIdx] = nextTile;

		// if piece lands on opponent's piece, reset
		// opponents piece to beginning
		const oppPieces = this.getOpponentPieces();
		const oppPath = this.getOpponentPath();
		if (oppPieces.includes(nextTile)) {
			const oppPieceIdx = oppPieces.findIndex((t) => nextTile === t);
			oppPieces[oppPieceIdx] = oppPath[0];
		}

		// when a player moves a piece onto a rosette tile,
		// they get to roll again
		if (!ROSETTE_TILES.includes(nextTile)) this.turn = !this.turn;
	}

	canMovePiece(pieceIdx: number): boolean {
		const pieces = this.getPieces();
		const path = this.getPath();

		const tile = pieces[pieceIdx];

		// cannot move piece that has already been scored
		if (tile === path.at(-1)) return false;

		const pathIdx = path.findIndex((t) => tile === t);
		const nextIdx = pathIdx + this.getRollValue();

		// piece must roll the exact amount of spaces left
		// in order to leave the board
		if (nextIdx >= path.length) return false;

		const nextTile = path[nextIdx];

		// piece cannot land on the player's other pieces
		if (nextTile !== path.at(-1) && pieces.includes(nextTile)) return false;

		// piece cannot land on opponent's piece if its on
		// the rosette in the center of the board
		const oppPieces = this.getOpponentPieces();
		if (nextTile === SAFE_ROSETTE_TILE && oppPieces.includes(nextTile)) {
			return false;
		}

		return true;
	}

	roll(): void {
		for (let i = 0; i < NUM_DICE; i++) {
			this.dice[i] = randint(6);
		}
	}

	getRollValue(): number {
		return this.dice
			.map((d) => (d > 2 ? 1 : 0))
			.reduce((sum: number, val: number) => sum + val, 0);
	}

	getP1Score(): number {
		return this.p1Pieces.filter((t) => t === P1_PATH.at(-1)).length;
	}

	getP2Score(): number {
		return this.p2Pieces.filter((t) => t === P2_PATH.at(-1)).length;
	}

	getP1UnusedPiecesCount(): number {
		return this.p1Pieces.filter((tile) => tile === P1_PATH[0]).length;
	}

	getP2UnusedPiecesCount(): number {
		return this.p2Pieces.filter((tile) => tile === P2_PATH[0]).length;
	}

	getWinner(): boolean | undefined {
		if (this.getP1Score() === NUM_PIECES) return P1;
		if (this.getP2Score() === NUM_PIECES) return P2;
		return undefined;
	}

	// :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
	// Current Player Data
	// :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

	getPieces(): number[] {
		return this.turn ? this.p1Pieces : this.p2Pieces;
	}

	getOpponentPieces(): number[] {
		return this.turn ? this.p2Pieces : this.p1Pieces;
	}

	getMovablePieceIndices(): number[] {
		const movable: number[] = [];
		for (let i = 0; i < NUM_PIECES; i++) {
			if (this.canMovePiece(i)) movable.push(i);
		}
		return movable;
	}

	getPath(): number[] {
		return this.turn ? P1_PATH : P2_PATH;
	}

	getOpponentPath(): number[] {
		return this.turn ? P2_PATH : P1_PATH;
	}
}

export function randint(max: number): number {
	return Math.floor(Math.random() * max);
}
