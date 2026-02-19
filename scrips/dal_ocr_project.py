#!/usr/bin/env python3
import pdfplumber
import numpy as np
import json
import time
import os
import re
from flask import Flask, request, jsonify, render_template, send_file, send_from_directory
from PIL import Image, ImageDraw
from multiprocessing import Pool, cpu_count
from pyzbar.pyzbar import decode

# OCR Modules
import easyocr
import pytesseract
from pytesseract import Output

app = Flask(__name__)

# Folders for uploads and static output.
UPLOAD_FOLDER = "uploads"
STATIC_FOLDER = "static"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(STATIC_FOLDER, exist_ok=True)

# Global initialization for EasyOCR.
easyocr_reader = easyocr.Reader(['en'])

def is_bullet_or_number(text):
    """Return True if text looks like a bullet/number."""
    return bool(re.match(r'^(\d+\.)|([•\-])', text.strip()))

###############################################################################
# OCR Processing Functions (Module Level)
###############################################################################

def process_page_tesseractOCR(page_num, pdf_path, pdf_name, render_resolution, json_mode, original_dims):
    """Process a single PDF page using TesseractOCR with barcode detection (pyzbar)."""
    print(f"Processing Page {page_num + 1} with TesseractOCR...")
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[page_num]
        image = page.to_image(resolution=render_resolution).original
        draw = ImageDraw.Draw(image)
        np_image = np.array(image)

        # --- Barcode Detection using pyzbar ---
        barcode_results = decode(np_image)
        barcode_boxes = []
        for barcode in barcode_results:
            x, y, w, h = barcode.rect
            barcode_text = barcode.data.decode("utf-8")
            barcode_box = {
                "text": f"Barcode ({barcode.type}): {barcode_text}",
                "x": x,
                "y": y,
                "width": w,
                "height": h,
                "corners": {
                    "top_left": (x, y),
                    "top_right": (x + w, y),
                    "bottom_left": (x, y + h),
                    "bottom_right": (x + w, y + h)
                },
                "source": "barcode"  # Mark box as coming from barcode detection.
            }
            barcode_boxes.append(barcode_box)
        # -------------------------------------------------------------------

        # Extract overall text using Tesseract.
        text = pytesseract.image_to_string(np_image, lang='eng')
        # Detailed OCR data with bounding boxes.
        data = pytesseract.image_to_data(np_image, lang='eng', output_type=Output.DICT)
        ocr_results = []
        n_boxes = len(data['text'])
        for i in range(n_boxes):
            word = data['text'][i].strip()
            if not word:
                continue
            try:
                conf = float(data['conf'][i])
            except ValueError:
                conf = 0.0
            left = data['left'][i]
            top = data['top'][i]
            width = data['width'][i]
            height = data['height'][i]
            # Create bounding box with four corners.
            bbox = [(left, top), (left + width, top),
                    (left + width, top + height), (left, top + height)]
            ocr_results.append((bbox, word, conf))
        
        # Build a word_data list.
        word_data = []
        for bbox, word, conf in ocr_results:
            label = word if (conf >= 45 and word) else "Image/Logo/Symbol/Signature Detected"
            x1, y1 = bbox[0]
            x3, y3 = bbox[2]
            word_data.append({
                "text": label,
                "x": int(x1),
                "y": int(y1),
                "width": int(x3 - x1),
                "height": int(y3 - y1)
            })
        
        # Group words into lines.
        word_data.sort(key=lambda w: (w["y"], w["x"]))
        line_groups = []
        line_threshold = 0.1
        max_horizontal_gap = 19.5
        current_group = []
        for wd in word_data:
            if not current_group:
                current_group.append(wd)
            else:
                avg_y = sum(item["y"] for item in current_group) / len(current_group)
                last_word = current_group[-1]
                last_right = last_word["x"] + last_word["width"]
                horizontal_gap = wd["x"] - last_right
                if abs(wd["y"] - avg_y) <= line_threshold and horizontal_gap <= max_horizontal_gap:
                    if is_bullet_or_number(wd["text"]) and is_bullet_or_number(current_group[-1]["text"]):
                        line_groups.append(current_group)
                        current_group = [wd]
                    else:
                        current_group.append(wd)
                else:
                    line_groups.append(current_group)
                    current_group = [wd]
        if current_group:
            line_groups.append(current_group)

        # Helper to add corner points.
        def add_corner_points(x, y, width, height):
            return {
                "top_left": (x, y),
                "top_right": (x + width, y),
                "bottom_left": (x, y + height),
                "bottom_right": (x + width, y + height)
            }

        # Convert line groups into bounding boxes with corners.
        grouped_boxes = []
        for group in line_groups:
            line_text = " ".join(item["text"] for item in group)
            min_x = min(item["x"] for item in group)
            min_y = min(item["y"] for item in group)
            max_x = max(item["x"] + item["width"] for item in group)
            max_y = max(item["y"] + item["height"] for item in group)
            width = max_x - min_x
            height = max_y - min_y
            corners = add_corner_points(min_x, min_y, width, height)
            grouped_boxes.append({
                "text": line_text,
                "x": min_x,
                "y": min_y,
                "width": width,
                "height": height,
                "corners": corners
            })
        
        # Optionally merge boxes that are very close.
        def boxes_are_close_or_overlap(boxA, boxB, threshold=2, max_horizontal_gap=10, max_vertical_gap=2):
            A_left = boxA["x"] - threshold
            A_right = boxA["x"] + boxA["width"] + threshold
            A_top = boxA["y"] - threshold
            A_bottom = boxA["y"] + boxA["height"] + threshold
            B_left = boxB["x"] - threshold
            B_right = boxB["x"] + boxB["width"] + threshold
            B_top = boxB["y"] - threshold
            B_bottom = boxB["y"] + boxB["height"] + threshold
            horizontal_overlap = not (A_right < B_left or A_left > B_right)
            vertical_overlap = not (A_bottom < B_top or A_top > B_bottom)
            if boxA["x"] + boxA["width"] < boxB["x"]:
                horizontal_gap = boxB["x"] - (boxA["x"] + boxA["width"])
            elif boxB["x"] + boxB["width"] < boxA["x"]:
                horizontal_gap = boxA["x"] - (boxB["x"] + boxB["width"])
            else:
                horizontal_gap = 0
            if boxA["y"] + boxA["height"] < boxB["y"]:
                vertical_gap = boxB["y"] - (boxA["y"] + boxA["height"])
            elif boxB["y"] + boxB["height"] < boxA["y"]:
                vertical_gap = boxA["y"] - (boxB["y"] + boxB["height"])
            else:
                vertical_gap = 0
            if horizontal_gap > max_horizontal_gap or vertical_gap > max_vertical_gap:
                return False
            return horizontal_overlap and vertical_overlap
        
        def merge_two_boxes(boxA, boxB):
            merged_text = boxA["text"] + " " + boxB["text"]
            min_x = min(boxA["x"], boxB["x"])
            min_y = min(boxA["y"], boxB["y"])
            max_x = max(boxA["x"] + boxA["width"], boxB["x"] + boxB["width"])
            max_y = max(boxA["y"] + boxA["height"], boxB["y"] + boxB["height"])
            width = max_x - min_x
            height = max_y - min_y
            corners = add_corner_points(min_x, min_y, width, height)
            return {
                "text": merged_text,
                "x": min_x,
                "y": min_y,
                "width": width,
                "height": height,
                "corners": corners
            }
        
        if not grouped_boxes:
            grouped_boxes = []
        merged = True
        while merged and grouped_boxes:
            merged = False
            new_list = []
            while grouped_boxes:
                current = grouped_boxes.pop(0)
                has_merged = False
                for i, other in enumerate(grouped_boxes):
                    if boxes_are_close_or_overlap(current, other, threshold=10, max_horizontal_gap=max_horizontal_gap, max_vertical_gap=10):
                        merged_box = merge_two_boxes(current, other)
                        new_list.append(merged_box)
                        grouped_boxes.pop(i)
                        has_merged = True
                        merged = True
                        break
                if not has_merged:
                    new_list.append(current)
            grouped_boxes = new_list

        # Append barcode boxes to OCR-detected boxes.
        grouped_boxes.extend(barcode_boxes)

        # Draw bounding boxes using computed corners.
        # Use blue for barcode boxes, red for OCR boxes.
        for box in grouped_boxes:
            x1, y1 = box["corners"]["top_left"]
            x2, y2 = box["corners"]["bottom_right"]
            if x2 < x1:
                x1, x2 = x2, x1
            if y2 < y1:
                y1, y2 = y2, y1
            # Determine the drawing color.
            color = "green" if box.get("source") == "barcode" else "blue"
            draw.rectangle([(x1, y1), (x2, y2)], outline=color, width=4)

        pdf_output_folder = os.path.join(STATIC_FOLDER, pdf_name)
        os.makedirs(pdf_output_folder, exist_ok=True)
        output_image_path = os.path.join(pdf_output_folder, f"output_visualized_page_{page_num+1}.png")
        image.save(output_image_path)
        
        if json_mode == "with_text":
            page_data = {
                "page": page_num + 1,
                "boxes": grouped_boxes,
                "text": text
            }
        else:
            page_data = {
                "page": page_num + 1,
                "boxes": [{
                    "x": box["x"],
                    "y": box["y"],
                    "width": box["width"],
                    "height": box["height"],
                    "corners": box["corners"]
                } for box in grouped_boxes]
            }
        json_output_path = os.path.join(pdf_output_folder, f"text_extraction_page_{page_num+1}.json")
        with open(json_output_path, "w") as f:
            json.dump(page_data, f, indent=4)
        return page_data

