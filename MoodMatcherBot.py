import asyncio
import re

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import CallbackQueryHandler, Application, CommandHandler, CallbackContext, filters, MessageHandler
import random
import requests  # used to the increase the timeout to access spotify
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os
import time
import yt_dlp as youtube_dl
from collections import defaultdict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


print(f"Before: why?")

current_page = defaultdict(lambda: 0)
print(f"Before2: why?")
search_title = defaultdict(str)
print(f"Before3: why?")
search_list = {}
print(f"Before4: why?")

SPOTIFY_CLIENT_ID = "af7649e254f64ea599efaf7a4da70042"
print(f"Before5: why?")
SPOTIFY_CLIENT_SECRET = "acadba0539e7418b8ac98169e855f13e"
print(f"Before6: why?")

spotify = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET
))
print(f"Before7: why?")

<<<<<<< HEAD

ffmpeg_path = os.getenv('FFMPEG_PATH', 'ffmpeg')

FFMPEG_PATH = r"C:\Users\Bewnet\Downloads\ffmpeg-master-latest-win64-gpl\bin"

=======
ffmpeg_path = os.get('FFMPEG_PATH', '/usr/local/bin/ffmpeg') 

FFMPEG_PATH = ffmpeg_path        # local path{r"C:\Users\Bewnet\Downloads\ffmpeg-master-latest-win64-gpl\bin"}
>>>>>>> e02244d9f6c2f7e33012bc3a43233745e3af6c2b
TELEGRAM_TOKEN = "7721272091:AAF0okX_gbCM1hgYd5pI9n0_Ww6goVuL4MY"
print(f"Before8: why?")

session = requests.Session()
adapter = requests.adapters.HTTPAdapter(max_retries=3)  # Optional: Retry on failures
session.mount('https://', adapter)
session.request = lambda *args, **kwargs: requests.request(*args, **kwargs, timeout=30)  # Set 30 seconds timeout


try:
    available_genres = spotify.recommendation_genre_seeds()
    print(f"Available genres: {available_genres}")
except Exception as e:
    print(f"Error: {e}")

async def start(update: Update, context: CallbackContext):
    keyboard = [
        [KeyboardButton("😊 Happy"), KeyboardButton("😎 Relaxed")],  # First row
        [KeyboardButton("⚡ Energetic"), KeyboardButton("😃 Excited"), KeyboardButton("✈ Adventurous")],
        [KeyboardButton("😔 Sad"), KeyboardButton("😡 Angry 💢"), KeyboardButton("🌑 Dark")],  # Second row
        [KeyboardButton("😍 Romantic"), KeyboardButton("🎴 Mellow"), KeyboardButton("🧐 Focused")],  # Third row
        [KeyboardButton("😝 Playful"), KeyboardButton("🧓 Nostalgic 👴")]
    ]

    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    welcome_message = (
        f"👋 Hi there, {update.effective_user.username}!\n\n"
        f"🎵 I'm *Mood Matcher*! Tell me your current mood, "
        f"and I'll suggest a perfect song for you 🎶🎵🎼\n\n"
        f"✨ Pick an option below to get started!"
    )

    temp = await update.message.reply_text(welcome_message, reply_markup=reply_markup, parse_mode="Markdown")
    try:
        await update.message.delete()
    except Exception as e:
        print(f"Error while deleting the original message: {e}")


async def help(update: Update, context: CallbackContext):
    await update.message.reply_text(
        """
        /start  -  Start the bot
/suggest <mood> - Suggests song based on mood
/help - All commands
        """
    )


async def display_songs_with_buttons(update: Update, songs, genre):
    # Prepare inline keyboard buttons for each song
    buttons = [
        [InlineKeyboardButton(text=song[0], callback_data=song[0])]
        for song in songs
    ]
    next_btn = InlineKeyboardButton('➡️ Next', callback_data=f'genre {genre}')
    close_btn = InlineKeyboardButton("❌ Close", callback_data='close')

    buttons.append([next_btn])
    buttons.append([close_btn])

    markup = InlineKeyboardMarkup(buttons)

    # Check if update is from a message or callback query
    if update.message:
        await update.message.reply_text(f"Here are some songs for {genre} genre:", reply_markup=markup)
    elif update.callback_query:
        await update.callback_query.answer()  # Acknowledge the callback
        await update.callback_query.message.reply_text(f"Here are some songs for {genre} genre:", reply_markup=markup)
    else:
        print("Error: Neither message nor callback query found in the update.")


