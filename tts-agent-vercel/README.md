# Multi-Model TTS Agent (React + Vercel Edge Functions)

This project contains:
- React frontend (Vite)
- Vercel Edge functions in /api for proxying TTS/video requests:
  - /api/openai
  - /api/claude
  - /api/gemini
  - /api/elevenlabs
  - /api/did

## Quick start (local)
1. Install dependencies:
   npm install

2. Run dev server:
   npm run dev

> Note: Edge functions require deployment on Vercel to call provider APIs. Locally they may not run as edge runtime.

## Deploy to Vercel
1. Push this repository to GitHub.
2. Import the repo on vercel.com.
3. In Project Settings > Environment Variables set:
   - OPENAI_API_KEY
   - CLAUDE_API_KEY
   - GEMINI_API_KEY
   - ELEVENLABS_API_KEY
   - DID_API_KEY
4. Deploy. The frontend will call `/api/<provider>` endpoints without CORS issues.

## Demo mode
Leave the API key field empty in the UI to use demo mode (no network calls).

