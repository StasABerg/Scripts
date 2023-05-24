import requests
import re
import base64
import hashlib
import os.path
import binascii
from io import BytesIO
from PIL import Image
import csv

# Define the path to the credentials file
credentials_file = r'credentials.csv'

# Initialize an empty list to store the credentials
credentials = []

# Read the credentials from the CSV file
with open(credentials_file, 'r', encoding='utf-8-sig') as file:
    reader = csv.DictReader(file)
    for row in reader:
        credentials.append(row)

# Process each set of credentials
for creds in credentials:
    site_url = f'https://{creds["domain"]}'
    username = 'administratoraccount'
    password = creds["password"]
    auth = (username, password)

    def get_all_posts():
        page = 1
        all_posts = []
        
        # Retrieve posts from the WordPress REST API in batches of 100
        while True:
            response = requests.get(f'{site_url}/wp-json/wp/v2/posts?_fields=id&per_page=100&page={page}', auth=auth)
            print(f'Starting {site_url}')
            
            # Check if the response was successful
            if response.status_code != 200:
                print('Error retrieving posts:', response.text)
                break

            # Extract the posts from the response
            posts = response.json()
            
            # Check if there are no more posts
            if not posts:
                break

            all_posts.extend(posts)
            
            # Retrieve the total number of pages
            total_pages = int(response.headers.get('X-WP-TotalPages', '0'))
            
            # Check if we have reached the last page
            if page >= total_pages:
                break

            page += 1

        return all_posts

    # Get all posts for the current site
    post_data = get_all_posts()

    # Loop through posts and find base64 images
    for post in post_data:
        post_id = post['id']
        print(f'Start processing post ID: {post_id}')
        
        # Retrieve the individual post data
        response = requests.get(f'{site_url}/wp-json/wp/v2/posts/{post_id}', auth=auth)
        
        # Check if the response was successful
        if response.status_code != 200:
            print('Error retrieving post:', response.text)
            continue

        post_data = response.json()
        post_content = post_data['content']['rendered']
        
        # Find all base64 images in the post content
        matches = re.findall(r'src="data:image/([^;]+);base64,([^"]+)"', post_content)

        # Initialize a variable to store the ID of the first image attachment
        first_image_attachment_id = None
                # Process each base64 image match
        for match in matches:
            image_type, image_data = match
            image_data = image_data.replace(' ', '+')
            
            try:
                image_data = base64.b64decode(image_data)
            except binascii.Error:
                print(f'Invalid base64 data for post ID: {post_id}. Base64 data: {image_data[:50]}...')
                continue

            if len(image_data) < 10 or image_data[:2] not in (b'\xff\xd8', b'\x89P', b'BM', b'GIF'):
                print(f'Invalid image data for post ID: {post_id}. Image data: {image_data[:10]}...')
                continue
            try:
                # Open the image using PIL
                image = Image.open(BytesIO(image_data))
                
                # Convert indexed or transparent images to RGB
                if image.mode == 'P' or image.mode == 'RGBA':
                    image = image.convert('RGB')
            except OSError:
                print(f'Error opening image for post ID: {post_id}. Base64 data: {image_data[:50]}...')
                continue

            # Calculate the MD5 hash of the image data
            image_hash = hashlib.md5(image_data).hexdigest()
            
            # Generate a filename for the image based on its hash and type
            filename = f'{image_hash}.{image_type}'
            
            # Save the image locally
            temp_file = os.path.join('C:\\temp', filename)
            image.save(temp_file)

            try:
                with open(temp_file, 'rb') as f:
                    # Create a dictionary to hold the file data
                    files = {'file': (filename, f, f'image/{image_type}')}
                    
                    # Upload the image to WordPress media library
                    response = requests.post(f'{site_url}/wp-json/wp/v2/media', files=files, auth=auth)
                    response.raise_for_status()
                    media_data = response.json()
                    
                    # Check if there are any errors in the response
                    if 'errors' in media_data:
                        print('Error uploading image:', media_data['errors'])
                        continue
                    
                    # Retrieve the attachment ID of the uploaded image
                    attachment_id = response.json()['id']

                    # Set the first image attachment ID if not already set
                    if first_image_attachment_id is None:
                        first_image_attachment_id = attachment_id

                    # Replace the base64 image with the URL of the uploaded image
                    new_url = media_data['source_url']
                    base64_str = match[1]
                    old_src = f'data:image/{image_type};base64,{base64_str}'
                    post_content = post_content.replace(old_src, new_url)

            except requests.exceptions.HTTPError as err:
                print('Error uploading image:', response.text)
                print(f'Response body: {response.content}')
                continue

            # Update the post content with the modified image URLs
            post_data['content'] = post_content
            
            # Update the post with the modified content
            response = requests.post(f'{site_url}/wp-json/wp/v2/posts/{post_id}', json=post_data, auth=auth)
            
            # Check if the post update was successful
            if response.status_code != 200:
                print('Error updating post:', response.text)
                continue

            print(f'Post {post_id} updated with new image URL')

            # Set the first image attachment as the featured media for the post
            if first_image_attachment_id is not None:
                post_data['featured_media'] = first_image_attachment_id
                
                # Update the post with the featured media
                response = requests.post(f'{site_url}/wp-json/wp/v2/posts/{post_id}', json=post_data, auth=auth)
                
                # Check if the post update was successful
                if response.status_code != 200:
                    print('Error updating post:', response.text)
                    continue

                print(f'Post {post_id} updated with new featured image')
            else:
                print(f'No valid base64 images found for post ID: {post_id}')

            # Remove the temporary image file
            os.remove(temp_file)
            print(f'Finished processing post ID: {post_id}')