async def suggest_by_specific_genre(genre, update: Update):
    try:
        results = spotify.recommendations(
            seed_genres=[genre],  # Only one genre now
            limit=10,
            requests_session=session
        )
        if results['tracks']:
            # Prepare the list of songs with artist names
            songs = [
                (track['name'], ', '.join(artist['name'] for artist in track['artists']))
                for track in results['tracks']
            ]

            # Pass the songs to the display function
            await display_songs_with_buttons(update, songs, genre)
        else:
            await update.callback_query.message.reply_text(f"Couldn't find other suggestions for  (genre: {genre}).")
    except Exception as e:
        print(f"Error in suggest_by_specific_genre: {e}")


async def suggest_by_mood(update, context, feel=""):
    mood = ""
    """Suggest songs based on the user's mood with buttons."""
    if update.callback_query:
        if context.args:
            # Join the arguments and lower the case
            mood = ' '.join(context.args).lower()

    elif update.message:
        mood = feel.lower()
    else:
        if update.message:
            await update.message.reply_text("Please provide a mood or use a valid reply button.")
        return

    if not mood:
        await update.message.reply_text("Please provide a mood from the last if. Usage: /suggest [mood]")
        return

    print(f"mood = {mood}")
    clear_mood = mood.replace("/suggest", " ")
    clear_mood = clear_mood.strip()
    print(f"mood = {clear_mood}")
    # Define the mood to genre mapping
    mood_to_genre = {
        "happy": ["afrobeat", "dance", "pop", "disco", "happy", "latin", "ska", "club", "party", "reggaeton", "synth-pop"],
        "relaxed": ["acoustic", "ambient", "chill", "classical", "jazz", "study", "bossanova", "bluegrass", "folk"],
        "romantic": ["romance", "samba", "r-n-b", "soul", "latin", "brazil", "mpb", "piano"],
        "sad": ["acoustic", "emo", "folk", "blues", "sad", "indie", "rainy-day", "singer-songwriter"],
        "excited": ["electronic", "house", 'salsa', "techno", "drum-and-bass", "dubstep", "edm", "hardstyle", "trance"],
        "dark": ["black-metal", "goth", "industrial", "darkwave", "death-metal", "grindcore"],
        "energetic": ["hip-hop", "rock", 'rock-n-roll', "punk", "metal", "heavy-metal", "hard-rock", "psych-rock", "garage", "power-pop"],
        "nostalgic": ["british", "funk", "disco", "jazz", "soundtracks", "grunge"],
        "adventurous": ["world-music", "afrobeat", "samba", "indian", "turkish", "latin", "philippines-opm"],
        "angry": ["punk", "metal", "industrial", "hardcore", "trap", "metalcore", "post-dubstep"],
        "mellow": ["folk", "acoustic", "indie", "chill", "ambient", "alt-rock", "mandopop", "soul"],
        "playful": ["children", "comedy", "disney", "anime", "k-pop", "j-pop", "j-idol", "holidays"],
        "focused": ["study", "idm", "electronic", "detroit-techno", "minimal-techno", "trance", "progressive-house"]
    }


    # Randomly select a genre based on the mood
    genres = mood_to_genre.get(clear_mood)

    if not genres:
        await update.message.reply_text(f"Sorry, I don't have suggestions for the mood '{clear_mood}'.")
        return

    # Randomly choose a single genre from the list
    genre = random.choice(genres)


    try:
        results = spotify.recommendations(
            seed_genres=[genre],  # Only one genre now
            limit=10,
            requests_session=session
        )

        if results['tracks']:
            # Prepare the list of songs with artist names
            songs = [
                (track['name'], ', '.join(artist['name'] for artist in track['artists']))
                for track in results['tracks']
            ]

            # Pass the songs to the display function
            await display_songs_with_buttons(update, songs, genre)
        else:
            await update.message.reply_text(f"Couldn't find suggestions for mood '{clear_mood}' (genre: {genre}).")

    except Exception as e:
        print(f"Error in suggest_by_mood: {e}")


