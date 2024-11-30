from PIL import Image, ImageDraw, ImageFont
from decouple import config
from datetime import datetime
import os

def get_distributed_left_list(cc_list, rf_list, oe_list, ix_list, dx_list):
    total_length = len(cc_list) + len(rf_list) + len(oe_list) + len(ix_list) + len(dx_list)
    if total_length <= 20:
        return [{
            'C/C: ': cc_list,
            'Risk Factor: ': rf_list,
            'O/E:': oe_list,
            'Investigations: ': ix_list,
            'Diagnosis: ': dx_list,
        }]
    
    distributed = []
    temp_data = {}
    current_length = 0

    for key, data in [('C/C: ', cc_list), ('Risk Factor: ', rf_list), ('O/E:', oe_list), ('Investigations: ', ix_list), ('Diagnosis: ', dx_list)]:
        if current_length + len(data) > 20:
            temp_data[key] = data[:20 - current_length]
            distributed.append(temp_data)
            temp_data = {key: data[20 - current_length:]}
            current_length = len(temp_data[key])
        else:
            temp_data[key] = data
            current_length += len(data)
    
    if temp_data:
        distributed.append(temp_data)
    
    return distributed

def get_distributed_right_list(prescription_text):
    lines = prescription_text.split('\n')
    if len(lines) <= 25:
        return [{'prescription_text': '\n'.join(lines)}]
    
    distributed = []
    for i in range(0, len(lines), 28):
        distributed.append({'prescription_text': '\n'.join(lines[i:i+25])})
    return distributed

def draw_left_column(draw, data, bold_font, regular_font, line_spacing, start_x, start_y):
    current_y = start_y
    for key, value in data.items():
        draw.text((start_x, current_y), key, font=bold_font, fill=(0, 0, 0))
        current_y += line_spacing
        for item in value:
            draw.ellipse((start_x + 20, current_y+40, start_x + 30, current_y + 50), fill=(0, 0, 0))
            draw.text((start_x + 40, current_y - 5), item, font=regular_font, fill=(0, 0, 0))
            current_y += line_spacing

def draw_right_column(draw, data, bold_font, regular_font, line_spacing, start_x, start_y):
    if 'prescription_text' in data:
        draw.text((start_x, start_y), "Rx:", font=bold_font, fill=(0, 0, 0))
        draw.multiline_text((start_x + 40, start_y + line_spacing), data['prescription_text'], font=regular_font, fill=(0, 0, 0), spacing=10)

def create_pdf(template_image_path,output_pdf_path,cc, rf, oe, ix, dx, prescription_text,chamber,dr_name_e,dr_d_e,dr_name_b,dr_d_b,p_name,p_age,p_sex,p_address):
    # Load base image
    image = Image.open(template_image_path).convert('RGB')
    image_width, image_height = image.size

    # Load fonts
    font_path = config("BOLD_FONT_PATH")
    regular_font_path = config("FONT_PATH")
    if not os.path.exists(font_path) or not os.path.exists(regular_font_path):
        raise FileNotFoundError("Font files not found at the specified paths.")

    bold_font = ImageFont.truetype(font_path, 60)
    regular_font = ImageFont.truetype(regular_font_path, 52)
    line_spacing = 80

    # Distribute data into pages
    cc_list = cc.split('\n')
    rf_list = rf.split('\n')
    oe_list = oe.split('\n')
    ix_list = ix.split('\n')
    dx_list = dx.split('\n')

    distributed_left_list = get_distributed_left_list(cc_list, rf_list, oe_list, ix_list, dx_list)
    distributed_right_list = get_distributed_right_list(prescription_text)

    # Determine number of pages
    pages = max(len(distributed_left_list), len(distributed_right_list))

    # Create pages
    page_images = []
    for i in range(pages):
        page_image = image.copy()
        draw = ImageDraw.Draw(page_image)

        #doc name writing
        draw.text((83.2,83.2),dr_name_b, font=bold_font, fill=(0,0,0))
        draw.multiline_text((83.2,83.2+line_spacing),dr_d_b,fill=(0,0,0),font=regular_font)
        dr_name_e_length = draw.textlength(dr_name_e,font=bold_font)
        draw.text((image_width-dr_name_e_length-83.2,83.2),dr_name_e, font=bold_font,fill=(0,0,0))
        max_dr_d_e_length_text = dr_d_e.split('\n')[0]
        for line in dr_d_e.split('\n'):
            if line == max_dr_d_e_length_text:
                max_dr_d_e_length_text = max_dr_d_e_length_text
            elif line < max_dr_d_e_length_text:
                max_dr_d_e_length_text = max_dr_d_e_length_text
            else:
                max_dr_d_e_length_text = line
        dr_d_e_length = draw.textlength(max_dr_d_e_length_text,font=regular_font)
        draw.multiline_text((image_width-dr_d_e_length-83.2,83.2+line_spacing),dr_d_e, font=regular_font,fill=(0,0,0),align='right',)
        draw.text((83.2,693),"নামঃ "+p_name, font=regular_font, fill=(255,255,255))
        draw.text((790.5,693),"বয়সঃ "+p_age, font=regular_font, fill=(255,255,255))
        draw.text((1325.625,693),"লিঙ্গঃ "+p_sex, font=regular_font, fill=(255,255,255))
        p_address_length = draw.textlength("ঠিকানাঃ "+p_address,font=regular_font)
        draw.text((image_width-p_address_length-83.2,693),"ঠিকানাঃ "+p_address, font=regular_font, fill=(255,255,255))

        #date and chamber drawing
        today = "তারিখঃ "+str(datetime.today().strftime('%d-%m-%Y %H:%M'))
        draw.text((83.2,3390.4),today, font=regular_font,fill=(255,255,255))
        chamber_length = draw.textlength("চেম্বারঃ "+chamber,font=regular_font)
        draw.text((image_width-chamber_length-83.2,3390.4),"চেম্বারঃ "+chamber, font=regular_font,fill=(255,255,255))

        # Draw left column
        left_data = distributed_left_list[i] if i < len(distributed_left_list) else {}
        draw_left_column(draw, left_data, bold_font, regular_font, line_spacing, start_x=86.5, start_y=910)

        # Draw right column
        right_data = distributed_right_list[i] if i < len(distributed_right_list) else {}
        draw_right_column(draw, right_data, bold_font, regular_font, line_spacing, start_x=1075, start_y=910)

        # Append page image
        page_images.append(page_image)

    # Save as PDF
    if page_images:
        page_images[0].save(output_pdf_path, save_all=True, append_images=page_images[1:], format="PDF")
    else:
        raise ValueError("No pages created to save as PDF.")