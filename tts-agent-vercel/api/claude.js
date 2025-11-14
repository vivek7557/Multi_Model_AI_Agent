export const config = { runtime: 'edge' };

export default async function handler(req) {
  if (req.method !== 'POST') return new Response('Method Not Allowed', { status: 405 });
  try {
    const { text, voice } = await req.json();
    const CLAUDE_API_KEY = process.env.CLAUDE_API_KEY;
    if (!CLAUDE_API_KEY) return new Response('Claude API key not configured', { status: 500 });

    const providerResp = await fetch('https://api.anthropic.com/v1/audio/speech', {
      method: 'POST',
      headers: {
        'x-api-key': CLAUDE_API_KEY,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ text, voice })
    });

    if (!providerResp.ok) {
      const txt = await providerResp.text();
      return new Response(txt || 'Claude error', { status: providerResp.status });
    }
    const ct = providerResp.headers.get('content-type') || 'audio/mpeg';
    return new Response(providerResp.body, { status: 200, headers: { 'Content-Type': ct } });
  } catch (err) {
    return new Response(err.message || 'Claude proxy error', { status: 500 });
  }
}