async def button_callback(update: Update, context: CallbackContext):
    callback_data = update.callback_query.data
    message = update.callback_query.message  # Fixed access to message
    chat_id = message.chat_id
    await update.callback_query.answer()

    if callback_data == "next":
        if current_page[chat_id] == 4:
            await message.reply_text("This is the last page!!")
            return
        else:
            current_page[chat_id] += 1
            await search_from_youtube(search_title[chat_id], message, current_page[chat_id])
            return
    elif callback_data == "back":
        if current_page[chat_id] == 0:
            await message.reply_text("This is the first page!!")
            return
        else:
            current_page[chat_id] -= 1
            await search_from_youtube(search_title[chat_id], message, current_page[chat_id])
            return
    elif callback_data == "close":
        try:
            await message.delete()
        except Exception as e:
            print(f"Failed to delete message: {e}")
            return
    elif "genre" in callback_data:
        genre = callback_data.replace("genre", " ")
        genre = genre.strip()
        await update.callback_query.message.delete()
        await suggest_by_specific_genre(genre, update)
        return
    elif "artist" in callback_data:
        song_name = callback_data.replace("artist", "").strip()
        await search_from_youtube(song_name, message, 0)
        return
    else:
        temp = await message.reply_text("Downloading...")
        await download_song(callback_data, message)
        await temp.delete()
        return


async def download_song(song_name, message):
    keyboard = []  # Create an empty list for buttons

    ydl_opts_soundcloud = {
        'format': 'bestaudio/best',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '128',
        }],
        'ffmpeg_location': FFMPEG_PATH,
        'quiet': True,
        'noplaylist': True,
        'concurrent_fragment_downloads': 5,
    }

    ydl_opts_youtube = {
        'format': 'bestaudio/best',
        'extract_flat':True,
        'quiet': True,
        'noplaylist': True,
    }

    try:
        # Search on YouTube for views
        youtube_search_query = f"ytsearch1:{song_name}"
        print(f"🔍 Searching \"{song_name}\" on YouTube...")
        youtube_views = "No data"
        youtube_url = None
        with youtube_dl.YoutubeDL(ydl_opts_youtube) as ydl:
            yt_info = ydl.extract_info(youtube_search_query, download=False)
            yt_video_info = yt_info['entries'][0]
            youtube_views = await format_number(yt_video_info.get("view_count", "No data"))
            youtube_url = yt_video_info.get("webpage_url")

        # Search and download from SoundCloud
        soundcloud_search_query = f"scsearch1:{song_name}"
        print(f"🔍 Searching and downloading \"{song_name}\" from SoundCloud...")
        with youtube_dl.YoutubeDL(ydl_opts_soundcloud) as ydl:
            sc_info = ydl.extract_info(soundcloud_search_query, download=True)
            sc_video_info = sc_info['entries'][0]
            sc_title = sc_video_info.get("title", "Unknown Title")
            sc_uploader = sc_video_info.get("uploader", "Unknown Artist")
            sc_views = await format_number(sc_video_info.get("view_count", "No data"))
            file_path = ydl.prepare_filename(sc_video_info)
            mp3_file_path = file_path.rsplit('.', 1)[0] + '.mp3'

        # Caption for the message
        caption = (
            f"🎵 *Song:* {sc_title}\n"
            f"🎤 *Artist:* {sc_uploader}\n"
            f"👁‍🗨 *YouTube Views:* {youtube_views}\n"
            f"👁‍🗨 *SoundCloud Views:* {sc_views}\n"
            f"📥 *Enjoy your download!*"
        )

        # Check if the file exists and send
        if os.path.exists(mp3_file_path):
            with open(mp3_file_path, 'rb') as audio_file:
                # Add interactive buttons
                if youtube_url:
                    keyboard.append([InlineKeyboardButton("🔗 View on YouTube", url=youtube_url)])
                keyboard.append([InlineKeyboardButton(f"🎧 More from {sc_title}", callback_data=f"artist_{sc_uploader}")])
                markup = InlineKeyboardMarkup(keyboard)

                for i in range(3):  # Retry logic
                    try:
                        await asyncio.wait_for(
                            message.reply_audio(
                                audio=audio_file,
                                caption=caption,
                                parse_mode="Markdown",
                                reply_markup=markup,
                            ),
                            timeout=30,  # Timeout in seconds
                        )
                        return
                    except Exception as e:
                        print(f"Retry {i + 1}/3 failed: {e}")
                        await asyncio.sleep(5)
            os.remove(mp3_file_path)
        else:
            temp_text = await message.reply_text(f"❌ Could not find the audio file: {mp3_file_path}")
            await asyncio.sleep(10)
            await temp_text.delete()
            return

    except Exception as e:
        temp_text = await message.reply_text(f"⚠️ An error occurred: {str(e)}")
        await asyncio.sleep(15)
        await temp_text.delete()
        return


