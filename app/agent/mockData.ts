import { BrowserRouter, Route, Routes } from "react-router-dom";
import Home from "./pages/Home";
import Course from "./pages/Course";
import Bookshelf from "./pages/Bookshelf";
import HonorRoll from "./pages/HonorRoll";
import Contribute from "./pages/Contribute";
import Resource from "./pages/Resource";
import Terms from "./pages/Terms";
import Releases from "./pages/Releases";

function ScrollToTop() {
  return null;
}

export default function App() {
  return (
    <BrowserRouter>
      <ScrollToTop />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/course/:id" element={<Course />} />
        <Route path="/bookshelf" element={<Bookshelf />} />
        <Route path="/honor-roll" element={<HonorRoll />} />
        <Route path="/contribute" element={<Contribute />} />
        <Route path="/resource/:id" element={<Resource />} />
        <Route path="/terms" element={<Terms />} />
        <Route path="/releases" element={<Releases />} />
      </Routes>
    </BrowserRouter>
  );
}
