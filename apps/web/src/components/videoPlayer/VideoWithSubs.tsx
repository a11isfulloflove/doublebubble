import "./VideoWithSubs.css";
import { useEffect, useState, useRef } from "react";
import { useParams } from "react-router-dom";
import ReactPlayer from "react-player";
import { loadSingleVideo } from "@doublesub/shared";
import type { Segment, VideoDetail } from "@doublesub/shared";

export default function VideoWithSubs() {
    const { slug } = useParams();
    const [videoToShow, setVideoToShow] = useState<Pick<VideoDetail, "link" | "title" | "status"> | null>(null);
    const [segments, setSegments] = useState<Segment[]>([]);
    const [currentTime, setCurrentTime] = useState(0);
    const [currentSegment, setCurrentSegment] = useState<Segment | null>(null);
    const playerRef = useRef<HTMLVideoElement | null>(null);
    const [transcriptVisible, setTranscriptVisible] = useState(false);

    useEffect(() => {
        if (!slug) {
            return;
        }

        const fetchVideos = async () => {
            const data = await loadSingleVideo(decodeURIComponent(slug));
            if (!data) return;
            setVideoToShow(data);
            setSegments(data.segments || []);
        }
        
        fetchVideos();

    }, [slug]);

    useEffect(() => {
        if (!segments.length) return;
        const segment = segments.find(
            (s) => currentTime >= s.start && currentTime <= s.end
        );
        setCurrentSegment(segment || null);
    }, [currentTime, segments]);

    useEffect(() => {
        if (!segments.length) return;
        const current = segments.find(
            (s) => currentTime >= s.start && currentTime <= s.end
        );
        if (current) {
            const index = segments.indexOf(current);
            const lineEl = document.querySelectorAll('.transcript-line')[index] as HTMLElement;
            lineEl?.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    }, [currentTime, segments]);

    if (!slug) {
        return null;
    }

    return (
        <>
            <div className="header">
                <div className="main-text-container">
                    <a className="go-back-link" href="/">
                        {"< BACK"}
                    </a>
                    <a className="video-title">{videoToShow?.title}</a>
                </div>
            </div>

            <div className={`container ${!transcriptVisible ? "show-full-video" : ""}`}>
                <div className="card relative">
                    <ReactPlayer
                        ref={playerRef}
                        src={videoToShow?.link}
                        controls
                        width="95%"
                        height="95%"
                        // eslint-disable-next-line @typescript-eslint/no-explicit-any
                        onTimeUpdate={(ev: any) => {
                            setCurrentTime(ev.target.api.getCurrentTime());
                        }}
                    />

                    {videoToShow?.status === "processing" && (
                        <div className="subtitle-loading-overlay">
                            Subtitles are currently being generated... Please, check back later! 
                        </div>
                    )}
                    {currentSegment && (
                        <div className="subtitle-overlay">
                            <div className="subtitle-original">{currentSegment.text}</div>
                            <div className="subtitle-translation">{currentSegment.tr}</div>
                        </div>
                    )}
                </div>

                <button
                    className="toggle-btn"
                    onClick={() => setTranscriptVisible(!transcriptVisible)}
                >
                    {transcriptVisible ? "hide subtitles" : "show all subtitles"}
                </button>

                <div className={`transcript ${!transcriptVisible ? "hidden" : ""}`}>
                    {segments.map((s, i) => (
                        <div
                            key={i}
                            className={`transcript-line ${currentTime >= s.start && currentTime <= s.end ? "active" : ""
                                }`}
                            onClick={() => {
                                if (playerRef.current) {
                                    playerRef.current.currentTime = s.start;
                                }
                            }}
                        >
                            <div className="transcript-original">{s.text}</div>
                            <div className="transcript-translation">{s.tr}</div>
                        </div>
                    ))}
                </div>
            </div>
        </>
    );
}