async def search_from_youtube(song_name, message, page=0):
    global search_title, current_page, search_list

    chat_id = message.chat.id
    keyboard = []  # Create an empty list for the buttons
    ydl_opts = {
        'format': 'bestaudio/best',
        'extract_flat': True,
    }

    search_query = f"ytsearch25:{song_name}"
    try:
        if song_name != search_title.get(chat_id):
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(search_query, download=False)
                entries = info['entries']

                current_page[chat_id] = page
                search_title[chat_id] = song_name
                search_list[chat_id] = entries
                page_items = entries[0:5]
        else:
            page_items = search_list[chat_id][current_page[chat_id] * 5:(current_page[chat_id] + 1) * 5]

        for item in page_items:
            formated_view = await format_number(item.get("view_count", "No data"))
            button = InlineKeyboardButton(
                f"{item['title']}:  👀 {formated_view} ", callback_data=item['id'])
            keyboard.append([button])  # Add each button as a row

        back_btn = InlineKeyboardButton('⬅️ Back', callback_data='back')
        next_btn = InlineKeyboardButton('➡️ Next', callback_data='next')
        close_btn = InlineKeyboardButton("❌ Close", callback_data='close')

        keyboard.append([back_btn, next_btn])
        keyboard.append([close_btn])

        markup = InlineKeyboardMarkup(keyboard) # Add navigation buttons

        try:
            if not message.audio:
                await message.delete()
        except Exception as e:
            print(f"I think message does not exist. Error: {e}")

        temp_text = await message.reply_text(f"Result of {song_name}: ", reply_markup=markup)

    except Exception as e:
        temp_text = await message.reply_text(f"An error occurred: {e}")
        try:
            await asyncio.sleep(3)
            await temp_text.delete()
        except Exception as e:
            print(f"Error: {e}")
            return



async def format_number(n):
        try:
            num = int(n)
            if num >= 1_000_000_000:
                return f"{num / 1_000_000_000:.2f}B"
            elif num >= 1_000_000:
                return f"{num / 1_000_000:.2f}M"
            elif num >= 1_000:
                return f"{num / 1_000:.1f}K"
        except Exception as e:
            print(f"Can`t change to integer: {e}")

        else:
            return str(n)


async def message_handler(update: Update, context: CallbackContext):
    specials = ["Romantic", "Focused", "Angry", "Playful", "Adventurous", "Nostalgic", "Relaxed", "Happy", "Dark", "Mellow", "Sad", "Excited", "Energetic"]
    mood = re.sub(r"[^a-zA-Z]", "", update.message.text)
    print(f"mood = {mood}, update.text = {update.message.text}")
    if mood in specials:
        await suggest_by_mood(update, context, mood)
        try:
            await asyncio.sleep(3)
            await update.message.delete()
        except Exception as e:
            print(f"Error: {e}")
            return
    else:
        song_name = update.message.text
        await search_from_youtube(song_name, update.message, 0)
        return


async def error_handler(update, context):
    logger.error(msg="Exception while handling an update:", exc_info=context.error)
    return



def main():

    # Create an Application instance with your bot token
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("suggest", suggest_by_mood))
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    application.add_error_handler(error_handler)

    # Start the bot
    application.run_polling(timeout=30, poll_interval=1)


if __name__ == "__main__":
    main()
