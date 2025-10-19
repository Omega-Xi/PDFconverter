#import fitz
#import statistics
import io
#import cv2
#from PIL import Image
#import pytesseract
#import numpy as np
from dotenv import load_dotenv
import os
import platform
import shutil
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Try to find a valid Tesseract path automatically
def get_tesseract_path():
    env_path = os.getenv("TESSERACT_PATH")
    if env_path and os.path.exists(env_path):
        return env_path

    # Common Linux locations
    for path in ["/usr/bin/tesseract", "/usr/local/bin/tesseract", "/snap/bin/tesseract"]:
        if os.path.exists(path):
            return path

    # Windows default
    win_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    if platform.system() == "Windows" and os.path.exists(win_path):
        return win_path

    # As last resort, check PATH
    found = shutil.which("tesseract")
    if found:
        return found

    return None


tesseract_path = get_tesseract_path()
if tesseract_path:
    pytesseract.pytesseract.tesseract_cmd = tesseract_path
    print(f"[INFO] Using Tesseract at {tesseract_path}")
else:
    print("[ERROR] No valid Tesseract executable found! OCR will not work.")


# Load environment variables
load_dotenv()

# Use variables
tesseract_path = os.getenv("TESSERACT_PATH")
if tesseract_path:
    import pytesseract
    pytesseract.pytesseract.tesseract_cmd = tesseract_path

if not os.path.exists(tesseract_path):
    print(f"[WARN] Tesseract path not found at {tesseract_path}")

# Optional: for language detection
try:
    from langdetect import detect, DetectorFactory
    DetectorFactory.seed = 0
    USE_LANG_DETECT = True
except ImportError:
    USE_LANG_DETECT = False

