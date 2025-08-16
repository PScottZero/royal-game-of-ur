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

	const P1_START_END_TILES = [4, 5];
	const START_TILES = [4, 20];
	const INVISIBLE_TILES = [4, 5, 20, 21];

	const BASE_MOVE_DURATION_MS = 100;

	const game = new RoyalGameOfUr();

	let p1Score = $state(0);
	let p2Score = $state(0);
	let p1UnusedPiecesCount = $state(NUM_PIECES);
	let p2UnusedPiecesCount = $state(NUM_PIECES);
	let dice = $state([0, 0, 0, 0]);
	let turn = $state(true);
	let winner: boolean | undefined = $state(undefined);

	let movingPieceStartTile = -1;
	let movingPieceEndTile = -1;
	let movingPieceIdx = 0;
	let moveStartTime = Date.now();

	let piece1Img: HTMLImageElement | undefined = undefined;
	let piece2Img: HTMLImageElement | undefined = undefined;

	function getTileCenterCoords(tile: number): number[] {
		const col = tile % 8;
		const row = Math.floor(tile / 8);

		let x = col * CANVAS_TILE_OFFSET + CANVAS_OFFSET;
		let y = row * CANVAS_TILE_OFFSET + CANVAS_OFFSET;
		x += CANVAS_TILE_SIZE / 2;
		y += CANVAS_TILE_SIZE / 2;

		if (INVISIBLE_TILES.includes(tile)) {
			x += START_TILES.includes(tile) ? 16 : -16;
			y += P1_START_END_TILES.includes(tile) ? -40 : 40;
		}

		return [x, y];
	}

	function tileCoordsToPieceCoords(x: number, y: number): number[] {
		return [x - CANVAS_PIECE_SIZE / 2, y - CANVAS_PIECE_SIZE / 2];
	}

	function getMoveDuration(): number {
		let tile1 = movingPieceStartTile;
		let tile2 = movingPieceEndTile;

		const tile1OnCenterRow = tile1 >= 8 && tile1 < 16;
		const tile2OnCenterRow = tile2 >= 8 && tile2 < 16;

		let rowTransition = 0;
		if (tile1OnCenterRow && !tile2OnCenterRow) {
			tile2 += tile2 < 8 ? 8 : -8;
			rowTransition = 1;
		} else if (!tile1OnCenterRow && tile2OnCenterRow) {
			tile1 += tile1 < 8 ? 8 : -8;
			rowTransition = 1;
		}

		const durationMult = Math.abs(tile1 - tile2) + rowTransition;
		return durationMult * BASE_MOVE_DURATION_MS;
	}

	function renderPieces(animateMove: boolean = false) {
		const moveDuration = getMoveDuration();
		const elapsedTime = Date.now() - moveStartTime;
		let moveProgress = elapsedTime / moveDuration;

		if (animateMove && moveProgress >= 1) moveProgress = 1;

		const canvas = document.getElementById('pieces') as HTMLCanvasElement;
		const ctx = canvas.getContext('2d')!;
		ctx.clearRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);

		const pieces = game.getPieces();
		const movablePieces = game.getMovablePieceIndices();

		for (const pieceTile of game.getBoardPieces()) {
			let [x, y] = getTileCenterCoords(pieceTile);

			const isMovingPiece = animateMove && movingPieceStartTile === pieceTile;
			const pieceIdx = pieces.indexOf(pieceTile);

			if (!isMovingPiece && movablePieces.includes(pieceIdx)) {
				ctx.fillStyle = '#0055ff';
				ctx.beginPath();
				ctx.arc(x, y, CANVAS_PIECE_SIZE / 2 + 8, 0, 2 * Math.PI);
				ctx.fill();
			}

			[x, y] = tileCoordsToPieceCoords(x, y);

			if (isMovingPiece) {
				let [endX, endY] = getTileCenterCoords(movingPieceEndTile);
				[endX, endY] = tileCoordsToPieceCoords(endX, endY);
				x += (endX - x) * moveProgress;
				y += (endY - y) * moveProgress;
			}

			const img = game.p1Pieces.includes(pieceTile) ? piece1Img : piece2Img;
			ctx.drawImage(img!, x, y, CANVAS_PIECE_SIZE, CANVAS_PIECE_SIZE);
		}

		if (animateMove) {
			if (moveProgress < 1) {
				requestAnimationFrame(() => renderPieces(true));
				return;
			} else {
				game.move(movingPieceIdx);
				roll();
			}
		} else {
			p1Score = game.getP1Score();
			p2Score = game.getP2Score();
			p1UnusedPiecesCount = game.getP1UnusedCount();
			p2UnusedPiecesCount = game.getP2UnusedCount();
			dice = game.dice;
			turn = game.turn;
			winner = game.getWinner();
		}
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

		const pieces = game.getPieces();
		const path = game.getPath();

		for (const pieceIdx of game.getMovablePieceIndices()) {
			const tile = pieces[pieceIdx];
			const [tileX, tileY] = getTileCenterCoords(tile);

			const lowerX = tileX - CANVAS_TILE_SIZE / 2;
			const upperX = tileX + CANVAS_TILE_SIZE / 2;
			const lowerY = tileY - CANVAS_TILE_SIZE / 2;
			const upperY = tileY + CANVAS_TILE_SIZE / 2;

			if (x >= lowerX && x <= upperX && y >= lowerY && y <= upperY) {
				movingPieceStartTile = tile;
				movingPieceEndTile = path[path.indexOf(tile) + game.getRollValue()];
				movingPieceIdx = pieceIdx;
				moveStartTime = Date.now();
				requestAnimationFrame(() => renderPieces(true));
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
		requestAnimationFrame(() => {
			renderPieces();
			if (game.getMovablePieceIndices().length === 0) {
				game.turn = !game.turn;
				setTimeout(() => roll(), 1500);
			}
		});
	}

	function resetGame() {
		game.reset();
		roll();
	}

	onMount(() => {
		const canvas = document.getElementById('pieces') as HTMLCanvasElement;
		canvas.addEventListener('click', moveClickedPiece);

		piece1Img = new Image();
		piece2Img = new Image();
		piece1Img.src = `${base}/piece1.svg`;
		piece2Img.src = `${base}/piece2.svg`;

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

<div id="board-wrapper">
	<div id="board">
		{#if winner !== undefined}
			<div id="reset">
				<p>Player {winner ? '1' : '2'} Wins!!!</p>
				<button onclick={resetGame}>New Game</button>
			</div>
		{/if}
		<img src="{base}/board.svg" alt="Game Board" />
		<canvas id="pieces" width={CANVAS_WIDTH} height={CANVAS_HEIGHT}></canvas>
	</div>
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
			grid-template-rows: auto 1fr auto;
			width: 100vw;
			height: 100vh;
			min-width: 44rem;
		}

		a {
			text-decoration: none;
		}
	}

	@font-face {
		font-family: 'Assurbanipal';
		src: url('/Assurbanipal.ttf');
	}

	@mixin mobile {
		@media screen and (max-width: 1024px) {
			@content;
		}
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

	#board-wrapper {
		display: flex;
		justify-content: center;
		align-items: center;
	}

	#board {
		position: relative;
		width: 100%;
		height: auto;
		padding: 0 10%;

		img {
			width: 100%;
			height: 100%;
		}
	}

	#pieces {
		position: absolute;
		top: 0;
		left: 10%;
		width: 80%;
		height: 100%;
	}

	#menu {
		display: grid;
		grid-template-columns: 12.5rem auto 12.5rem;
		align-items: end;
		padding: 0.5rem;
		gap: 0.5rem;
	}

	.player-info {
		transition: 0.1s;
		display: flex;
		align-items: center;
		bottom: 1rem;
		font-family: 'Roboto Mono', monospace;
		font-size: 36px;
		height: 4rem;
		border-radius: 2rem;
		padding: 0.5rem;

		img {
			display: inline-block;
			vertical-align: bottom;
			height: 3rem;
		}

		span {
			margin: 0 0.5rem;
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
	}

	#dice {
		position: relative;
		display: flex;
		justify-self: center;
		gap: 0.5rem;
		height: 4rem;
		overflow: hidden;

		img {
			transition: 0.2s;
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
