# 🎙️ Multi-Model AI Agent

> **Transform text into professional audio and video content using multiple AI models**

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://https://multimodelaiagent-frxx8ahgrn6ft9nd8amz4h.streamlit.app/)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A powerful web application that combines multiple AI language models (Claude, GPT-4, Gemini, Llama-2) with advanced text-to-speech and video generation services to create professional multimedia content from simple text inputs.

---

## 🌟 Features

### 🧠 **Multi-Model Text Generation**
- **Claude 3.5 Sonnet** (Anthropic) - Advanced reasoning and natural language
- **GPT-4** (OpenAI) - Industry-leading language model
- **Gemini Pro** (Google) - Multimodal AI capabilities
- **Llama-2** (Meta via HuggingFace) - Open-source alternative

### 🎵 **Professional Audio/Video Output**
- **OpenAI TTS** - High-quality text-to-speech with multiple voices
- **ElevenLabs** - Premium voice synthesis with realistic intonation
- **D-ID** - AI avatar video generation with synchronized speech

### ✨ **Smart Enhancement Modes**
- ✍️ Improve & Enhance - Polish and refine existing text
- 🎬 Video Script - Convert to professional script format
- 📖 Narration Style - Transform into storytelling narrative
- 🎙️ Podcast Intro - Create engaging podcast intros/outros
- 📚 Story Expansion - Expand ideas into full stories
- 💼 Professional Tone - Business-ready formal content
- 😊 Casual & Friendly - Conversational and approachable

### 🎨 **Beautiful Modern UI**
- Glassmorphism design with animated gradients
- Responsive layout for all devices
- Real-time status indicators
- Intuitive user experience
- Dark mode optimized

---

## 🚀 Live Demo

