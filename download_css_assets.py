import re
import urllib.request
import os

css_path = 'assets/css/theme-main.css'
with open(css_path, 'r', encoding='utf-8-sig') as f:
    content = f.read()

# Find all occurrences of url(...)
urls = re.findall(r'url\(([^)]+)\)', content)

# Unique set of URLs to download
unique_urls = set()
for u in urls:
    # Strip quotes
    u = u.strip('"\'')
    if u.startswith('data:'):
        continue
    unique_urls.add(u)

print(f"Found {len(unique_urls)} unique URLs in CSS to process.")

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

for original_url in unique_urls:
    # Resolve the original absolute live URL
    if original_url.startswith('http'):
        live_url = original_url
    else:
        # e.g., ../../../../../../../../themes/bti/assets/img/property-card1-img-mask.png
        # Clean relative paths to get theme path
        clean_path = original_url.replace('../', '').replace('themes/bti/', '')
        live_url = f"https://btibd.com/wp-content/themes/bti/{clean_path}"
    
    filename = live_url.split('/')[-1].split('?')[0]
    local_path = os.path.join('assets', 'images', filename)
    
    print(f"Downloading {live_url} -> {local_path}...")
    try:
        req = urllib.request.Request(live_url, headers=headers)
        with urllib.request.urlopen(req) as resp:
            data = resp.read()
            with open(local_path, 'wb') as lf:
                lf.write(data)
        
        # Replace in CSS (relative to assets/css/theme-main.css, so it should be ../images/<filename>)
        content = content.replace(original_url, f"../images/{filename}")
        print(f"Successfully replaced in CSS: {filename}")
    except Exception as e:
        print(f"Failed to download {live_url}: {e}")

# Save the updated CSS file
with open(css_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("All CSS assets processed!")
