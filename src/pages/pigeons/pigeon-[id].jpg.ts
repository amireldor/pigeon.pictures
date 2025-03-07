import type { APIRoute } from "astro";
import { getSecret } from "astro:env/server";
import { pigeonRandomizedIds, PIGEONS_TO_SHOW } from "../../shared";

const page = Math.floor(Math.random() * 20) + 1;
const PIXABAY_API_KEY = getSecret("PIXABAY_API_KEY");
const PIXABAY_API_URL = `https://pixabay.com/api/?key=${PIXABAY_API_KEY}&q=pigeon&image_type=photo&page=${page}&per_page=${PIGEONS_TO_SHOW}`;

const response = await fetch(PIXABAY_API_URL);
const data = await response.json();

const images: { largeImageURL: string }[] = data.hits;

	if (!images.length) {
		throw new Error("No pigeon images found");
	}


export const GET: APIRoute = async ({ props}) => {
	const { index } = props;
	const image = images[index];

	if (!image) {
		throw new Error("Pigeon image not found");
	}
	
	const imageResponse = await fetch(image.largeImageURL);
	const imageBuffer = await imageResponse.arrayBuffer();

	return new Response(imageBuffer);
};


export function getStaticPaths() {
	return pigeonRandomizedIds.map((id, index) => ({
		params: { id },
		props: {index },
	}));
}