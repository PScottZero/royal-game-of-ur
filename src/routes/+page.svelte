<script lang="ts">
	import { base } from '$app/paths';
	import { onMount } from 'svelte';

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

	const NUM_TILES = 24;
	const NUM_PIECES = 7;
	const NUM_DICE = 4;

	const CANVAS_WIDTH = 1700;
	const CANVAS_HEIGHT = 700;
	const CANVAS_OFFSET = 64;
	const CANVAS_TILE_SIZE = 172;
	const CANVAS_TILE_OFFSET = 200;
	const CANVAS_PIECE_SIZE = 128;

	const P1_COLOR = "#0000ff";
	const P2_COLOR = "#ff0000";

	const P1 = true;
	const P2 = false;

	const P1_PATH = [4, 3, 2, 1, 0, 8, 9, 10, 11, 12, 13, 14, 15, 7, 6, 5];
	const P2_PATH = [
		20, 19, 18, 17, 16, 8, 9, 10, 11, 12, 13, 14, 15, 23, 22, 21
	];

	const INVISIBLE_TILES = [4, 5, 20, 21];
	const ROSETTE_TILES = [0, 6, 11, 16, 22];
	const SAFE_ROSETTE_TILE = 11;

	class RoyalGameOfUr {
		p1Pieces: number[];
		p2Pieces: number[];
		dice: number[];
		turn: boolean;

		constructor() {
			this.p1Pieces = $state(new Array(NUM_PIECES).fill(P1_PATH[0]));
			this.p2Pieces = $state(new Array(NUM_PIECES).fill(P2_PATH[0]));
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
				this.dice[i] = Math.floor(Math.random() * 6);
			}
		}

		getRollValue(): number {
			return this.dice
				.map((d) => (d > 2 ? 1 : 0))
				.reduce((sum: number, val: number) => sum + val, 0);
		}

		// :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
		// Current Player Data
		// :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

		getPieces(): number[] {
			return this.turn ? this.p1Pieces : this.p2Pieces;
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

		getOpponentPieces(): number[] {
			return this.turn ? this.p2Pieces : this.p1Pieces;
		}

		getOpponentPath(): number[] {
			return this.turn ? P2_PATH : P1_PATH;
		}
	}

	const game = new RoyalGameOfUr();
	
	// game.p1Pieces[0] = 0;
	// game.p1Pieces[1] = 1;
	// game.p1Pieces[2] = 2;
	// game.p1Pieces[3] = 3;
	// game.p1Pieces[4] = 8;
	// game.p1Pieces[5] = 10;
	// game.p1Pieces[6] = 12;

	// game.p2Pieces[0] = 16;
	// game.p2Pieces[1] = 17;
	// game.p2Pieces[2] = 18;
	// game.p2Pieces[3] = 19;
	// game.p2Pieces[4] = 9;
	// game.p2Pieces[5] = 11;
	// game.p2Pieces[6] = 13;

	function renderPieces() {
		const canvas = document.getElementById('pieces') as HTMLCanvasElement;
		const ctx = canvas.getContext('2d')!;

		for (let tile = 0; tile < NUM_TILES; tile++) {
			const drawP1Piece = game.p1Pieces.includes(tile);
			const drawP2Piece = game.p2Pieces.includes(tile);
			
			if ((drawP1Piece || drawP2Piece) && !INVISIBLE_TILES.includes(tile)) {
				const col = tile % 8;
				const row = Math.floor(tile / 8);
				
				let x = col * CANVAS_TILE_OFFSET + CANVAS_OFFSET;
				let y = row * CANVAS_TILE_OFFSET + CANVAS_OFFSET;
				x += CANVAS_TILE_SIZE / 2;
				y += CANVAS_TILE_SIZE / 2;

				ctx.fillStyle = drawP1Piece ? P1_COLOR : P2_COLOR;
				ctx.beginPath();
				ctx.arc(x, y, CANVAS_PIECE_SIZE / 2, 0, 2 * Math.PI);
				ctx.fill();
			}
		}
	}

	onMount(() => renderPieces());
</script>

<svelte:head>
	<title>Royal Game of Ur</title>
</svelte:head>

<div id="title">
	Royal Game of Ur&nbsp;&nbsp;|&nbsp;&nbsp;
	<span class="cuneiform">𒊒𒅋𒂵𒅎𒄴𒌨</span>
</div>

<div id="board">
	<img src="{base}/board.svg" alt="Game Board" />
	<canvas id="pieces" width={CANVAS_WIDTH} height={CANVAS_HEIGHT}></canvas>
</div>

<div id="menu">
	<h1>⚠ WORK IN PROGRESS ⚠</h1>
</div>

<style lang="scss">
	:global {
		* {
			box-sizing: border-box;
			padding: 0;
			margin: 0;
		}

		html,
		body {
			color: white;
			background-color: #374560;
			font-family: 'Raleway', Arial, Helvetica, sans-serif;
		}

		body {
			display: grid;
			grid-template-rows: 1fr auto 1fr;
			width: 100vw;
			height: 100vh;
		}

		a {
			text-decoration: none;
		}
	}

	@font-face {
		font-family: 'Assurbanipal';
		src: url('/Assurbanipal.ttf');
	}

	#title {
		display: flex;
		justify-content: center;
		align-items: center;
		font-size: 28px;
		padding: 2rem;
	}

	.cuneiform {
		display: inline-block;
		transform: translateY(3px);
		font-family: 'Assurbanipal';
		font-size: 36px;
	}

	#board {
		position: relative;
		width: 100%;
		height: 100%;
		padding: 0 4rem;

		img {
			width: 100%;
			height: 100%;
		}
	}

	#pieces {
		position: absolute;
		top: 0;
		left: 4rem;
		width: calc(100% - 8rem);
		height: 100%;
	}

	#menu {
		display: flex;
		justify-content: center;
		align-items: center;
	}
</style>
