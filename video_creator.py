import os
import random
from moviepy.editor import ImageClip, TextClip, CompositeVideoClip, ColorClip, AudioFileClip
from moviepy.config import get_setting
from scrape_quote import getQuote
import re



cartella_immagini = "./stoic/images"
cartella_audio = "./stoic/music"  # Assicurati che questa cartella esista e contenga file audio

def wrap_text(text, font, fontsize, max_width):
    """
    Wrap the text so that each line won't exceed max_width pixels (approssimato)
    """
    words = text.split(' ')
    lines = []
    current_line = ""

    for word in words:
        test_line = current_line + (" " if current_line else "") + word
        # Crea clip temporaneo per misurare larghezza testo
        clip = TextClip(test_line, fontsize=fontsize, font=font)
        w, h = clip.size
        clip.close()  # chiudiamo la risorsa
        if w <= max_width:
            current_line = test_line
        else:
            # if current line empty means the word itself too long, force add anyway
            if current_line:
                lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    return "\n".join(lines)

def scegli_immagine(cartella_immagini):
    estensioni_immagini = ('.png', '.jpg', '.jpeg', '.bmp', '.gif')
    immagini = [f for f in os.listdir(cartella_immagini) if f.lower().endswith(estensioni_immagini)]

    if not immagini:
        raise ValueError(f"Nessuna immagine trovata nella cartella: {cartella_immagini}")

    immagine_scelta = random.choice(immagini)
    path_immagine = os.path.join(cartella_immagini, immagine_scelta)
    print(f"Immagine scelta: {immagine_scelta}")
    return path_immagine

def scegli_audio(cartella_audio):
    """
    Sceglie un file audio casuale dalla cartella specificata.
    """
    estensioni_audio = ('.mp3', '.wav', '.ogg')  # Estensioni audio supportate
    audio_files = [f for f in os.listdir(cartella_audio) if f.lower().endswith(estensioni_audio)]

    if not audio_files:
        raise ValueError(f"Nessun file audio trovato nella cartella: {cartella_audio}")

    audio_scelto = random.choice(audio_files)
    path_audio = os.path.join(cartella_audio, audio_scelto)
    print(f"File audio scelto: {audio_scelto}")
    return path_audio

def crea_cartella(percorso):
    if not os.path.exists(percorso):
        os.makedirs(percorso)
    else:
        pass

def sanitize_filename(filename):
    """
    Rimuove caratteri non validi e spazi dal nome del file per renderlo sicuro per l'uso come nome di file.
    """
    # Rimuove caratteri non alfanumerici tranne spazi e punti
    filename = re.sub(r'[^\w\s.-]', '', filename)
    # Sostituisce gli spazi con underscore
    filename = filename.replace(' ', '_')
    # Limita la lunghezza del nome del file
    filename = filename[:200]  # Limita a 200 caratteri per sicurezza
    return filename

def name_ext(quote):
    nome_cartella = 'output'
    crea_cartella(nome_cartella)
    """
    Funzione che genera un nome di file basato sulla citazione, pulito e sicuro.
    """
    nome_file = sanitize_filename(quote)
    return f"{nome_cartella}/{nome_file}.mp4"

def crea_video():
    # Ottieni una citazione dalla funzione getQuote
    quote_data = getQuote()
    testo = quote_data.get('text', 'text')
    autore = quote_data.get('author', 'author')

    durata = 5
    fadein_durata = 1.5
    fontsize = 16
    colore = 'white'
    font = 'Arial-Bold'
    autore_fontsize = fontsize - 2  # Dimensione leggermente più piccola per l'autore

    path_immagine = scegli_immagine(cartella_immagini)
    path_audio = scegli_audio(cartella_audio)  # Ottieni il percorso del file audio

    larghezza_video = 1080
    altezza_video = 1920

    # Crea immagine base e ridimensiona per occupare l'intero frame
    img_clip = ImageClip(path_immagine).resize((larghezza_video, altezza_video)).set_duration(durata)
    
    logo = ImageClip("./logo.png").resize((100, 100)).set_duration(durata).set_opacity(0.8).set_position(("center", "bottom")).margin(bottom=100, opacity=0)

    # Crea layer nero con opacità 50%
    overlay_nero = ColorClip(size=(larghezza_video, altezza_video), color=(0, 0, 0))
    overlay_nero = overlay_nero.set_opacity(0.5).set_duration(durata)

    max_text_width = larghezza_video * 0.7  # 70% della larghezza immagine

    # Applichiamo il wrapping al testo
    testo_wrap = wrap_text(testo, font, fontsize, max_text_width)

    # Crea clip di testo
    txt_clip = TextClip(testo_wrap, fontsize=fontsize, color=colore, font=font, method='label')
    txt_clip = txt_clip.set_duration(durata)

    # Crea clip di autore
    autore_clip = TextClip(f"- {autore}", fontsize=autore_fontsize, color=colore, font=font, method='label')
    autore_clip = autore_clip.set_duration(durata)

    # Calcola la posizione verticale del testo e dell'autore
    txt_clip_height = txt_clip.h
    autore_clip_height = autore_clip.h

    # Calcola il centro verticale dell'immagine
    center_y = altezza_video / 2

    # Posiziona il testo principale al centro
    txt_clip = txt_clip.set_position(('center', center_y - txt_clip_height/2 - 10))

    # Posiziona l'autore sotto il testo principale con un piccolo margine
    margin = 10  # Margine tra il testo e l'autore
    autore_y = center_y + txt_clip_height/2 + margin
    autore_clip = autore_clip.set_position(('center', autore_y))

    # Applica la stessa animazione di fadein a tutti i layer
    img_clip = img_clip.crossfadein(fadein_durata)
    overlay_nero = overlay_nero.crossfadein(fadein_durata)

    # Aggiungi layer nero tra immagine e testo
    video = CompositeVideoClip([img_clip, overlay_nero, txt_clip, autore_clip, logo], size=(larghezza_video, altezza_video))

    # Carica il file audio
    audio_clip = AudioFileClip(path_audio)
    
    # Imposta la durata dell'audio in modo che corrisponda alla durata del video
    audio_clip = audio_clip.set_duration(durata)
    
    # Attacca l'audio al video
    video = video.set_audio(audio_clip)
    
    # Imposta la durata del video composto
    video = video.set_duration(durata)
    
    # Usa la citazione per il nome del file
    nome_file_output = name_ext(testo)

    # esporta video utilizzando solo la GPU
    video.write_videofile(nome_file_output, fps=24, codec='h264_nvenc', preset='fast', audio_codec='aac') #aggiunto audio_codec

    # Libera le risorse audio
    audio_clip.close()

crea_video()