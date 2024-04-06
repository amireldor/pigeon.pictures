import { PIXABAY_API_KEY } from "../config";
import { PictureFetcher } from "./picture-fetcher";
import type { PigeonPicture } from "./picture-fetcher";
import { generatePigeonSearchTerm } from "./term-generator";

const endpoint = "https://pixabay.com/api/";

export interface PixabayImage {
  id: number;
  pageURL: string;
  type: string;
  tags: string;
  previewURL: string;
  previewWidth: number;
  previewHeight: number;
  webformatURL: string;
  webformatWidth: number;
  webformatHeight: number;
  largeImageURL: string;
  fullHDURL: string;
  imageURL: string;
  imageWidth: number;
  imageHeight: number;
  imageSize: number;
  views: number;
  downloads: number;
  likes: number;
  comments: number;
  user_id: number;
  user: string;
  userImageURL: string;
}

export interface PixabayResponse {
  total: number;
  totalHits: number;
  hits: PixabayImage[];
}

export async function fetchImages(
  query: string,
  page = 1
): Promise<PixabayResponse> {
  const response = await fetch(
    `${endpoint}?key=${PIXABAY_API_KEY}&q=${encodeURIComponent(query)}&image_type=photo&category=animals,transportation&page=${page}&per_page=20&order=latest`
  );
  if (response.status >= 200 && response.status < 300) {
    return (await response.json()) as PixabayResponse;
  }
  throw new Error("Error while fetching images");
}

export class PixabayPictureFetcher extends PictureFetcher {
  async fetchImages(): Promise<PigeonPicture[]> {
    const searchTerms: [string, number][] = [
      [generatePigeonSearchTerm(), Math.ceil(Math.random() * 3)],
      [generatePigeonSearchTerm(), Math.ceil(Math.random() * 3)],
      [generatePigeonSearchTerm(), Math.ceil(Math.random() * 3)],
    ];

    searchTerms.forEach(([term, page]) => {
      console.log(`Searching for term: "${term}" pn page ${page}...`);
    });

    const fetchPromises = searchTerms.map(([term, page]) =>
      fetchImages(term, page)
    );
    const responses = await Promise.all(fetchPromises);
    const hits = responses.reduce(
      (acc, response) => acc.concat(...response.hits),
      [] as PixabayImage[]
    );
    console.log(`Got ${hits.length} hits.`);

    const pickedIndices = new Set<number>();
    while (pickedIndices.size < Math.min(20, hits.length)) {
      pickedIndices.add(Math.floor(Math.random() * hits.length));
    }

    const pickedImages = Array.from(pickedIndices).map((index) => hits[index]);

    return pickedImages.map((hit) => ({
      id: hit.id.toString(),
      pageURL: hit.pageURL,
      imageURL: hit.largeImageURL,
    }));
  }
}
