import numpy as np
import cv2
import pytesseract
import re
import Levenshtein
from estnltk.taggers import SpellCheckRetagger
from estnltk import Text

#https://stackoverflow.com/questions/13538748/crop-black-edges-with-opencv
def crop_edges(image, thresh):
    y_nonzero, x_nonzero = np.nonzero(thresh)
    if len(y_nonzero) == 0 or len(x_nonzero) == 0:
        return image
    return image[np.min(y_nonzero):np.max(y_nonzero), np.min(x_nonzero):np.max(x_nonzero)]

def resize(img, resize_param):
    res = cv2.resize(img, (0,0), fx=resize_param, fy=resize_param, interpolation = cv2.INTER_CUBIC)
    return res

def multiply(img, pixel_multi):
    return np.clip(img.astype('uint16') * pixel_multi, 0, 255).astype('uint8')

def add(img, num):
    return np.clip(img.astype('uint16') + num, 0, 255).astype('uint8')

def adaptive_thresh(img, thresh_type, blocksize, C):
    thresh = cv2.adaptiveThreshold(img, 255, thresh_type, cv2.THRESH_BINARY, blocksize, C)
    return thresh

def otsu_thresh(img):
    ret, thresh = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    return thresh

def gaussian_blur(img, blur_size, blur_iter):
    img = cv2.GaussianBlur(img, (blur_size, blur_size), blur_size)
    return img

def median_blur(img, blur_size):
    img = cv2.medianBlur(img, blur_size)
    return img

def remove_background_noise(img, sigma = 33):
    blur = cv2.GaussianBlur(img, (0,0), sigmaX=sigma, sigmaY=sigma)
    img = cv2.divide(img, blur, scale=255)
    return img

def invert(img):
    return 255-img

def morph_open(img, kernel_size):
    img = invert(img)
    img = cv2.morphologyEx(img, cv2.MORPH_OPEN, np.ones((kernel_size, kernel_size)))
    img = invert(img)
    return img

def morph_close(img, kernel_size):
    img = invert(img)
    img = cv2.morphologyEx(img, cv2.MORPH_CLOSE, np.ones((kernel_size, kernel_size)))
    img = invert(img)
    return img

# https://stackoverflow.com/questions/4993082/how-can-i-sharpen-an-image-in-opencv
def unsharp_mask(image, kernel_size=(5, 5), sigma=1.0, amount=1.0, threshold=0):
    """Return a sharpened version of the image, using an unsharp mask."""
    blurred = cv2.GaussianBlur(image, kernel_size, sigma)
    sharpened = float(amount + 1) * image - float(amount) * blurred
    sharpened = np.maximum(sharpened, np.zeros(sharpened.shape))
    sharpened = np.minimum(sharpened, 255 * np.ones(sharpened.shape))
    sharpened = sharpened.round().astype(np.uint8)
    if threshold > 0:
        low_contrast_mask = np.absolute(image - blurred) < threshold
        np.copyto(sharpened, image, where=low_contrast_mask)
    return sharpened

def process_image_for_ocr(img, actions):
    if len(img.shape)==3:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        gray = img
    ret, binary_thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    img = crop_edges(gray, binary_thresh)
    for action in actions:
        img = action[0](img, *action[1:])
    return img

def detect_text_for_all_squares(grid):
    for square in grid.flatten():
        img = process_image_for_ocr(square.image, best_actions)
        predictions = []
        predictions.append(pytesseract.image_to_string(img, lang = 'est').lower())
        predictions.append(pytesseract.image_to_string(img, lang = 'est', config = r'--psm 4').lower())
        predictions.append(pytesseract.image_to_string(img, lang = 'est', config = r'--psm 6').lower())
        predictions.append(pytesseract.image_to_string(img, lang = 'est', config = r'--psm 12').lower())
        predictions.append(pytesseract.image_to_string(img, lang = 'est', config = r'--psm 13').lower())
        # If only one way detects text, it is probably an error
        empty_predictions = sum([p == "" for p in predictions])
        if empty_predictions>1:
            square.text = ""
        else:
            square.text = Levenshtein.median(predictions)

def clean_hint_text(text):
    clean = text.lower()
    tagged = Text(clean).tag_layer(['words'])
    spelling_tagger = SpellCheckRetagger()
    spelling_tagger.retag(tagged)
    clean_list = [span.normalized_form[0] if span.normalized_form[0] else span.text for span in tagged.words]
    clean = " ".join(clean_list)
    # Replace all punctuation except .-\n with dots
    clean = re.sub(r'([^\w\s.-]|_)','.', clean)
    # TODO replace double .. with ...
    # Join word parts together if word is written on two lines and joined by -
    clean = re.sub(r'\b(\w+)-\n(\w+)\b', r'\1\2', clean)
    clean = re.sub(r'\b(\w+)-\n\n(\w+)\b', r'\1\2', clean)
    # Replace \n with spaces
    # clean = clean.replace('\n', ' ')
    # Remove unneccessary spaces
    clean = re.sub(r' +', ' ', clean)
    return clean.strip()

best_actions = (
    (resize, 5),
    (multiply, 1.5),
    (adaptive_thresh, cv2.ADAPTIVE_THRESH_MEAN_C, 7, 3),
    (add, -50),
    (morph_open, 3),
    (morph_close, 3),
    (adaptive_thresh, cv2.ADAPTIVE_THRESH_MEAN_C, 15, 7)
)