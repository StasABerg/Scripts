import requests
import re
import base64
import hashlib
import os.path
import binascii
from io import BytesIO
from PIL import Image

site_url = 'https://sitename.tld'
username = 'username'
password = 'password'

auth = (username, password)


#retrieve all posts
def get_all_posts():
    page = 1
    all_posts = []
    while True:
        response = requests.get(f'{site_url}/wp-json/wp/v2/posts?_fields=id&per_page=100&page={page}', auth=auth)

        if response.status_code != 200:
            print('Error retrieving posts:', response.text)
            break

        posts = response.json()
        if not posts:
            break

        all_posts.extend(posts)
        total_pages = int(response.headers.get('X-WP-TotalPages', '0'))
        if page >= total_pages:
            break

        page += 1

    return all_posts


post_data = get_all_posts()

# loop through posts and find base64
for post in post_data:
    post_id = post['id']
    print(f'Start processing post ID: {post_id}')
    response = requests.get(f'{site_url}/wp-json/wp/v2/posts/{post_id}', auth=auth)
    if response.status_code != 200:
        print('Error retrieving post:', response.text)
        continue

    post_data = response.json()
    post_content = post_data['content']['rendered']
    matches = re.findall(r'src="data:image/([^;]+);base64,([^"]+)"', post_content)
    first_image_attachment_id = None  #default none for featured image

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
        #special cases for patterned and rgba images
        try:
            image = Image.open(BytesIO(image_data))
            if image.mode == 'P':
                image = image.convert('RGB')
            elif image.mode == 'RGBA':
                image = image.convert('RGB')
        except OSError:
            print(f'Error opening image for post ID: {post_id}. Base64 data: {image_data[:50]}...')
            continue
        #make md5has filename
        image_hash = hashlib.md5(image_data).hexdigest()
        filename = f'{image_hash}.{image_type}'
        temp_file = os.path.join('C:\\temp', filename)  # save image locally
        image.save(temp_file)
        #upload to wordpress library
        try:
            with open(temp_file, 'rb') as f:
                files = {'file': (filename, f, f'image/{image_type}')}
                response = requests.post(f'{site_url}/wp-json/wp/v2/media',
                                         files=files,
                                         auth=auth)
                response.raise_for_status()
                media_data = response.json()
                if 'errors' in media_data:
                    print('Error uploading image:', media_data['errors'])
                    continue
                attachment_id = response.json()['id']
                # if first image, store attachment id for the featured image
                if first_image_attachment_id is None:
                    first_image_attachment_id = attachment_id
                # replace old url with new url
                new_url = media_data['source_url']
                base64_str = match[1]
                old_src = f'data:image/{image_type};base64,{base64_str}'
                post_content = post_content.replace(old_src, new_url)

        except requests.exceptions.HTTPError as err:
            print('Error uploading image:', response.text)
            print(f'Response body: {response.content}')
            continue

        
        #update the post
        post_data['content'] = post_content
        response = requests.post(f'{site_url}/wp-json/wp/v2/posts/{post_id}',
                                 json=post_data,
                                 auth=auth)
        if response.status_code != 200:
            print('Error updating post:', response.text)
            continue

        print(f'Post {post_id} updated with new image URL')
           # update featured image with the first image
        if first_image_attachment_id is not None:
            post_data['featured_media'] = first_image_attachment_id
            response = requests.post(f'{site_url}/wp-json/wp/v2/posts/{post_id}',
                                     json=post_data,
                                     auth=auth)
            if response.status_code != 200:
                print('Error updating post:', response.text)
                continue

            print(f'Post {post_id} updated with new featured image')

        else:
            print(f'No valid base64 images found for post ID: {post_id}')
        
        os.remove(temp_file)
        print(f'Finished processing post ID: {post_id}')
