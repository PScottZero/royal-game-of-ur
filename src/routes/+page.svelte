<script lang="ts">
	import { base } from '$app/paths';
	import { NUM_PIECES, RoyalGameOfUr } from '$lib/ur';
	import { onMount } from 'svelte';

	const CANVAS_WIDTH = 1700;
	const CANVAS_HEIGHT = 700;
	const CANVAS_OFFSET = 64;
	const CANVAS_TILE_SIZE = 172;
	const CANVAS_TILE_OFFSET = 200;
	const CANVAS_PIECE_SIZE = 128;

	const INVISIBLE_TILES = [4, 5, 20, 21];
	const START_TILES = [4, 20];

	const game = new RoyalGameOfUr();

	let p1Score = $state(0);
	let p2Score = $state(0);
	let p1UnusedPiecesCount = $state(NUM_PIECES);
	let p2UnusedPiecesCount = $state(NUM_PIECES);
	let dice = $state([0, 0, 0, 0]);
	let turn = $state(true);
	let winner: boolean | undefined = $state(undefined);

	function getTileCenterCoords(tile: number): number[] {
		const col = tile % 8;
		const row = Math.floor(tile / 8);

		let x = col * CANVAS_TILE_OFFSET + CANVAS_OFFSET;
		let y = row * CANVAS_TILE_OFFSET + CANVAS_OFFSET;
		x += CANVAS_TILE_SIZE / 2;
		y += CANVAS_TILE_SIZE / 2;

		return [x, y];
	}

	function renderPieces() {
		const canvas = document.getElementById('pieces') as HTMLCanvasElement;
		const ctx = canvas.getContext('2d')!;

		const piece1 = document.getElementById('piece1') as HTMLImageElement;
		const piece2 = document.getElementById('piece2') as HTMLImageElement;

		const allPieces = game.p1Pieces.concat(game.p2Pieces);
		const currPieces = game.getPieces();
		const movablePieces = game.getMovablePieceIndices();

		ctx.clearRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);

		for (const pieceTile of allPieces) {
			const startTile = START_TILES[game.turn ? 0 : 1];
			const startPieceMovable =
				pieceTile === startTile &&
				movablePieces.includes(currPieces.indexOf(pieceTile));

			if (!INVISIBLE_TILES.includes(pieceTile) || startPieceMovable) {
				let [x, y] = getTileCenterCoords(pieceTile);
				if (startTile === pieceTile) {
					x += 16;
					y += game.turn ? -40 : 40;
				}

				const pieceIdx = game.getPieces().indexOf(pieceTile);
				if (movablePieces.includes(pieceIdx)) {
					ctx.fillStyle = '#0055ff';
					ctx.beginPath();
					ctx.arc(x, y, CANVAS_PIECE_SIZE / 2 + 8, 0, 2 * Math.PI);
					ctx.fill();
				}

				x -= CANVAS_PIECE_SIZE / 2;
				y -= CANVAS_PIECE_SIZE / 2;

				const img = game.p1Pieces.includes(pieceTile) ? piece1 : piece2;
				ctx.drawImage(img!, x, y, CANVAS_PIECE_SIZE, CANVAS_PIECE_SIZE);
			}
		}

		p1Score = game.getP1Score();
		p2Score = game.getP2Score();
		p1UnusedPiecesCount = game.getP1UnusedCount();
		p2UnusedPiecesCount = game.getP2UnusedCount();
		dice = game.dice;
		turn = game.turn;
		winner = game.getWinner();
	}

	function moveClickedPiece(e: MouseEvent) {
		const canvas = document.getElementById('pieces') as HTMLCanvasElement;
		const bounds = canvas.getBoundingClientRect();

		const canvasScreenWidth = bounds.right - bounds.left;
		const canvasScreenHeight = bounds.bottom - bounds.top;
		const xRatio = canvas.width / canvasScreenWidth;
		const yRatio = canvas.height / canvasScreenHeight;

		const x = Math.floor((e.clientX - bounds.left) * xRatio);
		const y = Math.floor((e.clientY - bounds.top) * yRatio);

		for (const pieceIdx of game.getMovablePieceIndices()) {
			const tile = game.getPieces()[pieceIdx];
			const [tileX, tileY] = getTileCenterCoords(tile);
			const lowerX = tileX - CANVAS_TILE_SIZE / 2;
			const upperX = tileX + CANVAS_TILE_SIZE / 2;
			const lowerY = tileY - CANVAS_TILE_SIZE / 2;
			const upperY = tileY + CANVAS_TILE_SIZE / 2;
			if (x >= lowerX && x <= upperX && y >= lowerY && y <= upperY) {
				game.move(pieceIdx);
				roll();
				break;
			}
		}
	}

	function dieClass(idx: number): string {
		let val = dice[idx];
		if (val > 2) val -= 3;
		if (val === 1) return 'rotate120';
		if (val === 2) return 'rotate240';
		return '';
	}

	function roll() {
		game.roll();
		renderPieces();
		if (game.getMovablePieceIndices().length === 0) {
			game.turn = !game.turn;
			setTimeout(() => roll(), 1500);
		}
	}

	function resetGame() {
		game.reset();
		roll();
	}

	onMount(() => {
		const canvas = document.getElementById('pieces') as HTMLCanvasElement;
		canvas.addEventListener('click', moveClickedPiece);
		roll();
		return () => {
			canvas.removeEventListener('click', moveClickedPiece);
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
	{#if winner !== undefined }
		<div id="reset">
			<p>Player {winner ? "1" : "2"} Wins!!!</p>
			<button onclick={resetGame}>New Game</button>
		</div>
	{/if}
	<img src="{base}/board.svg" alt="Game Board" />
	<canvas id="pieces" width={CANVAS_WIDTH} height={CANVAS_HEIGHT}></canvas>
</div>

<div id="menu">
	<div id="player1-info" class="player-info {turn ? 'turn' : ''}">
		<span>{p1Score}</span>
		{#each { length: p1UnusedPiecesCount }, _}
			<img src="{base}/piece1.svg" alt="Player 1 Piece" />
		{/each}
	</div>
	<div id="dice">
		{#each { length: 4 }, i}
			<img
				src="{base}/die{dice[i] > 2 ? '2' : '1'}.svg"
				class={dieClass(i)}
				alt="Die"
			/>
		{/each}
	</div>
	<div id="player2-info" class="player-info {turn ? '' : 'turn'}">
		{#each { length: p2UnusedPiecesCount }, _}
			<img src="{base}/piece2.svg" alt="Player 2 Piece" />
		{/each}
		<span>{p2Score}</span>
	</div>
</div>

<img src="{base}/piece1.svg" id="piece1" alt="P1 Piece" style="display: none" />
<img src="{base}/piece2.svg" id="piece2" alt="P2 Piece" style="display: none" />

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

		#grid {
			display: grid;
			grid-template-rows: 1fr auto 1fr;
			width: 100vw;
			height: 100vh;
			min-width: 42rem;
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
		display: grid;
		grid-template-columns: 12rem auto 12rem;
		align-items: end;
		padding: 0.5rem;
		gap: 0.5rem;
	}

	.player-info {
		display: flex;
		align-items: center;
		bottom: 1rem;
		font-family: 'Roboto Mono', monospace;
		font-size: 36px;
		border-radius: 4px;
		padding: 0.5rem;
		height: 4rem;

		img {
			display: inline-block;
			vertical-align: bottom;
			height: 3rem;
		}
	}

	#player1-info {
		justify-content: left;
		color: #e5ded1;
		border: 1px solid #374560;

		&.turn {
			border-color: #e5ded1;
		}

		img {
			margin-right: -2rem;

			&:last-child {
				margin-right: 0;
			}
		}

		span {
			margin-right: 0.5rem;
		}
	}

	#player2-info {
		justify-content: right;
		color: #95a6bd;
		border: 1px solid #374560;

		&.turn {
			border-color: #95a6bd;
		}

		img {
			margin-left: -2rem;

			&:first-child {
				margin-left: 0;
			}
		}

		span {
			margin-left: 0.5rem;
		}
	}

	#dice {
		position: relative;
		display: flex;
		justify-self: center;
		gap: 0.5rem;
		height: 4rem;
		overflow: hidden;

		img {
			height: 100%;
			transform-origin: center 63%;
		}
	}

	.rotate120 {
		transform: rotate(120deg);
	}

	.rotate240 {
		transform: rotate(240deg);
	}

	#reset {
		z-index: 1;
		position: absolute;
		top: 50%;
		left: 50%;
		transform: translate(-50%, -50%);
		border-radius: 4px;
		color: white;
		background-color: #374560;
		border: 1px solid white;
		padding: 4rem;
		font-size: 28px;

		button {
			width: 100%;
			height: 2rem;
			font-size: 18px;
		}
	}
</style>
