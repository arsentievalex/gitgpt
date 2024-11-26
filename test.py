from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os.path
from google.oauth2 import service_account
from googleapiclient.discovery import build
import time


# Define the path to your Service Account credentials file
SERVICE_ACCOUNT_FILE = 'service_acc.json'

# Define the scope for Google Slides API
SCOPES = ['https://www.googleapis.com/auth/presentations',
          'https://www.googleapis.com/auth/drive']

creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)

# Build the service for both Google Drive and Google Slides APIs
drive_service = build('drive', 'v3', credentials=creds)
slides_service = build('slides', 'v1', credentials=creds)


def make_copy_of_presentation(presentation_id, copy_title, folder_id):
    """
    Make a copy of the Google Slides presentation using Google Drive API.

    :param presentation_id: The ID of the original Google Slides presentation.
    :param copy_title: The title of the new copied presentation.
    :return: The presentation ID of the copied presentation.
    """
    # Create a copy of the file using Google Drive API
    copied_file = {
        'name': copy_title,
        'parents': [folder_id]  # Place the file in the specified folder
    }

    # Use the Google Drive API to copy the file
    copy = drive_service.files().copy(
        fileId=presentation_id,
        body=copied_file
    ).execute()

    # Return the new presentation ID of the copied file
    return copy.get('id')


# Function to replace text in a slide based on the slide index and replacement dictionary
def replace_text_in_slide_by_index(presentation_id, slide_index, replacements):
    """
    Replace placeholder text in a specific slide by index.

    :param presentation_id: The ID of the Google Slides presentation.
    :param slide_index: The index of the slide (0 for the first slide, 1 for the second, etc.).
    :param replacements: A dictionary where the keys are placeholders and the values are the replacement text.
    """
    # Fetch the presentation and get all the slides
    presentation = slides_service.presentations().get(presentationId=presentation_id).execute()
    slides = presentation.get('slides')

    # Get the slide by index
    target_slide = slides[slide_index]
    slide_id = target_slide.get('objectId')

    # List to store all replacement requests
    requests = []

    # Iterate over all shapes in the slide and replace text based on the dictionary
    for element in target_slide.get('pageElements'):
        shape = element.get('shape')
        if shape:
            text_content = shape.get('text')
            if text_content:
                for text_element in text_content.get('textElements', []):
                    for placeholder, replacement in replacements.items():
                        if 'textRun' in text_element and placeholder in text_element['textRun']['content']:
                            # Prepare a replaceAllText request for each placeholder-replacement pair
                            requests.append({
                                'replaceAllText': {
                                    'containsText': {
                                        'text': placeholder,
                                        'matchCase': True
                                    },
                                    'replaceText': replacement,
                                    'pageObjectIds': [slide_id]  # Apply only to this slide
                                }
                            })

    # If there are requests to process, send them in a batch update
    if requests:
        body = {'requests': requests}
        response = slides_service.presentations().batchUpdate(presentationId=presentation_id, body=body).execute()
        print(f"Replaced text in slide index {slide_index}")
    else:
        print(f"No placeholders found in the slide.")


def insert_image_on_slide(presentation_id, image_url, slide_index, x_pos, y_pos, width, height):
    """
    Insert an image from a URL on a specific slide at a given position.

    :param presentation_id: The ID of the Google Slides presentation.
    :param image_url: The URL of the image to be inserted.
    :param slide_index: The index of the slide where the image will be placed.
    :param x_pos: The X-coordinate for the image's position (in EMUs).
    :param y_pos: The Y-coordinate for the image's position (in EMUs).
    :param width: The width of the image (in EMUs).
    :param height: The height of the image (in EMUs).
    """
    # Fetch the presentation and get all the slides
    presentation = slides_service.presentations().get(presentationId=presentation_id).execute()
    slides = presentation.get('slides')

    # Ensure the slide index is within range
    if slide_index >= len(slides):
        print(f"Slide index {slide_index} is out of range.")
        return

    # Get the slide by index
    slide_id = slides[slide_index].get('objectId')

    # Prepare the image insert request
    image_request = {
        'createImage': {
            'url': image_url,
            'elementProperties': {
                'pageObjectId': slide_id,  # Slide where the image will be placed
                'size': {
                    'height': {'magnitude': height, 'unit': 'EMU'},  # Image height in EMUs
                    'width': {'magnitude': width, 'unit': 'EMU'},  # Image width in EMUs
                },
                'transform': {
                    'scaleX': 1,
                    'scaleY': 1,
                    'translateX': x_pos,  # X position in EMUs
                    'translateY': y_pos,  # Y position in EMUs
                    'unit': 'EMU'
                }
            }
        }
    }

    # Execute the request
    body = {'requests': [image_request]}
    response = slides_service.presentations().batchUpdate(presentationId=presentation_id, body=body).execute()
    print(f"Inserted image on slide index {slide_index} at position ({x_pos}, {y_pos}) with size ({width}x{height}).")


def delete_slide_by_index(presentation_id, slide_index):
    """
    Delete a slide from a Google Slides presentation based on the slide index.

    :param presentation_id: The ID of the Google Slides presentation.
    :param slide_index: The index of the slide to delete (0 for the first slide, 1 for the second slide, etc.).
    """
    # Fetch the presentation and get all the slides
    presentation = slides_service.presentations().get(presentationId=presentation_id).execute()
    slides = presentation.get('slides')

    # Get the slide by index
    slide_id = slides[slide_index].get('objectId')

    # Create the deleteObject request to delete the slide
    delete_request = {
        'deleteObject': {
            'objectId': slide_id
        }
    }

    # Execute the request to delete the slide
    body = {'requests': [delete_request]}
    slides_service.presentations().batchUpdate(presentationId=presentation_id, body=body).execute()

    print(f"Deleted slide index {slide_index} with ID {slide_id}.")


if __name__ == '__main__':
    # Your Google Slides presentation ID
    template_id = '1W3825bDDk5_lau86Xun7IydoYLOnOFz4Q4jHeEwV4Zo'

    # The folder ID where the copy should be saved
    folder_id = '10PRyhKFVsn4osl74KD6uUjkpnirna0Va'

    # Create a copy of the original presentation
    copy_title = 'Copy of My Google Slides Presentation'
    presentation_id = make_copy_of_presentation(template_id, copy_title, folder_id)

    print(f"Copied presentation ID: {presentation_id}")

    # Wait a few seconds for the copy to be fully available (optional but sometimes useful)
    time.sleep(2)

    # Slide 0 replacements
    replacements_slide_0 = {
        "{p1}": "This is the new text for placeholder 1",
        "{p2}": "This is the new text for placeholder 2"
    }

    # Slide 1 replacements
    replacements_slide_1 = {
        "{p3}": "Updated text for placeholder 3",
        "{p4}": "Updated text for placeholder 4"
    }

    # Call the function for the first slide (index 0)
    replace_text_in_slide_by_index(presentation_id, slide_index=0, replacements=replacements_slide_0)

    # Call the function for the second slide (index 1)
    replace_text_in_slide_by_index(presentation_id, slide_index=1, replacements=replacements_slide_1)

    # Image URL to be inserted
    image_url = 'https://logo.clearbit.com/apple.com'

    # Slide index where the image will be inserted (e.g., 0 for the first slide)
    slide_index = 0

    # Image position and size (in EMUs)
    x_pos = 1000000  # 1 inch from the left
    y_pos = 1000000  # 1 inch from the top
    width = 3000000  # 3 inches wide
    height = 3000000  # 3 inches high

    # Insert the image
    insert_image_on_slide(presentation_id, image_url, slide_index, x_pos, y_pos, width, height)