def process_page_easyocr(page_num, pdf_path, pdf_name, render_resolution, json_mode, original_dims):
    """Process a single PDF page using EasyOCR with integrated barcode detection (pyzbar)."""
    print(f"Processing Page {page_num + 1} with EasyOCR...")
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[page_num]
        image = page.to_image(resolution=render_resolution).original
        draw = ImageDraw.Draw(image)
        np_image = np.array(image)

        # --- Barcode Detection with pyzbar ---
        from pyzbar.pyzbar import decode  # ensure pyzbar is imported
        barcode_results = decode(np_image)
        barcode_boxes = []
        for barcode in barcode_results:
            x, y, w, h = barcode.rect
            barcode_text = barcode.data.decode("utf-8")
            barcode_box = {
                "text": f"Barcode ({barcode.type}): {barcode_text}",
                "x": x,
                "y": y,
                "width": w,
                "height": h,
                "corners": {
                    "top_left": (x, y),
                    "top_right": (x + w, y),
                    "bottom_left": (x, y + h),
                    "bottom_right": (x + w, y + h)
                },
                "source": "barcode"  # Tag to mark this box as coming from barcode detection.
            }
            barcode_boxes.append(barcode_box)
        # -----------------------------------------------------------------

        # Extract overall text from EasyOCR (detail=0) and detailed OCR data.
        text_lines = easyocr_reader.readtext(np_image, detail=0)
        text = " ".join(text_lines)
        ocr_results = easyocr_reader.readtext(np_image)
        word_data = []
        for bbox, word, conf in ocr_results:
            label = word if (conf >= 0.45 and word) else "Image/Logo/Symbol/Signature Detected"
            x1, y1 = bbox[0]
            x3, y3 = bbox[2]
            word_data.append({
                "text": label,
                "x": int(x1),
                "y": int(y1),
                "width": int(x3 - x1),
                "height": int(y3 - y1)
            })

        # Group words into lines.
        word_data.sort(key=lambda w: (w["y"], w["x"]))
        line_groups = []
        line_threshold = 0.1
        max_horizontal_gap = 19.5
        current_group = []
        for wd in word_data:
            if not current_group:
                current_group.append(wd)
            else:
                avg_y = sum(item["y"] for item in current_group) / len(current_group)
                last_word = current_group[-1]
                last_right = last_word["x"] + last_word["width"]
                horizontal_gap = wd["x"] - last_right
                if abs(wd["y"] - avg_y) <= line_threshold and horizontal_gap <= max_horizontal_gap:
                    if is_bullet_or_number(wd["text"]) and is_bullet_or_number(current_group[-1]["text"]):
                        line_groups.append(current_group)
                        current_group = [wd]
                    else:
                        current_group.append(wd)
                else:
                    line_groups.append(current_group)
                    current_group = [wd]
        if current_group:
            line_groups.append(current_group)

        # Helper to compute corner points.
        def add_corner_points(x, y, width, height):
            return {
                "top_left": (x, y),
                "top_right": (x + width, y),
                "bottom_left": (x, y + height),
                "bottom_right": (x + width, y + height)
            }

        # Convert line groups into bounding boxes with corners.
        grouped_boxes = []
        for group in line_groups:
            line_text = " ".join(item["text"] for item in group)
            min_x = min(item["x"] for item in group)
            min_y = min(item["y"] for item in group)
            max_x = max(item["x"] + item["width"] for item in group)
            max_y = max(item["y"] + item["height"] for item in group)
            width = max_x - min_x
            height = max_y - min_y
            corners = add_corner_points(min_x, min_y, width, height)
            grouped_boxes.append({
                "text": line_text,
                "x": min_x,
                "y": min_y,
                "width": width,
                "height": height,
                "corners": corners
            })

        # Optionally merge boxes that are very close.
        def boxes_are_close_or_overlap(boxA, boxB, threshold=2, max_horizontal_gap=10, max_vertical_gap=2):
            A_left = boxA["x"] - threshold
            A_right = boxA["x"] + boxA["width"] + threshold
            A_top = boxA["y"] - threshold
            A_bottom = boxA["y"] + boxA["height"] + threshold
            B_left = boxB["x"] - threshold
            B_right = boxB["x"] + boxB["width"] + threshold
            B_top = boxB["y"] - threshold
            B_bottom = boxB["y"] + boxB["height"] + threshold
            horizontal_overlap = not (A_right < B_left or A_left > B_right)
            vertical_overlap = not (A_bottom < B_top or A_top > B_bottom)
            if boxA["x"] + boxA["width"] < boxB["x"]:
                horizontal_gap = boxB["x"] - (boxA["x"] + boxA["width"])
            elif boxB["x"] + boxB["width"] < boxA["x"]:
                horizontal_gap = boxA["x"] - (boxB["x"] + boxB["width"])
            else:
                horizontal_gap = 0
            if boxA["y"] + boxA["height"] < boxB["y"]:
                vertical_gap = boxB["y"] - (boxA["y"] + boxA["height"])
            elif boxB["y"] + boxB["height"] < boxA["y"]:
                vertical_gap = boxA["y"] - (boxB["y"] + boxB["height"])
            else:
                vertical_gap = 0
            if horizontal_gap > max_horizontal_gap or vertical_gap > max_vertical_gap:
                return False
            return horizontal_overlap and vertical_overlap

        def merge_two_boxes(boxA, boxB):
            merged_text = boxA["text"] + " " + boxB["text"]
            min_x = min(boxA["x"], boxB["x"])
            min_y = min(boxA["y"], boxB["y"])
            max_x = max(boxA["x"] + boxA["width"], boxB["x"] + boxB["width"])
            max_y = max(boxA["y"] + boxA["height"], boxB["y"] + boxB["height"])
            width = max_x - min_x
            height = max_y - min_y
            corners = add_corner_points(min_x, min_y, width, height)
            return {
                "text": merged_text,
                "x": min_x,
                "y": min_y,
                "width": width,
                "height": height,
                "corners": corners
            }

        if not grouped_boxes:
            grouped_boxes = []
        merged = True
        while merged and grouped_boxes:
            merged = False
            new_list = []
            while grouped_boxes:
                current = grouped_boxes.pop(0)
                has_merged = False
                for i, other in enumerate(grouped_boxes):
                    if boxes_are_close_or_overlap(current, other, threshold=10, max_horizontal_gap=max_horizontal_gap, max_vertical_gap=10):
                        merged_box = merge_two_boxes(current, other)
                        new_list.append(merged_box)
                        grouped_boxes.pop(i)
                        has_merged = True
                        merged = True
                        break
                if not has_merged:
                    new_list.append(current)
            grouped_boxes = new_list

        # Append barcode boxes into the final results.
        grouped_boxes.extend(barcode_boxes)

        # Draw bounding boxes.
        for box in grouped_boxes:
            x1, y1 = box["corners"]["top_left"]
            x2, y2 = box["corners"]["bottom_right"]
            if x2 < x1:
                x1, x2 = x2, x1
            if y2 < y1:
                y1, y2 = y2, y1
            # Use blue for barcode boxes, red for normal OCR boxes.
            color = "blue" if box.get("source") == "barcode" else "red"
            draw.rectangle([(x1, y1), (x2, y2)], outline=color, width=4)

        # Save processed image and JSON output.
        pdf_output_folder = os.path.join(STATIC_FOLDER, pdf_name)
        os.makedirs(pdf_output_folder, exist_ok=True)
        output_image_path = os.path.join(pdf_output_folder, f"output_visualized_page_{page_num+1}.png")
        image.save(output_image_path)

        if json_mode == "with_text":
            page_data = {
                "page": page_num + 1,
                "boxes": grouped_boxes,
                "text": text
            }
        else:
            page_data = {
                "page": page_num + 1,
                "boxes": [{
                    "x": box["x"],
                    "y": box["y"],
                    "width": box["width"],
                    "height": box["height"],
                    "corners": box["corners"]
                } for box in grouped_boxes]
            }
        json_output_path = os.path.join(pdf_output_folder, f"text_extraction_page_{page_num+1}.json")
        with open(json_output_path, "w") as f:
            json.dump(page_data, f, indent=4)
        return page_data

