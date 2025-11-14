export const config = { runtime: 'edge' };

export default async function handler(req) {
  if (req.method !== 'POST') return new Response('Method Not Allowed', { status: 405 });
  try {
    const { text, voice } = await req.json();
    const DID_API_KEY = process.env.DID_API_KEY;
    if (!DID_API_KEY) return new Response('D-ID API key not configured', { status: 500 });

    const providerResp = await fetch('https://api.d-id.com/talks', {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${DID_API_KEY}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        script: { type: 'text', input: text, provider: { type: 'microsoft', voice_id: voice } },
        source_url: 'https://create-images-results.d-id.com/default-presenter.jpg'
      })
    });

    if (!providerResp.ok) {
      const txt = await providerResp.text();
      return new Response(txt || 'D-ID error', { status: providerResp.status });
    }
    const json = await providerResp.json();
    return new Response(JSON.stringify(json), { status: 200, headers: { 'Content-Type': 'application/json' } });
  } catch (err) {
    return new Response(err.message || 'D-ID proxy error', { status: 500 });
  }
}
