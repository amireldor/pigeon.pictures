import { S3Client, PutObjectCommand } from "@aws-sdk/client-s3";

export const handler = async (event, context) => {
  const s3 = new S3Client({});

  const bucketName = process.env.BUCKET_NAME;
  const objectKey = "test-object.txt";
  const objectContent = "This is a test object created by the Lambda function.";

  const putObjectCommand = new PutObjectCommand({
    Bucket: bucketName,
    Key: objectKey,
    Body: objectContent,
  });

  await s3.send(putObjectCommand);

  console.log(
    `Successfully created object ${objectKey} in bucket ${bucketName}`
  );

  return {
    statusCode: 200,
    body: JSON.stringify("Hello from pigeon.picture's AWS Lambda!"),
  };
};
