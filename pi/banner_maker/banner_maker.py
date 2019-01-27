import datetime

from PIL import Image, ImageFont, ImageDraw, ImageEnhance

FONTS_PATH = 'banner_maker/fonts/led.ttf'
GEN_DIR = 'banner_maker/generated/'
TRAIN_TIMES = 'train_times'
LED_OUPUT_PATH = GEN_DIR + TRAIN_TIMES + '.ppm'
WEB_OUPUT_PATH = GEN_DIR + TRAIN_TIMES + '.jpg'
SUMMARY_HEIGHT = 16
VERTICAL_OFFSET = 4


class BannerMaker:

    @staticmethod
    def format_text(text):
        now = datetime.date.strftime(datetime.datetime.now(), "%-I:%M")
        text = '{} {} '.format(now, text)
        print(text)
        return text

    def replace_banner(self, train_text):
        if not train_text:
            print('no train text')
            return

        summary = self.format_text(train_text)

        font_size_in_points = 9
        font = ImageFont.truetype(FONTS_PATH, font_size_in_points)
        font_size = font.getsize(summary)

        summary_img = Image.new('RGB', font_size)
        draw = ImageDraw.Draw(summary_img)
        draw.text((0, 0), summary, font=font)

        enhancement = ImageEnhance.Contrast(summary_img)
        enhancement.enhance(1.99).save(LED_OUPUT_PATH)

        enhanced_summary = Image.open(LED_OUPUT_PATH)

        size = (enhanced_summary.width, SUMMARY_HEIGHT)

        banner = Image.new('RGB', size)
        banner.paste(enhanced_summary, (0, VERTICAL_OFFSET))

        banner.save(LED_OUPUT_PATH)
        banner.save(WEB_OUPUT_PATH)