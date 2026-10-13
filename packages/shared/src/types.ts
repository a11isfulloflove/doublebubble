export type VideoStatus = "queued" | "processing" | "done" | "error";

export interface Segment {
  start: number;
  end: number;
  text: string;
  tr: string;
}

export interface VideoListItem {
  link: string;
  title: string;
  slug: string;
  thumbnail_base64: string;
  status: VideoStatus;
}

export interface VideoDetail extends VideoListItem {
  segments?: Segment[];
  language?: string;
  full_text?: string;
  error?: string;
}

export interface TranscribeResponse {
  status: VideoStatus;
  message?: string;
}

export interface DeleteResponse {
  status: string;
  message: string;
}
