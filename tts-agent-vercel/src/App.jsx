import React, { useState } from 'react';
import { Mic, Video, Download, Loader2, AlertCircle, CheckCircle2, Settings, Volume2 } from 'lucide-react';

export default function App() {
  const [text, setText] = useState('Welcome to multi-model TTS demo.');
  const [selectedModel, setSelectedModel] = useState('openai');
  const [voice, setVoice] = useState('alloy');
  const [isProcessing, setIsProcessing] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [apiKey, setApiKey] = useState('');
  const models = {
    openai: { name: 'OpenAI', voices: ['alloy','echo'] , supportsVideo:false},
    claude: { name: 'Claude', voices: ['female_1','male_1'], supportsVideo:false},
    gemini: { name: 'Gemini', voices: ['gemini_voice_1'], supportsVideo:false},
    elevenlabs: { name: 'ElevenLabs', voices: ['Rachel','Drew'], supportsVideo:false},
    did: { name: 'D-ID', voices: ['en-US-JennyNeural'], supportsVideo:true}
  };

  const generate = async () => {
    if(!text.trim()){ setError('Enter text'); return; }
    setError(''); setResult(null);
    if(!apiKey){
      // demo
      setIsProcessing(true);
      await new Promise(r=>setTimeout(r,700));
      setResult({type:'audio', url:'data:audio/mp3;base64,//uQZAAAA', blob:null, message:'Demo mode'});
      setIsProcessing(false);
      return;
    }
    setIsProcessing(true);
    try{
      const resp = await fetch(`/api/${selectedModel}`, {
        method:'POST',
        headers: {'Content-Type':'application/json', 'x-client-key': apiKey},
        body: JSON.stringify({ text, voice })
      });
      if(!resp.ok){
        const t = await resp.text();
        throw new Error(t || 'API error');
      }
      const ct = resp.headers.get('content-type') || '';
      if(ct.includes('application/json')){
        const j = await resp.json();
        setResult({type:'video', url: j.result_url || j.video_url || '', meta: j});
      } else {
        const blob = await resp.blob();
        setResult({type:'audio', url: URL.createObjectURL(blob), blob});
      }
    }catch(e){
      setError(e.message || 'Failed');
    }finally{ setIsProcessing(false); }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900 p-6 text-white">
      <div className="max-w-3xl mx-auto">
        <div className="text-center mb-6">
          <div className="flex items-center justify-center gap-3 mb-4">
            <Volume2 className="w-10 h-10 text-purple-300" />
            <h1 className="text-3xl font-bold">Multi-Model TTS Agent</h1>
          </div>
          <p className="text-purple-200">Preview (demo mode available)</p>
        </div>

        <div className="bg-white/5 p-6 rounded-xl">
          <div className="mb-4">
            <label className="block mb-2">API Key (optional demo)</label>
            <input type="password" value={apiKey} onChange={e=>setApiKey(e.target.value)} className="w-full p-2 rounded bg-white/10" placeholder="Enter API key to enable real calls"/>
          </div>

          <div className="mb-4">
            <label className="block mb-2">Model</label>
            <select value={selectedModel} onChange={e=>setSelectedModel(e.target.value)} className="w-full p-2 rounded bg-white/10">
              {Object.entries(models).map(([k,m])=> <option key={k} value={k}>{m.name}</option>)}
            </select>
          </div>

          <div className="mb-4">
            <label className="block mb-2">Voice</label>
            <select value={voice} onChange={e=>setVoice(e.target.value)} className="w-full p-2 rounded bg-white/10">
              {models[selectedModel].voices.map(v=> <option key={v} value={v}>{v}</option>)}
            </select>
          </div>

          <div className="mb-4">
            <label className="block mb-2">Text</label>
            <textarea value={text} onChange={e=>setText(e.target.value)} rows={6} className="w-full p-3 rounded bg-white/10"></textarea>
          </div>

          {error && <div className="p-3 bg-red-500/30 rounded mb-4">{error}</div>}

          <button onClick={generate} disabled={isProcessing} className="w-full p-3 bg-purple-600 rounded">
            {isProcessing ? 'Processing...' : 'Generate'}
          </button>

          {result && (
            <div className="mt-4 p-4 bg-black/20 rounded">
              {result.message && <div className="mb-2 text-purple-200">{result.message}</div>}
              {result.type==='audio' && result.url && (
                <div>
                  <audio controls src={result.url} className="w-full" />
                  <div className="mt-2">
                    <a href={result.url} download className="px-3 py-2 bg-white/10 rounded inline-block">Download</a>
                  </div>
                </div>
              )}
              {result.type==='video' && result.url && (
                <div>
                  <video controls src={result.url} className="w-full" />
                </div>
              )}
            </div>
          )}
        </div>

        <div className="mt-4 text-sm text-purple-200">
          <p>To deploy: set environment variables on Vercel for your provider keys and push this repo.</p>
        </div>
      </div>
    </div>
  );
}
