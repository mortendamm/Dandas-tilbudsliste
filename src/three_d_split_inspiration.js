/*
  Det her er ikke hele viewer-koden.
  Det er kun en kort, forklarende version af 3D-opdelingen.

  Ideen i hovedløsningen er:
  - en brønd tegnes ikke som én anonym cylinder
  - den deles i komponenter, så modellen svarer bedre til den tilbudsliste
  - samme princip bruges på ledninger, hvor vi viser rørstykker og samlinger
*/

export function describeManholeSplit({ diameterMm, depthM, materiale }) {
  const isPp = /PP|PE|PVC|plast/i.test(materiale || "");
  const parts = [];

  parts.push({
    component: "bundstykke",
    note: "placeres nederst i brønden",
  });

  parts.push({
    component: "skaktringe",
    note: isPp
      ? "PP-ringe bruges til at bygge skakten op"
      : "betonringe bruges til at bygge skakten op",
  });

  if (!isPp && (diameterMm || 0) >= 1000) {
    parts.push({
      component: "reduktionskegle",
      note: "bruges når den store betonskakt reduceres op mod dækselzonen",
    });
  }

  parts.push({
    component: "justeringsringe",
    note: "finjusterer højden mod terræn",
  });

  parts.push({
    component: "ramme_og_daeksel",
    note: "øverste synlige del i terræn",
  });

  return {
    shape: "manhole",
    diameterMm,
    depthM,
    materiale,
    parts,
  };
}

export function describePipeSplit({ lengthM, diameterMm }) {
  const standardSegmentLength = 3.0;
  const segmentCount = Math.max(1, Math.ceil((lengthM || 0) / standardSegmentLength));
  const couplingCount = Math.max(0, segmentCount - 1);

  return {
    shape: "pipe",
    diameterMm,
    lengthM,
    segments: segmentCount,
    couplings: couplingCount,
    note: "i den rigtige viewer bygges de som separate mesh-dele langs linjeforløbet",
  };
}

