<script lang="ts">
	import { base } from '$app/paths';
</script>

<svelte:head>
	<title>Royal Game of Ur</title>
</svelte:head>

<div id="sidebar">
	<p class="cuneiform">𒊒𒅋 𒂵𒅎 𒄴 𒌨</p>
</div>

<div id="board">
	<img src="{base}/board.svg" alt="Game Board" />
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
			font-family: Arial, Helvetica, sans-serif;
		}

		body {
			display: grid;
			grid-template-columns: 20rem 1fr;
			width: 100vw;
			height: 100vh;
		}

		a {
			text-decoration: none;
		}
	}

	@font-face {
		font-family: 'CuneiformNA';
		src: url('/CuneiformNA.ttf');
	}

	#sidebar {
		background-color: #c8ba9f;
		padding: 1rem;
	}

	#board {
		padding: 5%;

		img {
			width: 100%;
			height: 100%;
		}
	}

	.cuneiform {
		font-family: 'CuneiformNA';
		font-size: 20px;
		font-weight: bold;
	}
</style>
