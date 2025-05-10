# search_photo.py
import aiohttp
import json
import re
from .tarjima_anime_name import uzbek_mapping
from fuzzywuzzy import fuzz, process

async def handle_photo_from_file(image_bytes, BOT_TOKEN):
    async with aiohttp.ClientSession() as session:
        form = aiohttp.FormData()
        form.add_field('image', image_bytes, filename="anime.jpg", content_type='image/jpeg')

        async with session.post("https://api.trace.moe/search", data=form) as resp:
            if resp.status != 200:
                return {"error": "❌ Trace.moe xatosi"}

            data = await resp.json()

    if not data['result']:
        return {"error": "😔 Hech qanday anime topilmadi"}

    result = data['result'][0]
    anilist_id = result.get("anilist")
    filename = result.get("filename", "")
    episode = result.get("episode", "Noma'lum")
    similarity = round(result["similarity"] * 100, 2)
    from_time = int(result["from"])
    minutes, seconds = divmod(from_time, 60)

    match = re.search(r'\[(.*?)\]\s*([^-\[\]]+)', filename)
    title_from_filename = match.group(2).strip() if match else "Noma'lum"
    final_title = title_from_filename
    genre = "Janr topilmadi"

    if anilist_id:
        try:
            async with aiohttp.ClientSession() as api_session:
                anilist_query = """
                query ($id: Int) {
                    Media(id: $id, type: ANIME) {
                        title {
                            romaji
                            english
                            native
                            userPreferred
                        }
                        genres
                    }
                }
                """
                variables = {"id": anilist_id}
                headers = {"Content-Type": "application/json"}

                async with api_session.post(
                    "https://graphql.anilist.co",
                    json={"query": anilist_query, "variables": variables},
                    headers=headers
                ) as anilist_resp:
                    if anilist_resp.status == 200:
                        anilist_data = await anilist_resp.json()
                        media = anilist_data["data"]["Media"]
                        titles = media["title"]
                        final_title = titles.get("english") or titles.get("romaji") or titles.get("userPreferred") or titles.get("native") or final_title
                        genres = media.get("genres", [])
                        genre = ", ".join(genres) if genres else "Janr topilmadi"

        except Exception as e:
            final_title = f"Noma'lum (xatolik: {str(e)})"

    def find_best_match(title, mapping, threshold=70):
        choices = list(mapping.keys())
        best_match, score = process.extractOne(title, choices, scorer=fuzz.token_set_ratio)
        if score >= threshold:
            return mapping[best_match]
        return f"{title} (O'zbekcha tarjima yo'q)"

    uzbek_title = find_best_match(final_title, uzbek_mapping)

    return {
        "uzbek_title": uzbek_title,
        "similarity": similarity,
        "episode": episode,
        "minutes": minutes,
        "seconds": seconds,
        "genre": genre,
        "image": result["image"],
    }