Try it now: **[Your App URL](https://your-app-url.streamlit.app)**

---

## 📸 Screenshots

### Main Dashboard
![Main Dashboard](screenshots/dashboard.png)

### API Configuration
![API Config](screenshots/api-config.png)

### Generated Content
![Results](screenshots/results.png)

---

## 🛠️ Installation

### Prerequisites
- Python 3.9 or higher
- pip package manager
- API keys for the services you want to use

### Local Setup

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/multi-model-ai-agent.git
cd multi-model-ai-agent
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run the application**
```bash
streamlit run app.py
```

4. **Open in browser**
```
http://localhost:8501
```

---

## 🔑 Getting API Keys

### Required (Choose at least one LLM):

#### Claude (Recommended)
1. Visit [console.anthropic.com](https://console.anthropic.com)
2. Sign up for an account
3. Navigate to API Keys section
4. Create a new API key
5. **Pricing**: Pay-as-you-go, ~$0.003 per 1K input tokens

#### OpenAI
1. Visit [platform.openai.com](https://platform.openai.com/api-keys)
2. Create account and verify
3. Generate API key
4. **Pricing**: ~$0.03 per 1K tokens (GPT-4), $15 per 1M chars (TTS)

#### Google Gemini
1. Visit [makersuite.google.com](https://makersuite.google.com/app/apikey)
2. Sign in with Google account
3. Create API key
4. **Pricing**: Free tier available, then pay-as-you-go

#### HuggingFace
1. Visit [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
2. Create account
3. Generate access token
4. **Pricing**: Free tier available for inference API

### Audio/Video (Choose one):

#### OpenAI TTS
- Same key as OpenAI GPT-4
- $15 per 1M characters

#### ElevenLabs
1. Visit [elevenlabs.io](https://elevenlabs.io)
2. Sign up for account
3. Get API key from profile
4. **Pricing**: Free 10K chars/month, Starter $5/month (30K chars)

#### D-ID
1. Visit [d-id.com](https://www.d-id.com)
2. Create account
3. Access API credentials
4. **Pricing**: Free trial, then $0.12-$0.30 per video

---

## 📋 Usage Guide

### Basic Workflow

1. **Configure API Keys**
   - Open sidebar
   - Enter your Claude API key (required)
   - Optionally add other LLM keys
   - Select TTS provider and enter its key

2. **Select Models**
   - Choose your LLM model (Claude, GPT-4, Gemini, or Llama-2)
   - Select enhancement mode
   - Pick TTS/Video provider and voice

3. **Enter Content**
   - Type or paste your text (can be a topic or full content)
   - Examples:
     - "Create a professional introduction about AI"
     - "Write a podcast intro about climate change"
     - "Make a video script explaining blockchain"

4. **Generate**
   - Click "Generate AI Content → Audio/Video"
   - AI enhances your text
   - Converts to audio or video
   - Preview and download

### Pro Tips

- **Start Simple**: Begin with Claude + OpenAI TTS for best results
- **Experiment**: Try different enhancement modes for various styles
- **Voice Selection**: Test different voices to find the best fit
- **Length**: Keep text under 4,000 characters for optimal results
- **Cost Control**: Monitor API usage in respective dashboards

---

## 💻 Tech Stack

### Frontend
- **Streamlit** - Web application framework
- **Custom CSS** - Modern glassmorphism design
- **HTML/CSS** - Enhanced UI components

### Backend
- **Python 3.9+** - Core programming language
- **Requests** - HTTP library for API calls
- **Base64** - Encoding utilities

### AI/ML Services
- **Anthropic Claude API** - Text generation
- **OpenAI API** - GPT-4 & TTS
- **Google AI API** - Gemini
- **HuggingFace API** - Llama-2
- **ElevenLabs API** - Voice synthesis
- **D-ID API** - Video generation

---

## 📁 Project Structure

```
multi-model-ai-agent/
│
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation
├── .gitignore            # Git ignore rules
│
├── screenshots/          # App screenshots
│   ├── dashboard.png
│   ├── api-config.png
│   └── results.png
│
└── .streamlit/           # Streamlit configuration (optional)
    └── config.toml
```

---

## 🔒 Security & Privacy

- ✅ **No data storage** - All processing happens in real-time
- ✅ **Secure API calls** - Direct HTTPS connections to providers
- ✅ **Browser-only keys** - API keys stored in browser session
- ✅ **No logging** - Your content is never saved or logged
- ✅ **Open source** - Fully transparent codebase

### Best Practices
- Never commit API keys to Git
- Use environment variables for production
- Rotate keys regularly
- Monitor API usage dashboards
- Set spending limits on API accounts

---

## 🚢 Deployment

### Streamlit Cloud (Recommended)

1. Push code to GitHub
2. Visit [share.streamlit.io](https://share.streamlit.io)
3. Connect your repository
4. Set main file to `app.py`
5. Deploy!

### Heroku

```bash
# Create Procfile
echo "web: streamlit run app.py --server.port=$PORT" > Procfile

# Deploy
heroku create your-app-name
git push heroku main
```

### Docker

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/AmazingFeature
   ```
3. **Commit your changes**
   ```bash
   git commit -m 'Add some AmazingFeature'
   ```
4. **Push to the branch**
   ```bash
   git push origin feature/AmazingFeature
   ```
5. **Open a Pull Request**

### Development Guidelines
- Follow PEP 8 style guide
- Add comments for complex logic
- Test with multiple API providers
- Update documentation for new features

---

## 🐛 Known Issues & Limitations

- **Rate Limits**: API providers have rate limits; add delays for bulk processing
- **Cost**: Using multiple premium APIs can accumulate costs
- **D-ID Videos**: May take 1-2 minutes to generate
- **Text Length**: Very long texts may hit token limits
- **Browser Storage**: API keys not persisted between sessions

---

## 📝 Changelog

### Version 1.0.0 (2024-11-16)
- ✨ Initial release
- 🎨 Beautiful glassmorphism UI
- 🧠 Multi-model LLM support
- 🎵 Three TTS/Video providers
- 📚 Seven enhancement modes
- 🔒 Secure API handling

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2024 Vivek YT

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 👨‍💻 Author

**Vivek YT**

- GitHub: [@yourusername](https://github.com/yourusername)
- YouTube: [Your Channel](https://youtube.com/@yourchannel)
- Twitter: [@yourhandle](https://twitter.com/yourhandle)
- Email: your.email@example.com

---

## 🙏 Acknowledgments

- **Anthropic** for Claude AI
- **OpenAI** for GPT-4 and TTS
- **Google** for Gemini
- **Meta AI** for Llama-2
- **ElevenLabs** for voice synthesis
- **D-ID** for video generation
- **Streamlit** for the amazing framework
- All contributors and users

---

## 💖 Support

If you find this project helpful, please consider:

- ⭐ Starring the repository
- 🐛 Reporting bugs
- 💡 Suggesting new features
- 📢 Sharing with others
- ☕ [Buy me a coffee](https://buymeacoffee.com/yourusername)

---

## 📞 Support & Contact

- **Issues**: [GitHub Issues](https://github.com/yourusername/multi-model-ai-agent/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/multi-model-ai-agent/discussions)
- **Email**: support@yourdomain.com

---

## 🗺️ Roadmap

### Upcoming Features
- [ ] Batch processing for multiple texts
- [ ] Custom voice cloning integration
- [ ] More LLM models (Cohere, AI21, etc.)
- [ ] Audio editing capabilities
- [ ] Video template selection
- [ ] Multi-language support
- [ ] API key encryption
- [ ] Usage analytics dashboard
- [ ] Export to multiple formats
- [ ] Webhook integrations

---

<div align="center">

### ⭐ Star this repo if you find it useful!

Made with ❤️ by **Vivek YT**

[![GitHub stars](https://img.shields.io/github/stars/yourusername/multi-model-ai-agent?style=social)](https://github.com/yourusername/multi-model-ai-agent/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/yourusername/multi-model-ai-agent?style=social)](https://github.com/yourusername/multi-model-ai-agent/network/members)

</div>
