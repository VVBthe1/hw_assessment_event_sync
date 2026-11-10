// App settings. Override API URL with VITE_API_BASE in a .env file.
export const API_BASE =
  import.meta.env.VITE_API_BASE || "http://localhost:8000/api";
