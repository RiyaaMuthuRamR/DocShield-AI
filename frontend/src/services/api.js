const API_BASE = (import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api').replace(/\/$/, '');

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, options);
  const contentType = response.headers.get('content-type') || '';
  const body = contentType.includes('application/json') ? await response.json() : await response.text();
  if (!response.ok) {
    const message = typeof body === 'object' ? body.detail || JSON.stringify(body) : body;
    throw new Error(message || `Request failed (${response.status})`);
  }
  return body;
}

export function analyzeDocument(file) {
  const form = new FormData();
  form.append('file', file);
  return request('/analyze', { method: 'POST', body: form });
}

export function generateReport(payload) {
  return request('/report', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
}

export function compareIdentity(payload) {
  return request('/identity-check', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
}

export function reportDownloadUrl(relativeUrl) {
  const origin = API_BASE.replace(/\/api$/, '');
  return `${origin}${relativeUrl}`;
}
