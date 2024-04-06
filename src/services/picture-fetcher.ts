export type PigeonPicture = {
  id: string;
  pageURL: string;
  imageURL: string;
};

export abstract class PictureFetcher {
  abstract fetchImages(): Promise<PigeonPicture[]>;
}
