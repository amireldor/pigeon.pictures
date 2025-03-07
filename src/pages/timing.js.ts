import type { APIRoute } from "astro";
import { nextPigeonsISO, PERIOD_MS } from "../shared";

export const GET:APIRoute = async ({}) => {
    return new Response(`window.nextPigeons = new Date('${nextPigeonsISO}'); window.pigeonPeriod = ${PERIOD_MS};` );
}