###############################################################################
# Combined OCR Processing Function
###############################################################################
def extract_text_and_convert_to_json(pdf_path, render_resolution, json_mode, original_dims, ocr_engine):
    start_time = time.time()
    pdf_name = os.path.basename(pdf_path).replace(".pdf", "")
    pdf_output_folder = os.path.join(STATIC_FOLDER, pdf_name)
    if os.path.exists(pdf_output_folder):
        for f in os.listdir(pdf_output_folder):
            os.remove(os.path.join(pdf_output_folder, f))
    else:
        os.makedirs(pdf_output_folder, exist_ok=True)
    with pdfplumber.open(pdf_path) as pdf:
        num_pages = len(pdf.pages)
    
    if ocr_engine == "tesseract":
        process_page_func = process_page_tesseractOCR
    else:
        process_page_func = process_page_easyocr

    with Pool(max(cpu_count() - 1, 1)) as pool:
        results = pool.starmap(
            process_page_func,
            [(i, pdf_path, pdf_name, render_resolution, json_mode, original_dims) for i in range(num_pages)]
        )
    execution_time = time.time() - start_time
    return results, execution_time, num_pages

###############################################################################
# Image to PDF Conversion Utility
###############################################################################
def image_to_pdf_file(input_path, output_pdf_path, conversion_resolution):
    try:
        image = Image.open(input_path).convert("RGB")
        image.save(output_pdf_path, "PDF", resolution=conversion_resolution)
        print("Image converted to PDF:", output_pdf_path)
        return output_pdf_path
    except Exception as e:
        print("Error converting image to PDF:", e)
        return None

