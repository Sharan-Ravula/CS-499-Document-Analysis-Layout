# coordinates.py
import os
import json
from PIL import Image
from pdf2image import convert_from_path

def get_image_dimensions(file_path):
    """
    Returns the dimensions (width, height) of the file.
    For PDFs, it converts the first page to an image using 300 dpi.
    For images, it returns the pixel dimensions.
    """
    if file_path.lower().endswith('.pdf'):
        from pdf2image import convert_from_path
        pages = convert_from_path(file_path, dpi=300)
        return pages[0].size
    else:
        with Image.open(file_path) as img:
            return img.size

def calculate_scaling_factors(original_path, processed_path):
    """
    Calculates scaling ratios for width and height, defined as:
       ratio_x = processed_width / original_width
       ratio_y = processed_height / original_height
    """
    orig_width, orig_height = get_image_dimensions(original_path)
    proc_width, proc_height = get_image_dimensions(processed_path)
    ratio_x = proc_width / orig_width
    ratio_y = proc_height / orig_height
    return orig_width, orig_height, proc_width, proc_height, ratio_x, ratio_y

def convert_processed_to_original(processed_coord, ratio_x, ratio_y):
    """
    Converts a coordinate (x, y) from the processed image coordinate system
    to the original coordinate system.
    """
    proc_x, proc_y = processed_coord
    orig_x = proc_x / ratio_x
    orig_y = proc_y / ratio_y
    return (orig_x, orig_y)

def update_json_coordinates(json_path, ratio_x, ratio_y, orig_width, orig_height):
    with open(json_path, "r") as f:
        data = json.load(f)
    
    updated_boxes = []
    for box in data.get("boxes", []):
        orig_box_x = box["x"] / ratio_x
        orig_box_y = box["y"] / ratio_y
        orig_box_width = box["width"] / ratio_x
        orig_box_height = box["height"] / ratio_y

        updated_box = {
            "x": orig_box_x,
            "y": orig_box_y,
            "width": orig_box_width,
            "height": orig_box_height
        }
        if "text" in box:
            updated_box["text"] = box["text"]

        # If 'corners' are provided, update them.
        if "corners" in box:
            updated_box["corners"] = {
                "top_left": convert_processed_to_original(box["corners"]["top_left"], ratio_x, ratio_y),
                "top_right": convert_processed_to_original(box["corners"]["top_right"], ratio_x, ratio_y),
                "bottom_left": convert_processed_to_original(box["corners"]["bottom_left"], ratio_x, ratio_y),
                "bottom_right": convert_processed_to_original(box["corners"]["bottom_right"], ratio_x, ratio_y)
            }
        else:
            # Otherwise, compute corners based on x, y, width, and height.
            updated_box["corners"] = {
                "top_left": [orig_box_x, orig_box_y],
                "top_right": [orig_box_x + orig_box_width, orig_box_y],
                "bottom_left": [orig_box_x, orig_box_y + orig_box_height],
                "bottom_right": [orig_box_x + orig_box_width, orig_box_y + orig_box_height]
            }
        updated_boxes.append(updated_box)
    
    page_num = data.get("page", 1)
    updated_data = {
        "page": page_num,
        "boxes": updated_boxes,
        "original_width": orig_width,
        "original_height": orig_height
    }
    return updated_data


def process_coordinates(original_path, processed_image_path, processed_json_path):
    """
    Given the file paths for:
       - the original file (image or PDF),
       - the processed image,
       - and the processed JSON (OCR output with processed coordinates),
    this function:
       1. Logs the absolute file paths.
       2. Calculates the scaling factors (using 300 dpi for PDF conversion).
       3. Updates the JSON coordinates to the original coordinate system.
    
    Returns:
       The updated JSON data.
    """
    # Log the absolute paths:
    print(f"original_image_path = \"{os.path.abspath(original_path)}\"")
    print(f"processed_image_path = \"{os.path.abspath(processed_image_path)}\"")
    print(f"processed_json_path = \"{os.path.abspath(processed_json_path)}\"")
    
    # Compute scaling factors.
    orig_width, orig_height, proc_width, proc_height, ratio_x, ratio_y = calculate_scaling_factors(original_path, processed_image_path)
    print(f"Dimensions: original=({orig_width}x{orig_height}), processed=({proc_width}x{proc_height})")
    print(f"Scaling Ratios: ratio_x = {ratio_x:.4f}, ratio_y = {ratio_y:.4f}")
    
    # Update JSON coordinates.
    updated_data = update_json_coordinates(processed_json_path, ratio_x, ratio_y, orig_width, orig_height)
    return updated_data

if __name__ == "__main__":

    # 1. Read the saved paths from last_paths.json
    with open("last_paths.json", "r") as f:
        paths_data = json.load(f)

    original_image_path = paths_data["original_image_path"]
    processed_image_path = paths_data["processed_image_path"]
    processed_json_path = paths_data["processed_json_path"]

    # 2. Call process_coordinates using those paths
    updated_data = process_coordinates(original_image_path, processed_image_path, processed_json_path)

    # 3. Optionally save the updated JSON or just print it
    updated_json_path = os.path.join(os.path.dirname(processed_json_path), "original_text_extraction_page_1.json")
    with open(updated_json_path, "w") as f:
        json.dump(updated_data, f, indent=4)

    print(f"Updated JSON saved to {os.path.abspath(updated_json_path)}")

