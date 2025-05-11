import requests
import os
from dotenv import load_dotenv

# Load environment variables
# Assumes .env file is in the project root, one level above the script's directory (Picsart_3)
dotenv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '.env')
load_dotenv(dotenv_path=dotenv_path)
PICSART_API_KEY = os.getenv("PICSART_API_KEY")

# API Configuration
API_URL = "https://api.picsart.io/tools/1.0/removebg"
PAYLOAD = {"format": "PNG", "output_type": "cutout"} # Output format is PNG. 'cutout' gives transparent background.

def remove_image_background(image_full_path, output_folder_name_at_project_root, output_file_name_in_folder):
    """
    Removes the background of an image using the Picsart API and saves the result.

    Args:
        image_full_path (str): Absolute path to the image file.
        output_folder_name_at_project_root (str): Name of the output folder (e.g., "taikoo_images_modified").
                                                  This will be created at the project root level.
        output_file_name_in_folder (str): Name for the saved output file (e.g., "Task4_result.png").
    """
    if not PICSART_API_KEY:
        print("Error: PICSART_API_KEY not found. Please set it in your .env file located at the project root.")
        return

    # Validate input image path
    if not os.path.exists(image_full_path):
        print(f"Error: Image file not found at {image_full_path}")
        return

    headers = {
        "accept": "application/json",
        "x-picsart-api-key": PICSART_API_KEY
    }

    try:
        with open(image_full_path, "rb") as img_file:
            files = {
                # Use original filename for the multipart request
                "image": (os.path.basename(image_full_path), img_file, "image/png") # Assuming PNG, adjust if necessary
                # No "bg_image" is sent for background removal
            }

            print(f"Removing background from {os.path.basename(image_full_path)}...")
            # The PAYLOAD (with output_type: cutout) should instruct the API to remove the background
            response = requests.post(API_URL, headers=headers, data=PAYLOAD, files=files)

            # Determine script_dir to locate project_root for output
            script_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(script_dir)
            output_dir_absolute_path = os.path.join(project_root, output_folder_name_at_project_root)

            # Create output directory if it doesn't exist
            if not os.path.exists(output_dir_absolute_path):
                os.makedirs(output_dir_absolute_path)
                print(f"Created output directory: {output_dir_absolute_path}")

            output_file_path = os.path.join(output_dir_absolute_path, output_file_name_in_folder)

            if response.status_code == 200:
                try:
                    response_data = response.json() # Parse JSON response
                    if response_data.get("status") == "success" and response_data.get("data") and response_data["data"].get("url"):
                        image_download_url = response_data["data"]["url"]
                        print(f"Image processed successfully. Downloading from: {image_download_url}")
                        
                        # Download the image from the URL
                        image_response = requests.get(image_download_url, stream=True)
                        if image_response.status_code == 200:
                            with open(output_file_path, "wb") as f:
                                for chunk in image_response.iter_content(chunk_size=8192):
                                    f.write(chunk)
                            print(f"Image downloaded and saved to: {output_file_path}")
                        else:
                            print(f"Error downloading processed image. Status code: {image_response.status_code}")
                            print(f"Response: {image_response.text}")
                    else:
                        print(f"API success, but unexpected JSON structure in response:")
                        print(response.text) # Print the raw text if JSON is not as expected
                except ValueError: # Handles cases where response is not valid JSON
                    print("API call successful, but response was not valid JSON. Attempting to save raw content (if any).")
                    # This case might occur if the API sometimes returns image data directly
                    # and sometimes JSON. It's less likely given the user's report.
                    if response.content:
                        with open(output_file_path, "wb") as f:
                            f.write(response.content)
                        print(f"Saved raw API response content to: {output_file_path}")
                    else:
                        print("No content found in API response to save.")
            else:
                print(f"Error processing image. Status code: {response.status_code}")

    except FileNotFoundError as e:
        # This catch is redundant due to prior checks, but kept for safety.
        print(f"Error: One of the image files was not found during open: {e}")
    except requests.exceptions.RequestException as e:
        print(f"Error during API request: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def main():
    """
    Main function to configure and run the background removal process.
    """
    # Define the directory where source images are located
    image_source_directory = "/home/daniel/taikooResearch/taikoo_images/"

    # Configuration for the main execution:
    foreground_image_filename = "backpack.png"
    # background_image_filename = "bg2_image.png" # No longer needed for background removal

    foreground_image_full_path = os.path.join(image_source_directory, foreground_image_filename)
    # background_image_full_path = os.path.join(image_source_directory, background_image_filename) # No longer needed
    
    # Output configuration as per user request
    output_folder = "taikoo_images_modified" # Will be created at project root
    output_filename = "Task4_result.png"

    remove_image_background(
        foreground_image_full_path,
        output_folder,
        output_filename
    )

if __name__ == "__main__":
    main()
