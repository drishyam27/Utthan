import { STATES, DISTRICTS } from '../src/data/locations.js';

const stateIdSet = new Set(STATES.map(s => s.id));
let orphans = 0;
for (const d of DISTRICTS) {
  if (!stateIdSet.has(d.stateId)) orphans++;
}

const lgdCodes = new Set();
let dupLgd = 0;
for (const d of DISTRICTS) {
  if (lgdCodes.has(d.lgdDistrictCode)) dupLgd++;
  lgdCodes.add(d.lgdDistrictCode);
}

console.log(`States: ${STATES.length}`);
console.log(`Districts: ${DISTRICTS.length}`);
console.log(`Unique LGD district codes: ${lgdCodes.size}`);
console.log(`Orphans: ${orphans}`);
console.log(`Duplicate LGD district codes: ${dupLgd}`);
