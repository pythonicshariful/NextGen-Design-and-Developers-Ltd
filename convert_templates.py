"""
convert_templates.py
Convert static HTML files to Jinja2 templates for Flask.
Injects dynamic variables for SEO meta, analytics, logo, site name, etc.
Run once: python convert_templates.py
"""
import os
import re
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')
os.makedirs(TEMPLATES_DIR, exist_ok=True)

PAGES = [
    ('index.html',                'home'),
    ('about.html',                'about'),
    ('properties.html',           'properties'),
    ('landowner.html',            'landowner'),
    ('construction-status.html',  'construction-status'),
    ('referral-program.html',     'referral-program'),
    ('nrb.html',                  'nrb'),
    ('contact.html',              'contact'),
]

# Analytics block injected before </head>
ANALYTICS_BLOCK = """\n{%- if settings.ga4_tracking_id %}
<!-- Google Analytics 4 -->
<script async src="https://www.googletagmanager.com/gtag/js?id={{ settings.ga4_tracking_id }}"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', '{{ settings.ga4_tracking_id }}');
</script>
{%- endif %}
{%- if settings.fb_pixel_id %}
<!-- Facebook Pixel -->
<script>
  !function(f,b,e,v,n,t,s){if(f.fbq)return;n=f.fbq=function(){n.callMethod?
  n.callMethod.apply(n,arguments):n.queue.push(arguments)};if(!f._fbq)f._fbq=n;
  n.push=n;n.loaded=!0;n.version='2.0';n.queue=[];t=b.createElement(e);t.async=!0;
  t.src=v;s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s)}(window,
  document,'script','https://connect.facebook.net/en_US/fbevents.js');
  fbq('init','{{ settings.fb_pixel_id }}');
  fbq('track','PageView');
</script>
{%- endif %}\n"""

