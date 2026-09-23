import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "@nexova/design-system/theme.css";
import "./styles.css";
import { App } from "./App";
document.documentElement.classList.add("js");
const root=document.getElementById("root"); if(!root) throw new Error("Website root element was not found.");
createRoot(root).render(<StrictMode><App/></StrictMode>);
