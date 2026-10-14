export function ytLinkChecker(url: string): boolean {
    try {
    const parsed = new URL(url);
    console.log("parsed:", parsed)
    const hostname = parsed.hostname.replace("www.", ""); // убираем www
    console.log("hostname: ", hostname)
    return hostname === "youtube.com";
  } catch {
    return false;
  }
}

export function normalizeUrl (url: string){
    return url.trim().replace(/\/+$/, "")
}

export function isValidUrl(url: string): boolean {
  try {
    new URL(url);
    console.log("ссылка", url)
    return true;
  } catch {
    console.log("не ссылка", url)
    return false;
  }
}