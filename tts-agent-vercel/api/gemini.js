export const config = { runtime: 'edge' };

export default async function handler(req) {
  if (req.method !== 'POST') return new Response('Method Not Allowed', { status: 405 });
  try {
    const { text, voice } = await req.json();
    const GEMINI_API_KEY = process.env.GEMINI_API_KEY;
    if (!GEMINI_API_KEY) return new Response('Gemini API key not configured', { status: 500 });

    const providerResp = await fetch(`https://generativelanguage.googleapis.com/v1/audio/speech?key=${GEMINI_API_KEY}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ input: { text }, voice: { name: voice }, audioConfig: { audioEncoding: 'MP3' } })
    });

    if (!providerResp.ok) {
      const txt = await providerResp.text();
      return new Response(txt || 'Gemini error', { status: providerResp.status });
    }
    const ct = providerResp.headers.get('content-type') || 'audio/mpeg';
    return new Response(providerResp.body, { status: 200, headers: { 'Content-Type': ct } });
  } catch (err) {
    return new Response(err.message || 'Gemini proxy error', { status: 500 });
  }
}