###############################################################################
# Flask Routes
###############################################################################
@app.route('/')
def upload_form():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"})
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"})
    
    # Read document type, JSON mode, and OCR engine from the form.
    doc_type = request.form.get('doc_type')
    json_mode = request.form.get('json_mode')
    ocr_engine = request.form.get('ocr_engine', 'easyocr').lower()  # default to easyocr

    # Set default resolutions based on OCR engine and document type.
    if ocr_engine == "tesseract":
        if doc_type == "large":
            conversion_resolution = 200
            render_resolution = 150
        elif doc_type == "small":
            conversion_resolution = 100
            render_resolution = 110
        elif doc_type == "custom":
            try:
                conversion_resolution = float(request.form.get('conversion_resolution', 100))
                render_resolution = float(request.form.get('render_resolution', 300))
            except ValueError:
                return jsonify({"error": "Invalid custom resolution values"}), 400
        else:
            conversion_resolution = 100
            render_resolution = 110
    else:  # easyocr
        if doc_type == "large":
            conversion_resolution = 55
            render_resolution = 500
        elif doc_type == "small":
            conversion_resolution = 100
            render_resolution = 300
        elif doc_type == "custom":
            try:
                conversion_resolution = float(request.form.get('conversion_resolution', 100))
                render_resolution = float(request.form.get('render_resolution', 300))
            except ValueError:
                return jsonify({"error": "Invalid custom resolution values"}), 400
        else:
            conversion_resolution = 100
            render_resolution = 300

    filename = file.filename
    file_ext = os.path.splitext(filename)[1].lower()
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)
    original_filepath = filepath

    original_dims = None
    if file_ext not in [".pdf"]:
        try:
            orig_img = Image.open(filepath)
            original_dims = orig_img.size
        except Exception as e:
            print("Error reading original image dimensions:", e)
        pdf_filename = os.path.splitext(filename)[0] + ".pdf"
        pdf_file_path = os.path.join(UPLOAD_FOLDER, pdf_filename)
        converted = image_to_pdf_file(filepath, pdf_file_path, conversion_resolution)
        if not converted:
            return jsonify({"error": "Image to PDF conversion failed"}), 500
        filepath = pdf_file_path
        filename = pdf_filename

    results, execution_time, num_pages = extract_text_and_convert_to_json(filepath, render_resolution, json_mode, original_dims, ocr_engine)
    pdf_name = os.path.basename(filepath).replace(".pdf", "")
    pdf_output_folder = os.path.join(STATIC_FOLDER, pdf_name)
    output_image_path = os.path.join(pdf_output_folder, "output_visualized_page_1.png")
    json_output_path = os.path.join(pdf_output_folder, "text_extraction_page_1.json")

    original_filepath_abs = os.path.abspath(original_filepath)
    processed_image_path_abs = os.path.abspath(output_image_path)
    processed_json_path_abs = os.path.abspath(json_output_path)

    print("Original uploaded file path:", original_filepath_abs)
    print("Processed image file path:", processed_image_path_abs)
    print("Processed JSON file path:", processed_json_path_abs)
    print(f"Execution Time: {execution_time:.2f} seconds")

    paths_data = {
        "original_image_path": original_filepath_abs,
        "processed_image_path": processed_image_path_abs,
        "processed_json_path": processed_json_path_abs
    }
    with open("last_paths.json", "w") as f:
        json.dump(paths_data, f, indent=4)

    redirect_url = f"/results/{pdf_name}"
    return jsonify({
        "status": "success",
        "redirect": redirect_url,
        "execution_time": f"{execution_time:.2f}"
    })

