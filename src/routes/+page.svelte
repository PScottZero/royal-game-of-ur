<script lang="ts">
	import { base } from '$app/paths';
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
			color: black;
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
		padding: 0 2rem;

		img {
			object-fit: contain;
			width: 100%;
			height: 100%;
		}
	}

	#menu {
		display: flex;
		justify-content: center;
		align-items: center;
	}
</style>
