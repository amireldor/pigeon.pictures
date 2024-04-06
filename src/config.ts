export const PIXABAY_API_KEY = process.env.PIXABAY_API_KEY;

if (!PIXABAY_API_KEY) {
  console.error(
    "Please provide a Pixabay API key in the environment variable PIXABAY_API_KEY. Exiting."
  );
  process.exit(1);
}
