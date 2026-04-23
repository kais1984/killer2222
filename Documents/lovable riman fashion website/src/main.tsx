import { createRoot } from "react-dom/client";
import App from "./App.tsx";
import "./index.css";

const root = document.getElementById("root")!;

root.innerHTML = '<div style="min-height:100vh;display:flex;align-items:center;justify-content:center;font-family:serif;color:#8b7355;font-size:18px;">Loading Riman Fashion...</div>';

try {
  createRoot(root).render(<App />);
} catch (e) {
  root.innerHTML = '<div style="min-height:100vh;display:flex;align-items:center;justify-content:center;font-family:serif;color:#8b7355;font-size:18px;padding:20px;text-align:center;">Unable to load. Please refresh or check console for errors.</div>';
  console.error(e);
}
