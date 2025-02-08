import {
  S3Client,
  ListObjectsV2Command,
  DeleteObjectCommand,
} from "@aws-sdk/client-s3";

const s3 = new S3Client({ region: process.env.AWS_REGION });
const BUCKET_NAME = process.env.BUCKET_NAME;
const FOLDER_PREFIX = "pigeons/";
const SIX_HOURS_IN_MS = 6 * 60 * 60 * 1000;

export const handler = async (event) => {
  try {
    // List all objects in the "pigeons/" folder
    const listCommand = new ListObjectsV2Command({
      Bucket: BUCKET_NAME,
      Prefix: FOLDER_PREFIX, // Filter for only files in "pigeons/"
    });

    const listResponse = await s3.send(listCommand);
    if (!listResponse.Contents || listResponse.Contents.length === 0) {
      return {
        statusCode: 200,
        body: JSON.stringify({ message: "No files to delete" }),
      };
    }

    const now = Date.now();
    const oldFiles = listResponse.Contents.filter((file) => {
      const lastModified = new Date(file.LastModified).getTime();
      return now - lastModified > SIX_HOURS_IN_MS;
    });

    if (oldFiles.length === 0) {
      return {
        statusCode: 200,
        body: JSON.stringify({ message: "No old files to delete" }),
      };
    }

    // Delete all old files in parallel
    const deletePromises = oldFiles.map((file) => {
      const deleteCommand = new DeleteObjectCommand({
        Bucket: BUCKET_NAME,
        Key: file.Key,
      });

      return s3.send(deleteCommand);
    });

    await Promise.all(deletePromises);

    return {
      statusCode: 200,
      body: JSON.stringify({
        message: `${oldFiles.length} files deleted successfully`,
      }),
    };
  } catch (error) {
    console.error("Error deleting old files:", error);
    return {
      statusCode: 500,
      body: JSON.stringify({ error: error.message }),
    };
  }
};
