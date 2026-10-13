import { useEffect, useState } from 'react'
import "./ListOfVideos.css"
import { generateNewSubtitles, loadVideos, deleteSingleVideo } from "@doublesub/shared";
import type { VideoListItem } from "@doublesub/shared";
import { loadingImage } from "../../assets/loadingImage";
import { normalizeUrl, isValidUrl, ytLinkChecker } from '../../features/linkChecker';

export default function ListOfVideos() {
    const [listOfVideos, setListOfVideos] = useState<VideoListItem[]>([])
    const [urlSentByUser, setUrlSentByUser] = useState("");
    const [error, setError] = useState<string | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchVideos = async () => {
            try {
                setLoading(true);
                const data = await loadVideos();
                setListOfVideos(data);
                // eslint-disable-next-line @typescript-eslint/no-unused-vars
            } catch (err) {
                setError("Failed to load. The server currently might not be available.");
            } finally {
                setLoading(false);
            }
        };

        fetchVideos();
    }, []);

    function addNewVideo(urlToAdd: string) {
        const newInfo: VideoListItem = {
            slug: "",
            title: "VIDEO IS LOADING...",
            link: urlToAdd,
            thumbnail_base64: loadingImage(),
            status: "queued"
        }
        setListOfVideos([...listOfVideos, newInfo]);
    }

    async function handleUrlSubmit() {
        const url = urlSentByUser;
        setUrlSentByUser("");
        if (!isValidUrl(url)) {
            alert("Link is not valid... Honestly i dont think this was a link at all...");
            return;
        }
        if (!ytLinkChecker(url)) {
            alert("We can process only yt videos atm!!! Please paste a valid yt link instead.");
            return;
        }
        if (listOfVideos.some(v => normalizeUrl(v.link) === normalizeUrl(url))) {
            alert("This video already exists. Please!! check the feed");
            return;
        }
        addNewVideo(url);
        try {
            const data = await generateNewSubtitles(url);
            if (data.message) {
                alert(data.message);
            }

        } catch (err) {
            setListOfVideos((prevList) =>
                prevList.filter(video => video.link !== url)
            );

            if (err instanceof Error) {
                alert(err.message);
            } else {
                alert("Something went wrong...");
            }
        }
    }

    const [videoToDelete, setVideoToDelete] = useState<VideoListItem | null>(null);
    async function deleteVideo(slug: string) {
        await deleteSingleVideo(slug)
        setListOfVideos((prevList) => prevList.filter(video => video.slug !== slug));
        setVideoToDelete((prev) => (prev && prev.slug === slug ? null : prev));
    }

    if (loading) {
        return (
            <div>
                <div className="header">
                    <div className="main-text-container">
                        <a className="header-main-text" href="/">{"🫧double더블🫧버블bubble🫧"}</a>
                    </div>
                </div>
                <div className="text-gray-500">Loading...</div>;
            </div>
        );
    }

    if (error) {
        return (
            <div>
                <div className="header">
                    <div className="main-text-container">
                        <a className="header-main-text" href="/">{"🫧double더블🫧버블bubble🫧"}</a>
                    </div>
                </div>
                <div className="error-showing">
                    {error}
                </div>
            </div>
        );
    }

    return (
        <div className="list-of-videos">
            <div className="header">
                <div className="main-text-container">
                    <a className="header-main-text" href="/">{"🫧double더블🫧버블bubble🫧"}</a>
                </div>
                <div className="url-input-button">
                    <input
                        className="url-input-field"
                        type="text"
                        placeholder="paste url here"
                        value={urlSentByUser}
                        onChange={
                            (e) => { setUrlSentByUser(e.target.value); }
                        }
                    />
                    <button className="submit-url-button" type="button" onClick={handleUrlSubmit}>add</button>
                </div>
            </div>

            <div className="video-grid">
                {listOfVideos.map((video) => (

                    <div key={video.slug} className="video-card">
                        <a
                            href={`/video/${encodeURIComponent(video.slug)}`}
                            data-status={video.status}
                            className="video-link"
                            onClick={(e) => {
                                if (video.status !== "done") e.preventDefault();
                            }}
                        >
                            <div className="thumbnail-wrapper">
                                <img
                                    src={`data:image/jpeg;base64,${video.thumbnail_base64}`}
                                    alt={video.title}
                                    className="thumbnail"
                                />
                            </div>
                            <h3 className="video-title">{video.title}</h3>
                        </a>

                        {video.status === "done" && (
                            <button
                                className="delete-btn"
                                onClick={(e) => {
                                    e.preventDefault();
                                    setVideoToDelete(video);

                                }}
                                title="Delete video"
                            >
                                ✕
                            </button>
                        )}
                    </div>
                ))}

                {videoToDelete && (
                    <div className="delete-confirmation-overlay">
                        <div className="delete-confirmation-container">
                            <h2 className="delete-confirmation-header">Delete this video?</h2>
                            <img
                                src={`data:image/jpeg;base64,${videoToDelete.thumbnail_base64}`}
                                alt={videoToDelete.title}
                                className="delete-confirmation-thumbnail"
                            />
                            <p className="delete-confirmation-title">«{videoToDelete.title}» will be deleted.</p>
                            <div className="delete-confirmation-buttons">
                                <button onClick={() => setVideoToDelete(null)}>Cancel</button>
                                <button
                                    className="confirm"
                                    onClick={async () => {
                                        deleteVideo(videoToDelete.slug);
                                        setVideoToDelete(null);
                                    }}
                                >
                                    Delete
                                </button>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    )
}
