import re
import os
from io import BytesIO

import requests
from PIL import Image, ImageDraw, ImageFont

from .parse import Parse, Rank, SteamID32
from app.config import BASE_DIR

class DotaProfile:
    def __init__(self, steam_link):
        if self._is_valid_steam_link(steam_link):
            userid = SteamID32.get_steamid32(steam_link)
            self.userinfo = Parse.get_user_info(userid)
            self.heroes_images = self.__output_images_of_five_favorite_characters()
        else:
            raise ValueError("Invalid Steam link format")

    @staticmethod
    def _is_valid_steam_link(steam_link):
        pattern = r'(?:https?://)?steamcommunity.com/(?:profiles|id)/[\w/]+'
        return re.match(pattern, steam_link) is not None

    def capture_this(self):
        # Setup Fonts
        nickname_font = self.__setup_font('SFNSDisplay-Bold', 22)
        lastmath_text = self.__setup_font('SFNSDisplay-Regular', 11)
        lastmath_data = self.__setup_font('SFNSDisplay-Semibold', 11)
        winloserate = self.__setup_font('SFNSDisplay-Regular', 12)
        stats_number = self.__setup_font('SFNSDisplay-Medium', 18)
        leaderboard_rank_font = self.__setup_font('SFNSDisplay-Medium', 16)

        img = Image.open(f'{BASE_DIR}/app/module/img/background.png')
        draw = ImageDraw.Draw(img)

        # Resize and paste avatar
        avatar = self.__take_avatar().resize((93, 93), resample=Image.Resampling.LANCZOS)
        img.paste(avatar, (25, 21))

        # Heroes images paste
        hero_positions = [(133, 93), (158, 93), (183, 93), (208, 93), (232, 93)]
        hero_images_resized = [x.resize((21, 21), resample=Image.Resampling.LANCZOS) for x in self.heroes_images]
        for position, hero_image in zip(hero_positions, hero_images_resized):
            img.paste(hero_image, position, mask=hero_image)

        rank_images = self.__rank_images()
        rank_image = rank_images[0].resize((100, 100), resample=Image.Resampling.LANCZOS)
        rank_stars_image = None

        if len(rank_images) == 2:
            if isinstance(rank_images[1], Image.Image):  # Если это изображение
                rank_stars_image = rank_images[1].resize((100, 100), resample=Image.Resampling.LANCZOS)

        img.paste(rank_image, (328, 20), mask=rank_image)
        if rank_stars_image:
            img.paste(rank_stars_image, (328, 20), mask=rank_stars_image)
        else:
            if len(rank_images) == 2 and isinstance(rank_images[1], int):
                leaderboard_rank = str(rank_images[1])
                bbox = draw.textbbox((0, 0), leaderboard_rank, font=leaderboard_rank_font)
                w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
                draw.text((380 - w, 103 - h), leaderboard_rank, font=leaderboard_rank_font, fill=(255, 255, 255))

        # Dota plus
        if self.userinfo['plus']:
            plus_img = Image.open(f'{BASE_DIR}/app/module/img/dota_plus.png').convert('RGBA')
            plus_img = plus_img.resize((27, 31), resample=Image.Resampling.LANCZOS)
            img.paste(plus_img, (103, 92), mask=plus_img)

        # First part
        draw.text((130, 17), self.userinfo['personaname'], font=nickname_font, fill=(255, 255, 255))
        draw.text((130, 45), 'Last match:', font=lastmath_text, fill=(142, 165, 176))
        draw.text((193, 45), self.userinfo['last_match'], font=lastmath_data, fill=(255, 255, 255))
        draw.text((130, 59), 'WON', font=winloserate, fill=(141, 165, 175))
        draw.text((190, 59), 'LOST', font=winloserate, fill=(141, 165, 175))
        draw.text((252, 59), 'WINRATE', font=winloserate, fill=(141, 165, 175))
        draw.text((130, 68), self.userinfo['win_count'], font=stats_number, fill=(100, 184, 105))
        draw.text((190, 68), self.userinfo['lose_count'], font=stats_number, fill=(241, 74, 76))
        draw.text((252, 68), self.userinfo['winrate'] + '%', font=stats_number, fill=(255, 255, 255))

        return img


    def __take_avatar(self):
        avatar = Image.open(BytesIO(requests.get(self.userinfo['avatar'], stream=True).content))
        return avatar

    @staticmethod
    def __setup_font(name, size):
        font_path = f'{BASE_DIR}/app/module/fonts/{name}.otf'

        if os.path.exists(font_path):
            try:
                print(f"Loading font from: {font_path}")
                with open(font_path, 'rb') as f:
                    font_data = BytesIO(f.read())
                return ImageFont.truetype(font_data, size)
            except Exception:
                pass

        return ImageFont.load_default()


    def __output_images_of_five_favorite_characters(self):
        heroes_images = []
        for hero in self.userinfo['heroes']:
            hero = hero.replace(' ', '_')
            image_png = Image.open(f'{BASE_DIR}/app/module/img/heroes/{hero}.png').convert('RGBA')
            heroes_images.append(image_png)
        return heroes_images

    def __rank_images(self):
        rank = str(Rank(self.userinfo['account_id'])).split()
        if rank[0] == 'Immortal':
            if int(rank[1]) > 100:
                rank_img = Image.open(f'{BASE_DIR}/app/module/img/ranks/Immortal.png').convert('RGBA')
                return [rank_img, int(rank[1])]
            elif 100 >= int(rank[1]) > 10:
                rank_img = Image.open(f'{BASE_DIR}/app/module/img/ranks/Immortalb.png').convert('RGBA')
                return [rank_img, int(rank[1])]
            elif 10 >= int(rank[1]) >= 1:
                rank_img = Image.open(f'{BASE_DIR}/app/module/img/ranks/Immortalc.png').convert('RGBA')
                return [rank_img, int(rank[1])]
        else:
            rank_img = Image.open(f'{BASE_DIR}/app/module/img/ranks/{rank[0]}.png').convert('RGBA')
            rank_stars_img = Image.open(f'{BASE_DIR}/app/module/img/ranks/stars/{rank[1]}.png').convert('RGBA')
            return [rank_img, rank_stars_img]

    def export(self, path=None):
        try:
            img = self.capture_this()

            if img is None:
                return None

            cards_dir = BASE_DIR / 'cards'
            cards_dir.mkdir(parents=True, exist_ok=True)

            file_path = cards_dir / f'{self.userinfo["account_id"]}.png'
            img.save(str(file_path), 'PNG')
            return str(self.userinfo['account_id'])

        except Exception:
            raise
