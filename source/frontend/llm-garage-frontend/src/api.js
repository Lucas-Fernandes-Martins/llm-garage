// src/api.js
export const API_BASE_URL = (
  process.env.REACT_APP_API_URL ||
  "https://llm-garage-api-513913820596.us-central1.run.app"
).trim();

export const WS_BASE_URL = (
  process.env.REACT_APP_WS_URL ||
  "wss://llm-garage-api-513913820596.us-central1.run.app"
).trim();

