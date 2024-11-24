from PIL import Image, ImageDraw, ImageFont
import textwrap
from decouple import config

font_path = config("FONT_PATH")
bold_font_path = config("BOLD_FONT_PATH")

dpi = 300
font_size = 50
bold_font_size = 66.67

def split_text_into_pages(draw, font, text, max_width, max_height):
    lines = []
    paragraphs = text.splitlines()
    
    for paragraph in paragraphs:
        wrapped_lines = textwrap.wrap(paragraph, width=max_width // font_size)
        lines.extend(wrapped_lines or [""])

    pages = []
    current_page_lines = []
    current_height = 0

    for line in lines:
        line_bbox = font.getbbox(line)
        line_height = line_bbox[3] - line_bbox[1]

        if current_height + line_height > max_height:
            pages.append(current_page_lines)
            current_page_lines = []
            current_height = 0
        
        current_page_lines.append(line)
        current_height += line_height

    if current_page_lines:
        pages.append(current_page_lines)

    return pages

def create_pdf(template_image_path, output_pdf_path, text_blocks,chamber,dr_name_e,dr_c_e,dr_q_e,dr_name_b,dr_c_b,dr_q_b,p_name,p_age,p_sex,p_contact):
    template_image = Image.open(template_image_path).convert("RGB")
    font = ImageFont.truetype(font_path, font_size)
    bold_font = ImageFont.truetype(bold_font_path, bold_font_size)

    page_images = []

    draw = ImageDraw.Draw(template_image)
    pages_text_blocks = [
        split_text_into_pages(draw, font, block["text"], block["width"], block["height"])
        for block in text_blocks
    ]

    max_pages = max(len(pages) for pages in pages_text_blocks)

    for page_index in range(max_pages):
        page_image = template_image.copy()
        draw = ImageDraw.Draw(page_image)

        draw.text((83.33,600), chamber, font=font, fill="black")
        draw.text((1292,75), dr_name_e, font=bold_font, fill="white")
        draw.text((1292,180), dr_c_e, font=font, fill="white")
        draw.text((1292,255), dr_q_e, font=font, fill="white")
        draw.text((1292,416.67), dr_name_b, font=bold_font, fill="white")
        draw.text((1292,520), dr_c_b, font=font, fill="white")
        draw.text((1292,595), dr_q_b, font=font, fill="white")
        draw.text((83.33,1000), p_name, font=font, fill="black")
        draw.text((83.33,1100), p_age, font=font, fill="black")
        draw.text((83.33,1200), p_sex, font=font, fill="black")
        draw.text((83.33,1300), p_contact, font=font, fill="black")
        
        for block_index, block in enumerate(text_blocks):
            if page_index < len(pages_text_blocks[block_index]):
                page_lines = pages_text_blocks[block_index][page_index]
                y_text = block["y"]
                
                for line in page_lines:
                    draw.text((block["x"], y_text), line, font=font, fill="black")
                    y_text += font_size + 10

        page_images.append(page_image)

    page_images[0].save(output_pdf_path, save_all=True, append_images=page_images[1:], format="PDF", resolution=dpi)