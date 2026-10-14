import type {
  DeleteResponse,
  TranscribeResponse,
  VideoDetail,
  VideoListItem,
} from "./types";

export async function generateNewSubtitles(
  url: string,
): Promise<TranscribeResponse> {
  const formData = new FormData();
  formData.append("link", url);

  const res = await fetch("/whisper/transcribe", {
    method: "POST",
    body: formData,
  });

  const data: TranscribeResponse = await res.json();

  if (!res.ok) {
    throw new Error((data as { detail?: string }).detail || `Error: ${res.status}`);
  }

  return data;
}

export async function loadVideos(): Promise<VideoListItem[]> {
  const url = "/whisper/getallvideos";
  const res = await fetch(url);
  const text = await res.text();
  const data: VideoListItem[] = JSON.parse(text);
  return data;
}

export async function loadSingleVideo(slug: string): Promise<VideoDetail | null> {
  const formData = new FormData();
  formData.append("slugtitle", slug);

  const res = await fetch("/whisper/getbyslugtitle", {
    method: "POST",
    body: formData,
  });

  if (!res.ok) throw new Error(`Error: ${res.status}`);

  const data: VideoDetail | null = await res.json();
  return data;
}

export async function deleteSingleVideo(slug: string): Promise<DeleteResponse> {
  const response = await fetch(`/whisper/deletevideo/${slug}`, {
    method: "DELETE",
  });

  if (!response.ok) throw new Error(`Error: ${response.status}`);

  return await response.json();
}
