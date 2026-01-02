// ----------------------------
// Kartenparameter (ANPASSEN!)
// ----------------------------

// Größe deiner map.png
const MAP_WIDTH  = 8192;
const MAP_HEIGHT = 8192;

// Region-Grid-Abdeckung deiner Karte
// Beispiel: Nautilus + Umgebung
const GRID_MIN_X = 950;
const GRID_MAX_X = 1050;
const GRID_MIN_Y = 950;
const GRID_MAX_Y = 1050;

const REGION_SIZE = 256;

// ----------------------------
// Leaflet initialisieren
// ----------------------------
const map = L.map("map", {
  crs: L.CRS.Simple,
  minZoom: -3,
  maxZoom: 4,
  zoomControl: true
});

// Bildkoordinaten
const imageBounds = [
  [0, 0],
  [MAP_HEIGHT, MAP_WIDTH]
];

// Hintergrundbild
L.imageOverlay("map.png", imageBounds).addTo(map);
map.fitBounds(imageBounds);

// ----------------------------
// SL → Bildkoordinaten
// ----------------------------
function slToImageXY(gridX, gridY, x, y) {
  const gridWidth  = GRID_MAX_X - GRID_MIN_X;
  const gridHeight = GRID_MAX_Y - GRID_MIN_Y;

  const worldX = (gridX - GRID_MIN_X) * REGION_SIZE + x;
  const worldY = (gridY - GRID_MIN_Y) * REGION_SIZE + y;

  const scaleX = MAP_WIDTH  / (gridWidth  * REGION_SIZE);
  const scaleY = MAP_HEIGHT / (gridHeight * REGION_SIZE);

  return [
    MAP_HEIGHT - worldY * scaleY,
    worldX * scaleX
  ];
}

// ----------------------------
// Marker aus SLURLs
// ----------------------------
fetch("slurls.json")
  .then(r => r.json())
  .then(data => {
    data.forEach(p => {
      const pos = slToImageXY(
        p.grid_x,
        p.grid_y,
        p.x,
        p.y
      );

      const slurl =
        `https://maps.secondlife.com/secondlife/` +
        `${encodeURIComponent(p.region)}/` +
        `${p.x}/${p.y}/${p.z}`;

      L.marker(pos)
        .addTo(map)
        .bindPopup(`
          <strong>${p.name}</strong><br>
          ${p.region}<br>
          <a href="${slurl}" target="_blank">Open SLURL</a>
        `);
    });
  });

