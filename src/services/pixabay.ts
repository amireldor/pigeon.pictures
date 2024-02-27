import { PIXABAY_API_KEY } from "../config";

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
  page = 1,
): Promise<PixabayResponse> {
  const response = await fetch(
    `${endpoint}?key=${PIXABAY_API_KEY}&q=${encodeURIComponent(query)}&image_type=photo&category=animals,transportation&page=${page}&per_page=20&order=latest`,
  );
  if (response.status >= 200 && response.status < 300) {
    return (await response.json()) as PixabayResponse;
  }
  throw new Error("Error while fetching images");
}
