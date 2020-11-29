import json
import os
import time
import urllib.parse
import requests

file = open('settings.json', 'r')
raw = file.read()
file.close()
settings = json.loads(raw)

# Check validity of settings array
if 'book' not in settings or 'pages' not in settings:
    print('Settings are malformed. Exiting')
    exit(1)

# Load settings
label = settings['label']
book = settings['book']
page_count = settings['pageCount']
pages = settings['pages']
base_uri = 'https://invenio.bundesarchiv.de'
djatoka_uri = settings['djatokaUri']
record = label.replace('/', '-')

# Load cookie
with open('cookie', 'r') as file:
    cookies = {'JSESSIONID': file.read().replace('"', '').split(';')[0].split('=')[1]}

# Define scraping range
print('Scraping %s (%s) with %d pages' % (label, book, page_count))
start_page = int(input('Specify start page (default 1)') or "1")
end_page = int(input('Specify end page (default %s)' % page_count) or str(page_count))

if not os.path.exists(record):
    os.makedirs(record)

# Iterate over all pages
for page in pages:
    page_no = int(page['page'])
    label = page['label'].replace('/', '-')
    uri = page['uri']

    # Start page not reached, skip
    if page_no < start_page:
        continue

    # End page reached, break
    if page_no > end_page:
        break

    # Construct download URI
    uri = urllib.parse.quote_plus(uri)

    params = {
        'url_ver': 'Z39.88-2004',
        'svc_id': 'info:lanl-repo/svc/getRegion',
        'svc_val_fmt': 'info:ofi/fmt:kev:mtx:jpeg2000',
        'svc.format': 'image/jpeg',
        'svc.level': '5',
        'svc.rotate': '0'
    }

    p2 = urllib.parse.urlencode(params)

    params = '&url_ver=Z39.88-2004&svc_id=info%3Alanl-repo%2Fsvc%2FgetRegion' \
             '&svc_val_fmt=info%3Aofi%2Ffmt%3Akev%3Amtx%3Ajpeg2000&svc.format=image%2Fjpeg&svc.level=5&svc.rotate=0'
    download_uri = base_uri + djatoka_uri + '/resolver?rft_id=' + uri + '&' + p2

    print(params)
    print(p2)

    # Download
    print('Processing page %d' % page_no)
    response = requests.get(download_uri, cookies=cookies)
    if response.status_code == 200:
        file_name = record + os.path.sep + label + '.jpg'
        with open(file_name, 'wb') as handler:
            handler.write(response.content)
    elif response.status_code == 403:
        print('Reel ' + record + ', Incorrect or expired URI!')
    else:
        print('Reel ' + record + ', Unknown connection error')
    time.sleep(.5)
