import cv2
import time
import numpy as np
import tasks.util.logger as logger
import tasks.util.config as config
from .text_translator import TextTranslator
from PIL import Image, ImageDraw, ImageFont, ImageColor

class OverlayText:
    def __init__(self, azure_services):
        self.azure_services = azure_services
        self.text_translator = TextTranslator(self.azure_services)

    def prepare_overlay_image(self, image: Image, ocr_result, target_language):
        self.text_translator.translate_ocr_result(ocr_result)
        text_image = Image.new('RGBA', (image.width, image.height))
        if type(ocr_result) == self.azure_services.read_operation_result:
            for read_results in ocr_result.analyze_result.read_results:
                for line in read_results.lines:
                    text = line.text  # テキストを取得

                    # 翻訳を実行
                    translated_text = self.text_translator.translate(text, read_results.language, target_language)
                    if translated_text[1] == target_language:
                        continue

                    boundingBox = line.bounding_box#[int(i) for i in line.bounding_box]  # バウンディングボックスを取得
                    pts1 = np.float32([[boundingBox[i], boundingBox[i+1]] for i in range(0,8,2)])  # バウンディングボックスから座標を取得
                    width = max(np.linalg.norm(pts1[i]-pts1[(i+2)%4]) for i in range(0,4,2))  # 幅を計算
                    height = max(np.linalg.norm(pts1[i]-pts1[(i+3)%4]) for i in range(0,4,2))  # 高さを計算
                    font, nw = self.get_optimum_sized_font_and_width(translated_text[0], width, height)
                    if nw > width:
                        width = nw
                    # 翻訳したテキストを半透明の背景を持つバッファに描画
                    background_color = image.getpixel((pts1[0][0], pts1[0][1]))
                    img = Image.new('RGBA', (int(width), int(height)), (background_color[0], background_color[1], background_color[2],255))
                    d = ImageDraw.Draw(img)
                    d.text((0,0), translated_text[0], font=font, fill=self.get_text_color(image, background_color, pts1))
                    img = np.array(img)

                    # 射影変換を用いてバッファを元の画像に描画
                    pts2 = np.float32([[0,0],[width,0],[width,height],[0,height]])
                    M = cv2.getPerspectiveTransform(pts2, pts1)
                    dst = cv2.warpPerspective(img, M, (image.width, image.height))
                    
                    # 元の画像とdstを合成
                    dst = Image.fromarray(dst)
                    text_image = Image.alpha_composite(text_image.convert('RGBA'), dst)
        else:
            for region in ocr_result.regions:
                for line in region.lines:
                    text = ' '.join([word.text for word in line.words])  # 単語を一文に結合
                    # 翻訳を実行
                    translated_text = self.text_translator.translate(text, ocr_result.language, target_language)
                    if translated_text[1] == target_language:
                        continue
                    left, top, width, height = [int(value) for value in line.bounding_box.split(",")]  # 文章全体のバウンディングボックスを取得
                    nl, nt, nw, nh = [int(value) for value in [left, top, width, height]]
                    font, width = self.get_optimum_sized_font_and_width(translated_text[0], nw, nh)
                    if nw > width:
                        width = nw
                    # 翻訳したテキストを半透明の背景を持つバッファに描画
                    d = ImageDraw.Draw(text_image)
                    d.rectangle([(nl, nt), (nl + nw, nt + nh)], fill=(0, 0, 0, 255))
                    d.text((int(nl), int(nt)), translated_text[0], font=font, fill=image.getpixel((nl, nt)))
        return text_image

    def draw_text(self, image: Image, ocr_result, target_language):
        self.font_path = config.value_of("font_path") 
        return self.prepare_overlay_image(image, ocr_result, target_language)
        
    def get_optimum_sized_font_and_width(self, text, width, height):
        font = ImageFont.truetype(self.font_path, height)
        img_dummy = Image.new('RGB', (1, 1))
        d_dummy = ImageDraw.Draw(img_dummy)
        bbox = d_dummy.textbbox((0, 0), text, font=font)
        if bbox[2] > width or bbox[3] > height:
            low, high = 1, height
            while low <= high:
                mid = (low + high) // 2
                font = ImageFont.truetype(self.font_path, mid)
                bbox = d_dummy.textbbox((0, 0), text, font=font)
                if bbox[2] <= width and bbox[3] <= height:
                    low = mid + 1
                else:
                    high = mid - 1
                    
        if font.size < 12:
            font = ImageFont.truetype(self.font_path, 12)
            bbox = d_dummy.textbbox((0, 0), text, font=font)
            logger.warning(f"font size is too small: {font.size}->{text}")

        return font, bbox[2]
    
    def get_text_color(self, image: Image, background_color, pts1):
        #画像範囲内を分割し、それぞれの座標での色を取得し、background_colorから最もかけ離れた色をtext_colorとする。
        max_distance = 0
        text_color = background_color
        for i in range(5):
            for j in range(15):
                x = pts1[0][0] + (pts1[2][0] - pts1[0][0]) * i / 5
                y = pts1[0][1] + (pts1[2][1] - pts1[0][1]) * j / 15
                color = image.getpixel((x, y))
                if np.linalg.norm(np.array(color) - np.array(background_color)) > max_distance:
                    max_distance = np.linalg.norm(np.array(color) - np.array(background_color))
                    text_color = color
        return text_color
