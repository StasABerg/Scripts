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

#loop through posts and find base64
for post in post_data:
    post_id = post['id']
    print(f'Start processing post ID: {post_id}')  # Add this line
    response = requests.get(f'{site_url}/wp-json/wp/v2/posts/{post_id}', auth=auth)
    if response.status_code != 200:
        print('Error retrieving post:', response.text)
        continue

    post_data = response.json()
    post_content = post_data['content']['rendered']
    matches = re.findall(r'src="data:image/([^;]+);base64,([^"]+)"', post_content)

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
            image = Image.open(BytesIO(image_data))
            if image.mode == 'P':
                image = image.convert('RGB')
            elif image.mode == 'RGBA':
                image = image.convert('RGB')
        except OSError:
            print(f'Error opening image for post ID: {post_id}. Base64 data: {image_data[:50]}...')
            continue

        image_hash = hashlib.md5(image_data).hexdigest()
        filename = f'{image_hash}.{image_type}'
        temp_file = os.path.join('C:\\temp', filename) #save image locally
        image.save(temp_file)
        #upload to media
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

                new_url = media_data['source_url']
                base64_str = match[1]
                old_src = f'data:image/{image_type};base64,{base64_str}'
                post_content = post_content.replace(old_src, new_url)

        except requests.exceptions.HTTPError as err:
            print('Error uploading image:', response.text)
            print(f'Response body: {response.content}')
            continue

            #update base64 url to imagefile url
        post_data['content'] = post_content
        response = requests.post(f'{site_url}/wp-json/wp/v2/posts/{post_id}',
                                 json=post_data,
                                 auth=auth)
        if response.status_code != 200:
            print('Error updating post:', response.text)
            continue

        print(f'Post {post_id} updated with new image URL')

        # remove files locally
        os.remove(temp_file)
    #get post id for featured images
    response = requests.get(f'{site_url}/wp-json/wp/v2/posts/{post_id}', auth=auth)
    post_data = response.json()

    #check if the post already has a featured image
    if 'featured_media' in post_data and post_data['featured_media']:
        print(f'Post {post_id} already has a featured image')
        continue

    #make 1st pic featured or that starts with http
    for match in re.finditer(r'<img\s.*?src="(.*?)".*?>', post_content):
        image_url = match.group(1)
        if image_url.startswith('data:'):
            continue
        if not image_url.startswith('http'):
            continue
        try:
            with requests.get(image_url, stream=True) as r:
                r.raise_for_status()
                response = requests.post(f'{site_url}/wp-json/wp/v2/media',
                                         files={'file': ('image.jpg', r.raw, 'image/jpeg')},
                                         auth=auth)
                response.raise_for_status()
                media_data = response.json()
                attachment_id = media_data['id']
                post_data['featured_media'] = attachment_id
                response = requests.post(f'{site_url}/wp-json/wp/v2/posts/{post_id}',
                                         json=post_data,
                                         auth=auth)
                response.raise_for_status()
                print(f'Post {post_id} updated with new featured image')
                break
        except requests.exceptions.HTTPError as err:
            print(f'Error updating featured image for post ID: {post_id}:', err.response.text)
            break
        except Exception as err:
            print(f'Error updating featured image for post ID: {post_id}:', str(err))
            break

    if 'featured_media' not in post_data or not post_data['featured_media']:
        print(f'No image found for post ID: {post_id}')

    print(f'Finished processing post ID: {post_id}')  
