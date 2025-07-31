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

	const P1 = true;
	const P2 = false;

	const P1_PATH = [4, 3, 2, 1, 0, 8, 9, 10, 11, 12, 13, 14, 15, 7, 6, 5];
	const P2_PATH = [
		20, 19, 18, 17, 16, 8, 9, 10, 11, 12, 13, 14, 15, 23, 22, 21
	];

	const INVISIBLE_TILES = [4, 5, 20, 21];
	const ROSETTE_TILES = [0, 6, 11, 16, 22];
	const SAFE_ROSETTE_TILE = 11;

	let p1Score = $state(0);
	let p2Score = $state(0);

	class RoyalGameOfUr {
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

		getMovablePieceIndices(): number[] {
			const movable: number[] = [];
			for (let i = 0; i < NUM_PIECES; i++) {
				if (this.canMovePiece(i)) movable.push(i);
			}
			return movable;
		}

		// getUsedPieceIndices(): number[] {
		// 	const pieces = this.getPieces();
		// 	const path = this.getPath();
		// 	return pieces
		// 		.filter((tile) => tile !== path[0])
		// 		.map((tile) => pieces.indexOf(tile));
		// }

		// getUnusedPieceIndices(): number[] {
		// 	const pieces = this.getPieces();
		// 	const path = this.getPath();
		// 	return pieces
		// 		.filter((tile) => tile === path[0])
		// 		.map((tile) => pieces.indexOf(tile));
		// }

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

	function getTileCenterCoords(tile: number): number[] {
		const col = tile % 8;
		const row = Math.floor(tile / 8);

		let x = col * CANVAS_TILE_OFFSET + CANVAS_OFFSET;
		let y = row * CANVAS_TILE_OFFSET + CANVAS_OFFSET;
		x += CANVAS_TILE_SIZE / 2;
		y += CANVAS_TILE_SIZE / 2;

		return [x, y];
	}

	function clickToTile(e: MouseEvent): number {
		const canvas = document.getElementById('pieces') as HTMLCanvasElement;
		const bounds = canvas.getBoundingClientRect();

		const canvasScreenWidth = bounds.right - bounds.left;
		const canvasScreenHeight = bounds.bottom - bounds.top;
		const xRatio = canvas.width / canvasScreenWidth;
		const yRatio = canvas.height / canvasScreenHeight;

		const x = Math.floor((e.clientX - bounds.left) * xRatio);
		const y = Math.floor((e.clientY - bounds.top) * yRatio);

		for (let tile = 0; tile < NUM_TILES; tile++) {
			const [tileX, tileY] = getTileCenterCoords(tile);
			const lowerX = tileX - CANVAS_TILE_SIZE / 2;
			const upperX = tileX + CANVAS_TILE_SIZE / 2;
			const lowerY = tileY - CANVAS_TILE_SIZE / 2;
			const upperY = tileY + CANVAS_TILE_SIZE / 2;
			if (x >= lowerX && x <= upperX && y >= lowerY && y <= upperY) {
				return tile;
			}
		}

		return -1;
	}

	function renderPieces() {
		const canvas = document.getElementById('pieces') as HTMLCanvasElement;
		const ctx = canvas.getContext('2d')!;

		ctx.clearRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);

		for (let tile = 0; tile < NUM_TILES; tile++) {
			const drawP1Piece = game.p1Pieces.includes(tile);
			const drawP2Piece = game.p2Pieces.includes(tile);

			if ((drawP1Piece || drawP2Piece) && !INVISIBLE_TILES.includes(tile)) {
				const img = new Image();
				img.src = `${base}/${drawP1Piece ? 'piece1' : 'piece2'}.svg`;
				img.onload = () => {
					let [x, y] = getTileCenterCoords(tile);
					x -= CANVAS_PIECE_SIZE / 2;
					y -= CANVAS_PIECE_SIZE / 2;
					ctx.drawImage(img, x, y, CANVAS_PIECE_SIZE, CANVAS_PIECE_SIZE);
				};
			}
		}

		p1Score = game.getP1Score();
		p2Score = game.getP2Score();
	}

	function takeTurn() {
		if (game.getWinner() !== undefined) game.reset();
		game.roll();
		const movable = game.getMovablePieceIndices();
		if (movable.length > 0) {
			const idx = randint(2) === 0 ? randint(movable.length) : 0;
			const pieceIdx = movable[idx];
			game.move(pieceIdx);
			renderPieces();
		}
		setTimeout(takeTurn, 2000);
	}

	function randint(max: number): number {
		return Math.floor(Math.random() * max);
	}

	onMount(() => {
		const canvas = document.getElementById('pieces') as HTMLCanvasElement;
		canvas.addEventListener('click', clickToTile);
		const timeout = setTimeout(takeTurn, 2000);
		return () => {
			canvas.removeEventListener('click', clickToTile);
			clearTimeout(timeout);
		};
	});
</script>

<svelte:head>
	<title>Royal Game of Ur</title>
</svelte:head>

<div id="title">
	Royal Game of Ur&nbsp;&nbsp;|&nbsp;&nbsp;
	<span class="cuneiform">𒊒𒅋 𒂵𒅎 𒄴 𒌨</span>
</div>

<div id="board">
	<img src="{base}/board.svg" alt="Game Board" />
	<canvas id="pieces" width={CANVAS_WIDTH} height={CANVAS_HEIGHT}></canvas>
</div>

<div id="menu">
	<div id="player1-info" class="player-info">
		{p1Score}
	</div>
	<div id="player2-info" class="player-info">
		{p2Score}
	</div>
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
		position: relative;
	}

	.player-info {
		position: absolute;
		text-align: center;
		bottom: 1rem;
		font-size: 36px;
		border-radius: 4px;
		width: 3rem;
		height: 3rem;
		line-height: 2.65rem;
	}

	#player1-info {
		color: #e5ded1;
		border: 1px solid #e5ded1;
		left: 1rem;
	}

	#player2-info {
		color: #9296b8;
		border: 1px solid #9296b8;
		right: 1rem;
	}
</style>
