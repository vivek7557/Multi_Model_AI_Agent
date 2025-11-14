export const config = { runtime: 'edge' };

export default async function handler(req) {
  if (req.method !== 'POST') return new Response('Method Not Allowed', { status: 405 });
  try {
    const { text, voice } = await req.json();
    const ELEVEN_API_KEY = process.env.ELEVENLABS_API_KEY;
    if (!ELEVEN_API_KEY) return new Response('ElevenLabs API key not configured', { status: 500 });

    const voiceId = voice;
    const providerResp = await fetch(`https://api.elevenlabs.io/v1/text-to-speech/${voiceId}`, {
      method: 'POST',
      headers: {
        'xi-api-key': ELEVEN_API_KEY,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ text, model_id: 'eleven_monolingual_v1' })
    });

    if (!providerResp.ok) {
      const txt = await providerResp.text();
      return new Response(txt || 'ElevenLabs error', { status: providerResp.status });
    }
    const ct = providerResp.headers.get('content-type') || 'audio/mpeg';
    return new Response(providerResp.body, { status: 200, headers: { 'Content-Type': ct } });
  } catch (err) {
    return new Response(err.message || 'ElevenLabs proxy error', { status: 500 });
  }
}