@app.route('/results/<pdf_name>')
def display_results(pdf_name):
    pdf_output_folder = os.path.join(STATIC_FOLDER, pdf_name)
    if not os.path.exists(pdf_output_folder):
        return jsonify({"error": "PDF results not found"}), 404
    num_pages = sum(1 for f in os.listdir(pdf_output_folder) if f.endswith(".png"))
    return render_template('results.html', num_pages=num_pages, pdf_name=pdf_name)

@app.route('/json_data/<pdf_name>/<int:page>')
def get_json_data(pdf_name, page):
    pdf_output_folder = os.path.join(STATIC_FOLDER, pdf_name)
    json_output_path = os.path.join(pdf_output_folder, f"text_extraction_page_{page}.json")
    if not os.path.exists(pdf_output_folder):
        return jsonify({"error": "PDF not found"}), 404
    if not os.path.exists(json_output_path):
        return jsonify({"error": "JSON file not found"}), 404
    return send_file(json_output_path, mimetype='application/json')

@app.route('/templates/<path:filename>')
def send_template_file(filename):
    return send_from_directory('templates', filename)

@app.route('/highlighted_image/<pdf_name>/<int:page>')
def get_highlighted_image(pdf_name, page):
    pdf_output_folder = os.path.join(STATIC_FOLDER, pdf_name)
    image_path = os.path.join(pdf_output_folder, f"output_visualized_page_{page}.png")
    if not os.path.exists(pdf_output_folder):
        return jsonify({"error": "PDF not found"}), 404
    if not os.path.exists(image_path):
        return jsonify({"error": "Image not found"}), 404
    return send_file(image_path, mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=True)
    