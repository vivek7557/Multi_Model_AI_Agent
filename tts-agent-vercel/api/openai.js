export const config = { runtime: 'edge' };

export default async function handler(req) {
  if (req.method !== 'POST') return new Response('Method Not Allowed', { status: 405 });
  try {
    const { text, voice } = await req.json();
    const OPENAI_API_KEY = process.env.OPENAI_API_KEY;
    if (!OPENAI_API_KEY) return new Response('OpenAI API key not configured', { status: 500 });

    const providerResp = await fetch('https://api.openai.com/v1/audio/speech', {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${OPENAI_API_KEY}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ model: 'gpt-4o-mini-tts', input: text, voice })
    });

    if (!providerResp.ok) {
      const txt = await providerResp.text();
      return new Response(txt || 'OpenAI error', { status: providerResp.status });
    }
    const ct = providerResp.headers.get('content-type') || 'audio/mpeg';
    return new Response(providerResp.body, { status: 200, headers: { 'Content-Type': ct } });
  } catch (err) {
    return new Response(err.message || 'OpenAI proxy error', { status: 500 });
  }
}
