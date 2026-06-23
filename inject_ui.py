import os
import re

head_injection = '''
    <!-- AOS & Custom UI -->
    <link href="https://unpkg.com/aos@2.3.1/dist/aos.css" rel="stylesheet">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/custom-ui.css') }}">
'''

body_injection = '''
    <!-- AOS Init -->
    <script src="https://unpkg.com/aos@2.3.1/dist/aos.js"></script>
    <script>
      AOS.init({
        duration: 800,
        easing: 'ease-in-out',
        once: true,
        mirror: false
      });
    </script>
'''

templates_dir = 'templates'
files = [f for f in os.listdir(templates_dir) if f.endswith('.html')]

for filename in files:
    filepath = os.path.join(templates_dir, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Inject Head CSS
    if 'custom-ui.css' not in content:
        content = re.sub(r'(</head>)', r'%s\n\1' % head_injection.replace('\\', '\\\\'), content, flags=re.IGNORECASE)

    # 2. Inject Body JS
    if 'AOS.init' not in content:
        content = re.sub(r'(</body>)', r'%s\n\1' % body_injection.replace('\\', '\\\\'), content, flags=re.IGNORECASE)

    # 3. Add AOS to Section Titles
    content = re.sub(r'class="(sec-title[^"]*)"', r'class="\1" data-aos="fade-up"', content)
    content = re.sub(r'class="(sub-title[^"]*)"', r'class="\1" data-aos="fade-up" data-aos-delay="100"', content)

    # 4. Add AOS to property cards (that aren't dynamically looped, though we fixed index.html, we might have others)
    # Actually, we can add it directly to the loop in index.html later. Let's do a basic replace for static ones if any:
    content = re.sub(r'class="(property-card4[^"]*)"(?!.*data-aos)', r'class="\1" data-aos="fade-up" data-aos-delay="150"', content)

    # 5. Add AOS to Hero sliders
    content = re.sub(r'class="(hero-title[^"]*)"', r'class="\1" data-aos="zoom-in" data-aos-duration="1000"', content)
    content = re.sub(r'class="(hero-text[^"]*)"', r'class="\1" data-aos="fade-up" data-aos-delay="200"', content)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

print("Injected AOS and Custom CSS to all templates.")