# Path to Tesseract executable
pytesseract.pytesseract.tesseract_cmd = os.getenv(
    "TESSERACT_PATH", r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

#import fitz
import io
from pypdf import PdfReader

def pdf_to_txt(pdfFile):

    #passing pdf object to pdf reader
    reader=PdfReader(pdfFile)
    text=""
    for page in reader.pages:
        extracted=page.extract_text()
        if extracted:
            text+=extracted
    
    textFile=io.BytesIO(text.encode("utf-8"))
    textFile.name="converted.txt"
    textFile.seek(0)
    return textFile

if __name__=="__main__":
    txt=pdf_to_txt("1-2014.pdf")
    with open("converted.txt", "wb") as f:
        f.write(txt.getvalue())

# def pdf_to_txt(pdfFile):
#     text = ""
#     try:
#         # --- Step 1: Get all installed languages ---
#         available_langs = pytesseract.get_languages(config='')
#         if not available_langs:
#             print("[WARN] No Tesseract languages found. Defaulting to English.")
#             available_langs = ['eng']

#         # Combine all languages into a single string for Tesseract
#         all_langs = '+'.join(available_langs)
#         print(f"[INFO] Installed Tesseract languages: {available_langs}")

#         # --- Step 2: Read PDF ---
#         pdf_content = pdfFile.read()
#         with fitz.open(stream=pdf_content, filetype="pdf") as doc:
#             lang_string = all_langs  # default: use all installed languages

#             for page_num, page in enumerate(doc):
#                 # Render page as image (~300 DPI)
#                 zoom = 300 / 72
#                 mat = fitz.Matrix(zoom, zoom)
#                 pix = page.get_pixmap(matrix=mat)

#                 img_bytes = pix.tobytes("png")
#                 pil_image = Image.open(io.BytesIO(img_bytes))
#                 opencv_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

#                 # --- Preprocessing ---
#                 gray = cv2.cvtColor(opencv_image, cv2.COLOR_BGR2GRAY)
#                 blur = cv2.GaussianBlur(gray, (3, 3), 0)
#                 bw = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

#                 # Ensure black text on white background
#                 if np.mean(bw) < 127:
#                     bw = cv2.bitwise_not(bw)

#                 # --- Deskewing ---
#                 h, w = bw.shape
#                 crop = bw[h // 4:3 * h // 4, w // 4:3 * w // 4]
#                 coords = np.column_stack(np.where(crop > 0))
#                 if coords.size > 0:
#                     angle = cv2.minAreaRect(coords)[-1]
#                     angle = -(90 + angle) if angle < -45 else -angle
#                 else:
#                     angle = 0

#                 if 1.5 < abs(angle) < 45:
#                     M = cv2.getRotationMatrix2D((w // 2, h // 2), angle, 1.0)
#                     bw = cv2.warpAffine(
#                         bw, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE
#                     )
#                     bw = cv2.threshold(bw, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

#                 # --- Optional language detection (first page only) ---
#                 if USE_LANG_DETECT and page_num == 0:
#                     try:
#                         sample_text = pytesseract.image_to_string(bw, lang='eng', config='--psm 6')
#                         detected_lang = detect(sample_text)
#                         # Map to tesseract codes if they exist
#                         detected_candidates = [l for l in available_langs if detected_lang in l]
#                         if detected_candidates:
#                             lang_string = '+'.join(detected_candidates)
#                             print(f"[INFO] Detected main language: {detected_candidates}")
#                         else:
#                             print(f"[INFO] Could not map '{detected_lang}', using all languages.")
#                             lang_string = all_langs
#                     except Exception as e:
#                         print(f"[WARN] Language detection failed: {e}")
#                         lang_string = all_langs

#                 bw = remove_page_border(bw)

#                 # --- Text region detection ---
#                 kernel_width = max(30, opencv_image.shape[1] // 100)
#                 kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_width, 1))
#                 closed = cv2.morphologyEx(bw, cv2.MORPH_CLOSE, kernel)

#                 contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
#                 rows, _ = sort_contours(contours)

#                 # --- OCR per detected row ---
#                 for row in rows:
#                     x_min = min(b[1][0] for b in row)
#                     y_min = min(b[1][1] for b in row)
#                     x_max = max(b[1][0] + b[1][2] for b in row)
#                     y_max = max(b[1][1] + b[1][3] for b in row)

#                     roi = bw[y_min:y_max, x_min:x_max]
#                     config = r'--oem 3 --psm 6'
#                     try:
#                         extracted_text = pytesseract.image_to_string(roi, lang=lang_string, config=config)
#                     except pytesseract.TesseractError:
#                         # fallback to English if one of the traineddata files is broken
#                         extracted_text = pytesseract.image_to_string(roi, lang='eng', config=config)
#                     text += extracted_text.strip() + "\n"

#     except Exception as e:
#         print(f"An Error Occurred: {e}")
#         return io.BytesIO(b"")

#     textFile = io.BytesIO(text.encode("utf-8"))
#     textFile.name = "converted.txt"
#     textFile.seek(0)
#     return textFile


# def sort_contours(contours, tolerance=10):
#     bounding_boxes = [cv2.boundingRect(c) for c in contours]
#     contours_with_boxes = sorted(zip(contours, bounding_boxes), key=lambda b: b[1][1])

#     rows, current_row, row_ys = [], [], []
#     for contour, (x, y, w, h) in contours_with_boxes:
#         if not row_ys or abs(y - statistics.median(row_ys)) <= tolerance:
#             current_row.append((contour, (x, y, w, h)))
#             row_ys.append(y)
#         else:
#             rows.append(current_row)
#             current_row, row_ys = [(contour, (x, y, w, h))], [y]

#     if current_row:
#         rows.append(current_row)

#     sorted_contours = [c for row in rows for c, _ in sorted(row, key=lambda b: b[1][0])]
#     return rows, sorted_contours

# def remove_page_border(bw):
#     # Remove a solid outer border if present
#     contours, _ = cv2.findContours(bw, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
#     if not contours:
#         return bw

#     # Get largest contour (likely the page border)
#     largest_contour = max(contours, key=cv2.contourArea)
#     x, y, w, h = cv2.boundingRect(largest_contour)

#     # Calculate area ratios
#     page_area = bw.shape[0] * bw.shape[1]
#     contour_area = cv2.contourArea(largest_contour)

#     # If the largest contour is nearly the full page, crop inside it slightly
#     if contour_area / page_area > 0.9:
#         margin = int(min(w, h) * 0.02)  # 2% inward crop
#         bw = bw[y + margin:y + h - margin, x + margin:x + w - margin]
#     return bw


# if __name__ == "__main__":
#     try:
#         with open("1-2014.pdf", "rb") as doc:
#             pdfFile = io.BytesIO(doc.read())
#         txt = pdf_to_txt(pdfFile)
#         with open("converted.txt", "wb") as f:
#             f.write(txt.getvalue())
#         print("✅ OCR completed successfully. Output saved to 'converted.txt'.")
#     except Exception as e:
#         print(f"An Error Occurred: {e}")
