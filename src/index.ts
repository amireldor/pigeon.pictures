import { PixabayPictureFetcher } from "./services/pixabay";
import { addHour } from "@formkit/tempo";

const fetcher = new PixabayPictureFetcher();

const images = await fetcher.fetchImages();

console.log(`Downloading ${images.length} images...`);
const downloadPromises = images.map(async (image) =>
  Bun.write(
    `output/downloads/${image.id.toString()}.jpg`,
    await fetch(image.imageURL)
  )
);

await Promise.all(downloadPromises);
console.log("Writing HTML...");

const template = await Bun.file("src/template.html").text();
const now = new Date();
let nextUpdateDate = new Date();
const minutes = now.getMinutes();
if (minutes < 30) {
  nextUpdateDate.setMinutes(30);
} else {
  nextUpdateDate.setMinutes(0);
  nextUpdateDate = addHour(nextUpdateDate, 1);
}
nextUpdateDate.setSeconds(0);
nextUpdateDate.setMilliseconds(0);

console.log(now, nextUpdateDate);

Bun.write(
  "output/index.html",
  template
    .replace(
      "%%%PIGEONS%%%",
      images
        .map(
          (image, index) =>
            `<a href="${image.pageURL}"><img src="downloads/${image.id}.jpg" alt="pigeon picture #${index + 1}"></a>`
        )
        .join("\n")
    )
    .replace("%%%NEW_PIGEONS_TIME%%%", nextUpdateDate.toISOString())
);

console.log("Done.");
