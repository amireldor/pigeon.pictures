import boto3
import logging
import json
import hashlib
import os
import random
from botocore.exceptions import ClientError

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize S3 client
s3_client = boto3.client('s3')

# Constants - these should be configured according to your needs
BUCKET_NAME = 'pigeon.pictures'
WWWROOT = 'wwwroot'  # Root directory for web contentTEMPLATE_KEY = 'template.html'  # Placeholder - replace with actual template key
OUTPUT_KEY = 'index.html'      # Placeholder - replace with actual output key
IMAGES_DIR = 'pigeons'  # Directory in S3 where images will be stored

# Pixabay API configuration
PIXABAY_API_KEY = os.environ.get('PIXABAY_API_KEY')
if not PIXABAY_API_KEY:
    raise ValueError("PIXABAY_API_KEY environment variable is not set")
    
PIXABAY_API_URL = 'https://pixabay.com/api/'
PIXABAY_QUERY = 'pigeon'
PIXABAY_PER_PAGE = 20  # Number of images to fetch

# Image download configuration
IMAGE_QUALITY = 'large'  # Options: 'web' for 640px max, 'large' for full size


def replace_placeholders(template_content, replacements):
    """
    Replace placeholders in the template content with actual values.
    
    Args:
        template_content (str): The template content to modify
        replacements (dict): Dictionary of placeholder -> replacement value mappings
        
    Returns:
        str: Modified content with placeholders replaced
    """
    try:
        for placeholder, value in replacements.items():
            template_content = template_content.replace(placeholder, value)
        return template_content
    except Exception as e:
        logger.error(f"Error replacing placeholders: {str(e)}")
        raise

def download_image(url, image_id):
    """
    Download an image and save it to S3 with a unique hash.
    
    Args:
        url (str): URL of the image to download
        image_id (int): Unique identifier for the image
        
    Returns:
        str: S3 key where the image was saved
    """
    try:
        # Generate a unique hash for the image
        hash_object = hashlib.sha256()
        hash_object.update(str(image_id).encode())
        hash_object.update(url.encode())
        image_hash = hash_object.hexdigest()[:12]  # Use first 12 chars of hash
        
        # Download the image
        response = requests.get(url)
        response.raise_for_status()
        
        # Save to S3 with wwwroot prefix
        s3_key = f"{WWWROOT}/{IMAGES_DIR}/{image_hash}.jpg"
        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=s3_key,
            Body=response.content,
            ContentType='image/jpeg'
        )
        
        logger.info(f"Successfully downloaded and saved image {image_id} to {s3_key}")
        return s3_key
        
    except Exception as e:
        logger.error(f"Error downloading image {image_id} from {url}: {str(e)}")
        raise

def fetch_pigeon_images():
    """
    Fetch pigeon images from Pixabay API and download them to S3.
    
    Returns:
        list: List of image dictionaries containing image URLs and other metadata
    """
    try:
        # Randomize page number between 1-20 to get different images each time
        random_page = random.randint(1, 20)
        
        params = {
            'key': PIXABAY_API_KEY,
            'q': PIXABAY_QUERY,
            'per_page': PIXABAY_PER_PAGE,
            'image_type': 'photo',
            'page': random_page
        }
        
        response = requests.get(PIXABAY_API_URL, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Get hits and shuffle them for more randomness
        hits = data.get('hits', []).copy()
        random.shuffle(hits)
        
        # Extract and download images
        images = []
        for hit in hits:
            # Choose which URL to download based on IMAGE_QUALITY
            download_url = hit.get('largeImageURL') if IMAGE_QUALITY == 'large' else hit.get('webformatURL')
            
            # Download the image to S3
            s3_key = download_image(download_url, hit.get('id'))
            
            # Store image information with S3 key and filename
            filename = os.path.basename(s3_key)  # Extract just the filename part
            image_data = {
                's3_key': s3_key,
                'filename': filename,  # Add the filename for easy reference
                'title': hit.get('tags'),
                'user': hit.get('user'),
                'user_url': hit.get('userImageURL'),
                'views': hit.get('views'),
                'downloads': hit.get('downloads'),
                'likes': hit.get('likes'),
                'comments': hit.get('comments')
            }
            images.append(image_data)
        
        return images
        
    except Exception as e:
        logger.error(f"Error fetching images from Pixabay: {str(e)}")
        raise

def lambda_handler(event, context):
    """
    AWS Lambda handler function that reads a template file from S3,
    replaces placeholders, and writes the result back to S3.
    """
    try:
        # Read template file from S3
        response = s3_client.get_object(Bucket=BUCKET_NAME, Key=TEMPLATE_KEY)
        template_content = response['Body'].read().decode('utf-8')
        
        logger.info(f"Successfully read template from {TEMPLATE_KEY}")
        
        # Fetch pigeon images
        images = fetch_pigeon_images()
        
        # Create replacements for each pigeon placeholder
        replacements = {}
        
        # Add individual image replacements for each placeholder (0-indexed)
        for i, image in enumerate(images[:20]):  # Limit to 20 images
            placeholder = f"$$$PIGEON_PLACEHOLDER_{i}$$$"  # 0-based index
            # Use just the filename for the image
            replacements[placeholder] = image['filename']
        
        # Replace placeholders
        modified_content = replace_placeholders(template_content, replacements)
        
        # Write modified content back to S3
        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=OUTPUT_KEY,
            Body=modified_content.encode('utf-8'),
            ContentType='text/html'
        )
        
        logger.info(f"Successfully wrote modified content to {OUTPUT_KEY}")
        
        return {
            'statusCode': 200,
            'body': 'Template processing completed successfully'
        }
        
    except ClientError as e:
        logger.error(f"S3 operation failed: {str(e)}")
        return {
            'statusCode': 500,
            'body': f'S3 operation failed: {str(e)}'
        }
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return {
            'statusCode': 500,
            'body': f'Unexpected error: {str(e)}'
        }
