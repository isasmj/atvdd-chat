import streamlit as st
import re
import os
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs
import requests  # Fallback alternativo
import gemini_utils
import youtube_utils
import sys
from datetime import datetime  # Importação adicionada para corrigir o erro

import streamlit as st
import re
import requests
from youtube_transcript_api import YouTubeTranscriptApi
from datetime import datetime

# ======================================
# CONFIGURAÇÃO INICIAL
# ======================================
st.set_page_config(
    page_title="Transcritor YouTube - Isa 🎥",
    page_icon="🎬",
    layout="wide"
)

# Variáveis de sessão
if 'transcription_count' not in st.session_state:
    st.session_state.transcription_count = 0
if 'last_transcription' not in st.session_state:
    st.session_state.last_transcription = None
if 'history' not in st.session_state:
    st.session_state.history = []
if 'language' not in st.session_state:
    st.session_state.language = "Português"

# ======================================
# FUNÇÕES
# ======================================
def extract_video_id(url):
    patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11})',
        r'youtu.be\/([0-9A-Za-z_-]{11})',
        r'embed\/([0-9A-Za-z_-]{11})',
        r'shorts\/([0-9A-Za-z_-]{11})'
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def get_transcript(video_id, languages=None):
    try:
        if languages:
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=languages)
        else:
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return ' '.join([entry['text'] for entry in transcript])
    except Exception as e:
        st.error(f"Erro ao obter transcrição: {str(e)}")
        return None

# ======================================
# INTERFACE PRINCIPAL
# ======================================
st.title("🎬 Transcritor de Vídeos da Isa")

# Barra lateral
with st.sidebar:
    st.header("⚙️ Configurações")
    st.session_state.language = st.selectbox(
        "Idioma da Transcrição",
        ["Português", "Qualquer idioma"],
        index=0 if st.session_state.language == "Português" else 1
    )
    
    st.header("📅 Histórico")
    if st.session_state.history:
        for i, item in enumerate(reversed(st.session_state.history[-3:]), 1):
            st.markdown(f"{i}. **{item['title'][:25]}**\n`{item['date']}`")
    else:
        st.caption("Nenhuma transcrição realizada")

# Formulário principal
url = st.text_input(
    "Cole a URL do vídeo do YouTube:",
    placeholder="https://www.youtube.com/watch?v=..."
)

if st.button("🔍 Transcrever Vídeo"):
    if not url:
        st.error("Por favor, insira uma URL válida do YouTube")
    else:
        video_id = extract_video_id(url)
        
        if not video_id:
            st.error("URL inválida. Formatos aceitos:\n- https://www.youtube.com/watch?v=ID\n- https://youtu.be/ID")
        else:
            with st.spinner("🔍 Procurando informações do vídeo..."):
                try:
                    response = requests.get(
                        f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json",
                        timeout=10
                    )
                    video_title = response.json().get('title', 'Título desconhecido') if response.status_code == 200 else 'Título desconhecido'
                    
                    with st.spinner("📝 Processando transcrição..."):
                        languages = ['pt', 'pt-BR', 'pt-PT'] if st.session_state.language == "Português" else None
                        transcript = get_transcript(video_id, languages)
                        
                        if transcript:
                            st.session_state.history.append({
                                'date': datetime.now().strftime("%d/%m %H:%M"),
                                'title': video_title,
                                'video_id': video_id
                            })
                            st.session_state.transcription_count += 1
                            st.session_state.last_transcription = video_title
                            
                            st.success(f"✅ Transcrição concluída para: {video_title}")
                            st.text_area("Texto transcrito:", value=transcript, height=300)
                            
                            st.download_button(
                                "⬇️ Baixar Transcrição",
                                transcript,
                                file_name=f"transcricao_{video_id}.txt",
                                mime="text/plain"
                            )
                        else:
                            st.error("Não foi possível obter a transcrição")
                except Exception as e:
                    st.error(f"Erro: {str(e)}")

# Rodapé
st.markdown("""
    <div style="margin-top: 3rem; text-align: center; color: #666;">
        Desenvolvido com ❤️ por Isa | © 2025
    </div>
""", unsafe_allow_html=True)