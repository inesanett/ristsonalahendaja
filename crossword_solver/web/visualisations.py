import cv2
from crossword_solver.square_classification import SquareType
from copy import deepcopy
from PIL import ImageFont, ImageDraw, Image
from crossword_solver.paths import FONT_PATH
from io import BytesIO
from base64 import b64encode


def plot_square_types(crossword):
    type_to_text = {
        SquareType.HINT : "V",
        SquareType.MULTIHINT : "W",
        SquareType.IRRELEVANT : "X",
        SquareType.EMPTY : "0",
    }

    plotting_image = cv2.add(deepcopy(crossword.image), 50)
    for gs in crossword.grid.flatten():
        plotting_image = cv2.circle(plotting_image, (gs.x_min,gs.y_min), radius=3, color=(0, 0, 0), thickness=-1)
        
    plotting_image = cv2.cvtColor(plotting_image, cv2.COLOR_BGR2RGB)
    pil_image = Image.fromarray(plotting_image)    
    draw = ImageDraw.Draw(pil_image)
    pil_font = ImageFont.truetype(FONT_PATH, 25)
    for gs in crossword.grid.flatten():
        t = type_to_text[gs.type]
        x = gs.x_min+(gs.width/2)
        y = gs.y_min+(gs.height/2)
        draw.text((x,y), t, font=pil_font, fill='#000', anchor='mm')
    return pil_to_base64(pil_image) 

def plot_solution_texts(crossword, solution_matrix):
    font = ImageFont.truetype(FONT_PATH, 25)
    image = deepcopy(crossword.image)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    pil_image = Image.fromarray(image)    
    for gs in crossword.grid.flatten():
        if gs.type == SquareType.EMPTY:
            t = solution_matrix[gs.grid_x, gs.grid_y].upper()
            if t != '_':
                draw = ImageDraw.Draw(pil_image)
                x = gs.x_min+(gs.width/2)
                y = gs.y_min+(gs.height/2)
                draw.text((x,y), t, font=font, fill='#000', anchor='mm')
    return pil_to_base64(pil_image)

def plot_no_solution(crossword):
    font = ImageFont.truetype(FONT_PATH, 40)
    image = deepcopy(crossword.image)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    pil_image = Image.fromarray(image)    
    t = "LAHENDUSI\n EI LEITUD"
    draw = ImageDraw.Draw(pil_image)
    draw.text((image.shape[1]/2, image.shape[0]/2), t, font=font, fill='#cd0000', anchor='mm')
    return pil_to_base64(pil_image)

def cv2_to_base64(input_img):
    file_object = BytesIO()
    img = Image.fromarray(cv2.cvtColor(input_img , cv2.COLOR_BGR2RGB))
    img.save(file_object, 'PNG')
    return  "data:image/png;base64,"+b64encode(file_object.getvalue()).decode('ascii')

def pil_to_base64(input_img):
    file_object = BytesIO()
    input_img.save(file_object, 'PNG')
    return  "data:image/png;base64,"+b64encode(file_object.getvalue()).decode('ascii')