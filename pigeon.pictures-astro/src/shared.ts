export const PIGEONS_TO_SHOW = 20;
export const PERIOD_MS = 1000 * 60;
export const nextPigeonsISO = new Date(new Date().getTime() + PERIOD_MS).toISOString();

export const pigeonRandomizedIds = Array.from(
	{ length: PIGEONS_TO_SHOW },
	() => Math.floor(Math.random() * 1000).toString().padStart(3, "0")
);
