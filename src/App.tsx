import Layout from './layouts/layout'
import ListOfVideos from './components/home/listOfVideos';
import VideoWithSubs from './components/videoPlayer/videoWithSubs';
import NoPage from './components/errorPage/nopage'

import ReactDOM from "react-dom/client";
import { BrowserRouter, Routes, Route } from "react-router-dom";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path='/' element={<Layout />} />
        <Route index element={<ListOfVideos />} />
        <Route path='play' element={<VideoWithSubs />} />
        <Route path="video/:slug" element={<VideoWithSubs />} />
        <Route path='*' element={<NoPage />} />
      </Routes>
    </BrowserRouter>
  )
}

const root = ReactDOM.createRoot(document.getElementById('root')!);
root.render(<App />);
