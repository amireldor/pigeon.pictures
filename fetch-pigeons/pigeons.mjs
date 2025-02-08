import { S3Client, PutObjectCommand } from "@aws-sdk/client-s3";
import axios from "axios";

const s3 = new S3Client({ region: process.env.AWS_REGION });
const BUCKET_NAME = process.env.BUCKET_NAME;
const PIXABAY_API_KEY = process.env.PIXABAY_API_KEY;
const PIXABAY_API_URL = `https://pixabay.com/api/?key=${PIXABAY_API_KEY}&q=pigeon&image_type=photo&per_page=20`;

export const handler = async (event) => {
  try {
    const response = await axios.get(PIXABAY_API_URL);
    const images = response.data.hits;

    if (!images.length) {
      throw new Error("No images found");
    }

    // Fetch all images in parallel
    const imagePromises = images.map(async (image) => {
      const imageResponse = await axios.get(image.largeImageURL, {
        responseType: "arraybuffer",
      });
      const imageBuffer = Buffer.from(imageResponse.data, "binary");
      const fileName = `pigeons/pigeon-${Date.now()}-${Math.floor(
        Math.random() * 1000
      )}.jpg`; // Adding "pigeons/" prefix

      const putCommand = new PutObjectCommand({
        Bucket: BUCKET_NAME,
        Key: fileName,
        Body: imageBuffer,
        ContentType: "image/jpeg",
      });

      return s3.send(putCommand);
    });

    // Wait for all uploads to complete
    await Promise.all(imagePromises);

    return {
      statusCode: 200,
      body: JSON.stringify({
        message: "Images saved successfully in 'pigeons/' folder",
      }),
    };
  } catch (error) {
    console.error(error);
    return {
      statusCode: 500,
      body: JSON.stringify({ error: error.message }),
    };
  }
};