def convert(html_file, page_slug):
    src = os.path.join(BASE_DIR, html_file)
    dst = os.path.join(TEMPLATES_DIR, html_file)

    if not os.path.exists(src):
        print(f'[SKIP] {html_file} not found')
        return

    with open(src, 'r', encoding='utf-8') as f:
        content = f.read()

    # ── 1. Prepend Jinja2 page_slug variable ─────────────────────────────────
    header = f'{{% set page_slug = "{page_slug}" %}}\n'
    content = header + content

    # ── 2. <title> ────────────────────────────────────────────────────────────
    content = re.sub(
        r'<title>[^<]*</title>',
        '<title>{{ seo.title or settings.get("site_name", "") }}</title>',
        content, count=1
    )

    # ── 3. Meta description ───────────────────────────────────────────────────
    content = re.sub(
        r'<meta\s+name=["\']description["\']\s+content="[^"]*"\s*/>',
        '<meta name="description" content="{{ seo.description or \'\' }}"/>',
        content, count=1
    )

    # ── 4. OG title ───────────────────────────────────────────────────────────
    content = re.sub(
        r'<meta\s+property=["\']og:title["\']\s+content="[^"]*"\s*/>',
        '<meta property="og:title" content="{{ seo.og_title or seo.title or settings.get(\'site_name\',\'\') }}" />',
        content, count=1
    )

    # ── 5. OG description ─────────────────────────────────────────────────────
    content = re.sub(
        r'<meta\s+property=["\']og:description["\']\s+content="[^"]*"\s*/>',
        '<meta property="og:description" content="{{ seo.og_description or seo.description or \'\' }}" />',
        content, count=1
    )

    # ── 6. Twitter title ──────────────────────────────────────────────────────
    content = re.sub(
        r'<meta\s+name=["\']twitter:title["\']\s+content="[^"]*"\s*/>',
        '<meta name="twitter:title" content="{{ seo.og_title or seo.title or settings.get(\'site_name\',\'\') }}" />',
        content, count=1
    )

    # ── 7. Twitter description ────────────────────────────────────────────────
    content = re.sub(
        r'<meta\s+name=["\']twitter:description["\']\s+content="[^"]*"\s*/>',
        '<meta name="twitter:description" content="{{ seo.og_description or seo.description or \'\' }}" />',
        content, count=1
    )

    # ── 8. Favicon ────────────────────────────────────────────────────────────
    content = re.sub(
        r'(<link[^>]+rel=["\']icon["\'][^>]+href=["\'])([^"\']+)(["\'])',
        r'\1{{ settings.get("favicon_url", "/assets/images/fav.png") }}\3',
        content, count=1
    )

    # ── 9. Remove existing GA/GTM scripts (we'll inject ours) ─────────────────
    content = re.sub(
        r'<!--\s*Google Tag Manager.*?-->.*?<!--\s*/\s*Google Tag Manager\s*-->',
        '', content, flags=re.DOTALL
    )
    content = re.sub(
        r'<script[^>]*googletagmanager\.com/gtag[^>]*>.*?</script>',
        '', content, flags=re.DOTALL
    )
    content = re.sub(
        r'<script[^>]*>\s*window\.dataLayer.*?gtag\(\'config\'[^;]+;\s*</script>',
        '', content, flags=re.DOTALL
    )

    # ── 10. Inject analytics before </head> ───────────────────────────────────
    content = content.replace('</head>', ANALYTICS_BLOCK + '</head>', 1)

    # ── 11. Logo image src ────────────────────────────────────────────────────
    # Replace logo img src inside header (bti-logo, site-logo common class names)
    content = re.sub(
        r'(<img[^>]+(?:class=["\'][^"\']*(?:logo|site-logo|bti-logo|brand-logo)[^"\']*["\'])[^>]+src=["\'])([^"\']+)(["\'])',
        r'\1{{ settings.get("logo_url", "/assets/images/logo.svg") }}\3',
        content, count=2
    )
    # Also catch logos by common src patterns
    content = re.sub(
        r'(<img[^>]+src=["\'][^"\']*(?:logo[^"\']*\.(?:svg|png|webp))["\'][^>]*>)',
        lambda m: re.sub(r'src=["\'][^"\']+["\']',
                         'src="{{ settings.get(\'logo_url\', \'/assets/images/logo.svg\') }}"', m.group(0)),
        content, count=3
    )

    # ── 12. Navigation links — convert .html hrefs to Flask url_for ───────────
    url_map = {
        'href="index.html"':                "href=\"{{ url_for('index') }}\"",
        "href='index.html'":                "href=\"{{ url_for('index') }}\"",
        'href="about.html"':                "href=\"{{ url_for('about') }}\"",
        "href='about.html'":                "href=\"{{ url_for('about') }}\"",
        'href="properties.html"':           "href=\"{{ url_for('properties') }}\"",
        "href='properties.html'":           "href=\"{{ url_for('properties') }}\"",
        'href="landowner.html"':            "href=\"{{ url_for('landowner') }}\"",
        "href='landowner.html'":            "href=\"{{ url_for('landowner') }}\"",
        'href="construction-status.html"':  "href=\"{{ url_for('construction_status') }}\"",
        "href='construction-status.html'":  "href=\"{{ url_for('construction_status') }}\"",
        'href="referral-program.html"':     "href=\"{{ url_for('referral_program') }}\"",
        "href='referral-program.html'":     "href=\"{{ url_for('referral_program') }}\"",
        'href="nrb.html"':                  "href=\"{{ url_for('nrb') }}\"",
        "href='nrb.html'":                  "href=\"{{ url_for('nrb') }}\"",
        'href="contact.html"':              "href=\"{{ url_for('contact') }}\"",
        "href='contact.html'":              "href=\"{{ url_for('contact') }}\"",
    }
    for old, new in url_map.items():
        content = content.replace(old, new)

    # ── 13. Write output ──────────────────────────────────────────────────────
    with open(dst, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f'[OK] {html_file} -> templates/{html_file}')


if __name__ == '__main__':
    print('Converting HTML files to Jinja2 templates...\n')
    for html_file, slug in PAGES:
        convert(html_file, slug)
    print('\nDone! Templates are in the templates/ directory.')
    print('Run the app with: python app.py')
