// remplacer toute référence à "/api/..." par l’URL complète
const BASE = "http://localhost:8000";

export async function startRecording() {
  const res = await fetch(`${BASE}/start-recording`, { method: "POST" });
  if (!res.ok) throw new Error(`startRecording failed: ${res.status}`);
  const data = await res.json();    // { id: "…" }
  return data.id;                   // <-- on ne renvoie QUE data.id
}

export async function stopRecording(id) {
  const res = await fetch(
    `${BASE}/stop-recording?id=${encodeURIComponent(id)}`,
    { method: "POST" }
  );
  if (!res.ok) throw new Error(`stopRecording failed: ${res.status}`);
}

export async function fetchRecordings() {
  const res = await fetch(`${BASE}/recordings`);
  if (!res.ok) throw new Error(`fetchRecordings failed: ${res.status}`);
  return res.json();
}

        
// pour l’upload avec progression
export function uploadAudio(file, onProgress) {
  const form = new FormData()
  form.append("file", file)
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest()
    xhr.open("POST", `${BASE}/upload`)
    xhr.upload.onprogress = e => onProgress(Math.round(e.loaded * 100 / e.total))
    xhr.onload  = () => xhr.status === 200 ? resolve(JSON.parse(xhr.responseText).id) : reject(xhr)
    xhr.onerror = () => reject(new Error("Erreur réseau"))
    xhr.send(form)
  })
}
