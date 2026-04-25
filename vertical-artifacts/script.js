fetch('body.html')
	.then((response) => response.text())
	.then((html) => {
		document.body.insertAdjacentHTML('afterbegin', html);
	});

let map = null;

function changeStyle(styleFile) {
	if (!map) {
		map = initMap(styleFile);
	} else {
		map.setStyle(styleFile);
	}
}

function initMap(styleFile) {
	const map = (window.map = new maplibregl.Map({
		container: 'map',
		zoom: 12,
		center: [11.39085, 47.27574],
		pitch: 70,
		hash: true,
		style: `${styleFile}`,
		maxZoom: 18,
		maxPitch: 85,
		disableTerrainVerticalExtensions: true
	}));

	map.addControl(
		new maplibregl.NavigationControl({
			visualizePitch: true,
			showZoom: true,
			showCompass: true
		})
	);

	map.addControl(
		new maplibregl.TerrainControl({
			source: 'terrainSource',
			exaggeration: 1
		})
	);

	Array.from(document.getElementsByClassName('startupOnly')).forEach((el) => {
		el.remove();
	});
	return map;
}
