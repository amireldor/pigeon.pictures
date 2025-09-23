import { S3Client, PutObjectCommand } from "@aws-sdk/client-s3";

export const handler = async (event, context) => {
  const PIGEONS_PER_PAGE = 20;
  const page = Math.floor(Math.random() * 20) + 1;
  const PIXABAY_API_KEY = process.env.PIXABAY_API_KEY;
  const PIXABAY_API_URL = `https://pixabay.com/api/?key=${PIXABAY_API_KEY}&q=pigeon&image_type=photo&page=${page}&per_page=${PIGEONS_PER_PAGE}`;

  const searchResponse = await fetch(PIXABAY_API_URL);
  const searchData = await searchResponse.json();
  const images = searchData.hits;

  if (!images.length) {
    throw new Error("No pigeon images found");
  }

  const s3 = new S3Client({});
  const bucketName = process.env.BUCKET_NAME;

  const imageTasks = images.map(async (img, index) => {
    const imageResponse = await fetch(img.largeImageURL);
    const imageBuffer = await imageResponse.arrayBuffer();

    const putObjectCommand = new PutObjectCommand({
      Bucket: bucketName,
      Key: `pigeons-2025/pigeons/${index.toString().padStart(2, "0")}.jpg`,
      Body: Buffer.from(imageBuffer),
      ContentType: "image/jpeg",
    });

    await s3.send(putObjectCommand);
  });

  const settled = await Promise.allSettled(imageTasks);
  const failed = settled.filter((result) => result.status === "rejected");

  if (failed.length > 0) {
    console.error(`${failed.length} image uploads failed.`);
  }

  return {
    statusCode: 200,
    body: JSON.stringify(
      `Yay! ${settled.length - failed.length} Pigeon Pictures deployed.`
    ),
  };
};
