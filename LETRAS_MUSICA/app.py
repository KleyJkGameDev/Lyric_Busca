import requests
import streamlit as st
from bs4 import BeautifulSoup

GENIUS_API_KEY = "UhkP0F3njuzvQjR2BSp8GWojhHocLmL1mKpe69k-OyPyBRYaO5rnoeIxc0XzbvvB"

st.image("LETRAS_MUSICA/Wallpaper-anime-girl-BW.png", width=800)
st.title("Fácil Music :blue[_Lyrics_]")

def buscar_info_musica(musica):
    """Busca a URL da música no Genius usando a API, sem priorizar o artista"""
    headers = {"Authorization": f"Bearer {GENIUS_API_KEY}"}
    search_url = "https://api.genius.com/search"
    params = {"q": musica}

    response = requests.get(search_url, headers=headers, params=params)
    
    if response.status_code != 200:
        st.error("Erro ao acessar a API do Genius.")
        return None, None

    data = response.json()
    hits = data["response"]["hits"]

    if not hits:
        st.error("Nenhum resultado encontrado no Genius para a música.")
        return None, None

    # Pega o primeiro resultado (o mais relevante)
    song_data = hits[0]["result"]
    song_url = song_data["url"]  # URL da página da música no Genius
    artist_name = song_data["primary_artist"]["name"]  # Nome oficial do artista
    
    return song_url, artist_name

def buscar_letra(url):
    """Faz scraping para pegar a letra da música na página do Genius"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        st.error("Erro ao acessar a página do Genius.")
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    
    # 🔍 Pegamos a letra da música usando um seletor mais flexível
    lyrics_divs = soup.find_all("div", class_=lambda c: c and "Lyrics__Container" in c)
    
    if not lyrics_divs:
        st.error("Não foi possível encontrar a letra na página.")
        return None

    lyrics = "\n".join([div.get_text("\n", strip=True) for div in lyrics_divs])
    
    return lyrics

def formatar_lyric(lyrics):
    """Melhora a formatação da letra para exibição no Streamlit"""
    formatted_lyrics = ""
    lines = lyrics.split("\n")
    
    for line in lines:
        if line.strip() == "":
            formatted_lyrics += "\n"  # Espaço extra para separar estrofes
        else:
            formatted_lyrics += f"<p>{line.strip()}</p>"  # Usa HTML para formatar as linhas
    
    return formatted_lyrics

# Campos de entrada
banda = st.text_input("Artista ou Banda: ", placeholder="Billie Eilish",key="banda")
musica = st.text_input("Música: ", placeholder="Lonely", key="musica")

# Botão de pesquisa
if st.button("Pesquisar"):
    # Buscando apenas pela música (ignorando o nome do artista)
    url, artista_correto = buscar_info_musica(musica)

    if url and artista_correto:
        # Se o nome do artista estiver diferente, apenas avisa
        if banda and artista_correto.lower() != banda.lower():
            st.warning(f"⚠️ O artista correto é **{artista_correto}**, e não **{banda}**.")
        
        letra = buscar_letra(url)
        if letra:
            with st.chat_message("user"):
                st.subheader(f"Lyrics de: {musica} - {artista_correto}")
                # Aplica a formatação bonita
                formatted_lyrics = formatar_lyric(letra)
                st.markdown(formatted_lyrics, unsafe_allow_html=True)
        else:
            with st.chat_message("ai"):  
                st.error("Não foi possível encontrar a letra da música.")
    else:
        with st.chat_message("ai"):
            st.error("Erro ao buscar a música. Verifique a digitação.")
