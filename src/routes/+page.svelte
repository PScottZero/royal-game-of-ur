<script lang="ts">
	import { base } from '$app/paths';
	import { NUM_PIECES, randint, RoyalGameOfUr } from '$lib/ur';
	import { onMount } from 'svelte';

	const CANVAS_WIDTH = 1700;
	const CANVAS_HEIGHT = 700;
	const CANVAS_OFFSET = 64;
	const CANVAS_TILE_SIZE = 172;
	const CANVAS_TILE_OFFSET = 200;
	const CANVAS_PIECE_SIZE = 128;

	const NUM_TILES = 24;
	const INVISIBLE_TILES = [4, 5, 20, 21];

	let p1Score = $state(0);
	let p2Score = $state(0);
	let p1UnusedPiecesCount = $state(NUM_PIECES);
	let p2UnusedPiecesCount = $state(NUM_PIECES);

	let pieceImg1: HTMLImageElement | undefined = undefined;
	let pieceImg2: HTMLImageElement | undefined = undefined;

	function loadImage(imageName: string): HTMLImageElement {
		const img = new Image();
		img.src = `${base}/${imageName}`;
		img.onload = renderPieces;
		return img;
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
		if (pieceImg1 !== undefined && pieceImg2 !== undefined) {
			const canvas = document.getElementById('pieces') as HTMLCanvasElement;
			const ctx = canvas.getContext('2d')!;

			ctx.clearRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);

			for (let tile = 0; tile < NUM_TILES; tile++) {
				const drawP1Piece = game.p1Pieces.includes(tile);
				const drawP2Piece = game.p2Pieces.includes(tile);

				if ((drawP1Piece || drawP2Piece) && !INVISIBLE_TILES.includes(tile)) {
					const img = drawP1Piece ? pieceImg1 : pieceImg2;
					let [x, y] = getTileCenterCoords(tile);
					x -= CANVAS_PIECE_SIZE / 2;
					y -= CANVAS_PIECE_SIZE / 2;
					ctx.drawImage(img!, x, y, CANVAS_PIECE_SIZE, CANVAS_PIECE_SIZE);
				}
			}

			p1Score = game.getP1Score();
			p2Score = game.getP2Score();
			p1UnusedPiecesCount = game.getP1UnusedPiecesCount();
			p2UnusedPiecesCount = game.getP2UnusedPiecesCount();
		}
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

	onMount(() => {
		pieceImg1 = loadImage('piece1.svg');
		pieceImg2 = loadImage('piece2.svg');

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
		<span>P1 {p1Score}</span>
		{#each { length: p1UnusedPiecesCount }, i}
			<img src="{base}/piece1.svg" alt="Player 1 Piece" />
		{/each}
	</div>
	<div id="player2-info" class="player-info">
		{#each { length: p2UnusedPiecesCount }, i}
			<img src="{base}/piece2.svg" alt="Player 2 Piece" />
		{/each}
		<span>{p2Score} P2</span>
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
		display: flex;
		align-items: center;
		bottom: 1rem;
		font-size: 36px;
		border-radius: 4px;
		padding: 0.5rem;

		img {
			display: inline-block;
			vertical-align: bottom;
			height: 3rem;
		}
	}

	#player1-info {
		color: #e5ded1;
		border: 1px solid #e5ded1;
		left: 1rem;

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
		color: #95a6bd;
		border: 1px solid #95a6bd;
		right: 1rem;

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
</style>
