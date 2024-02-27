import { fetchImages, type PixabayImage } from "./services/pixabay";
import { generatePigeonSearchTerm } from "./services/term-generator";

console.log("Pigeon Pictures!");

const searchTerms: [string, number][] = [
  [generatePigeonSearchTerm(), Math.ceil(Math.random() * 3)],
  [generatePigeonSearchTerm(), Math.ceil(Math.random() * 3)],
  [generatePigeonSearchTerm(), Math.ceil(Math.random() * 3)],
];

searchTerms.forEach(([term, page]) => {
  console.log(`Searching for term: "${term}" pn page ${page}...`);
});

const fetchPromises = searchTerms.map(([term, page]) =>
  fetchImages(term, page),
);
const responses = await Promise.all(fetchPromises);
const hits = responses.reduce(
  (acc, response) => acc.concat(...response.hits),
  [] as PixabayImage[],
);
console.log(`Got ${hits.length} hits.`);

const pickedIndices = new Set<number>();
while (pickedIndices.size < Math.min(20, hits.length)) {
  pickedIndices.add(Math.floor(Math.random() * hits.length));
}

const pickedImages = Array.from(pickedIndices).map((index) => hits[index]);

console.log("Downloading images...");
const downloadPromises = pickedImages.map(async (image) =>
  Bun.write(
    `output/downloads/${image.id.toString()}.jpg`,
    await fetch(image.largeImageURL),
  ),
);
await Promise.all(downloadPromises);
console.log("Writing HTML...");

const template = await Bun.file("src/template.html").text();

Bun.write(
  "output/index.html",
  template.replace(
    "%%%PIGEONS%%%",
    pickedImages
      .map(
        (image, index) =>
          `<a href="${image.pageURL}"><img src="downloads/${image.id}.jpg" alt="pigeon picture #${index + 1}"></a>`,
      )
      .join("\n"),
  ),
);

console.log("Done.");
