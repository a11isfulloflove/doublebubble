export async function generateNewSubtitles(url: string) {
  const formData = new FormData();
  formData.append("link", url);

  const res = await fetch("/whisper/transcribe", {
    method: "POST",
    body: formData
  });

  const data = await res.json();

  if (!res.ok) {
    throw new Error(data.detail || `Error: ${res.status}`);
  }

  if (data.message) {
    alert(data.message);
  }

  return data;
}

export async function loadVideos() {
  const url = "/whisper/getallvideos";
  const res = await fetch(url);
  const text = await res.text();
  const data = JSON.parse(text);
  return data;
}

export async function loadSingleVideo(slug: string) {
  const formData = new FormData();
  formData.append("slugtitle", slug);

  const res = await fetch("/whisper/getbyslugtitle", {
    method: "POST",
    body: formData
  });

  if (!res.ok) throw new Error(`Error: ${res.status}`);

  const data = await res.json();
  return data;
}

export async function deleteSingleVideo(slug: string) {
  const formData = new FormData();
  formData.append("slug", slug);

  const response = await fetch(`/whisper/deletevideo/${slug}`, {
    method: "DELETE"
  });

  if (!response.ok) throw new Error(`Error: ${response.status}`);

  return await response.json();
}
