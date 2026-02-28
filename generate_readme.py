import re
import json

with open('order-of-mass.html', 'r', encoding='utf-8') as f:
    html = f.read()

with open('bible.json', 'r', encoding='utf-8') as f:
    bible = json.load(f)

# Find all headings to map lines to sections
headings = []
for m in re.finditer(r'<h[123][^>]*>(.*?)</h[123]>', html):
    title = re.sub(r'<[^>]*>', '', m.group(1)).strip()
    headings.append((m.start(), title))

# Extract the mass text and the references
all_refs = []

# To get the exact missal text, let's find the innermost div or element containing the footnote-ref
# The footnote ref looks like: <span class="footnote-ref" data-ref="refId">...</span>
# It is usually inside a <div class="v">...</div> or similar.
for m in re.finditer(r'<div[^>]*>(.*?)<span class="footnote-ref" data-ref="([^"]+)"[^>]*>.*?</span>(.*?)</div>', html, flags=re.DOTALL):
    start_pos = m.start()
    before_span = m.group(1)
    ref_id = m.group(2)
    after_span = m.group(3)
    
    # Strip HTML from the surrounding text to get just the Missal text
    missal_text = re.sub(r'<[^>]*>', '', before_span + after_span)
    # Clean up whitespace and entities
    missal_text = re.sub(r'\s+', ' ', missal_text).strip()
    missal_text = missal_text.replace('&#8217;', "'").replace('&rarr;', '->').replace('&#10016;', '+')
    
    # Exclude cases where the div captured too much
    if len(missal_text) > 300:
        # Fallback to something shorter if the regex matched greedily over many divs
        # A safer regex looks for <div[^>]*> containing EXACTLY ONE span, or no inner divs
        pass

# Let's do a more robust extraction using BeautifulSoup
import bs4
soup = bs4.BeautifulSoup(html, 'html.parser')

refs_data = []

for span in soup.find_all('span', class_='footnote-ref'):
    ref_id = span.get('data-ref')
    if not ref_id: continue
    
    # The Missal text is usually the text content of the parent element
    parent = span.parent
    
    # Clone parent to safely remove the span and get only the Missal text
    parent_clone = bs4.BeautifulSoup(str(parent), 'html.parser').div
    if parent_clone is None:
        parent_clone = bs4.BeautifulSoup(str(parent), 'html.parser').find()
    
    if parent_clone:
        # Remove the footnote span from the clone
        for s in parent_clone.find_all('span', class_='footnote-ref'):
            s.decompose()
        # Remove any rubrics inside
        for r in parent_clone.find_all('span', class_='rubric'):
            r.decompose()
            
        missal_text = parent_clone.get_text(strip=True)
    else:
        missal_text = "Unknown"
        
    # Find preceding heading
    # We can do this by finding all previous headers relative to the span
    prev_headings = span.find_all_previous(['h1', 'h2', 'h3'])
    heading_text = prev_headings[0].get_text(strip=True) if prev_headings else "Unknown"
    
    # Clean up the heading a bit
    heading_text = heading_text.replace('\u2019', "'").replace('&#8217;', "'")
    
    refs_data.append({
        'heading': heading_text,
        'missal_text': missal_text,
        'ref_id': ref_id
    })

# Deduplicate identical combinations
seen = set()
unique_refs = []
for d in refs_data:
    key = (d['heading'], d['missal_text'], d['ref_id'])
    if key not in seen:
        seen.add(key)
        unique_refs.append(d)

md = """# The Order of Mass: Scriptural Roots

This project provides an annotated, highly legible HTML version of the Catholic Order of Mass, specifically designed to highlight its profound scriptural roots. 

The Mass is deeply saturated with the Word of God—from direct quotations of the words of Christ and the Apostles, to prayers that echo the Psalms, the Prophets, and the letters of St. Paul. This page features interactive footnote annotations that allow users to hover over specific prayers and responses to read the underlying biblical texts (using the USCCB NABRE translation).

## Scripture References in the Mass

The following table catalogs the biblical references annotated in this project and the specific parts of the Mass where they appear.

| Part of Mass | Missal Text | Scripture Text |
|--------------|-------------|----------------|
"""

for item in unique_refs:
    ref_id = item['ref_id']
    bible_info = bible.get(ref_id, {})
    human_ref = bible_info.get('ref', ref_id)
    scripture_text = bible_info.get('text', '')
    
    # Format the Scripture Text column as: "text" (Ref)
    combined_scripture = f'"{scripture_text}" ({human_ref})' if scripture_text else f'({human_ref})'
    
    # Format Missal Text
    missal_text = item['missal_text']
    if missal_text:
        missal_text = f'"{missal_text}"'
        
    # Markdown table delimiters require escaping pipes
    heading = item['heading'].replace('|', '&#124;')
    missal_text = missal_text.replace('|', '&#124;')
    combined_scripture = combined_scripture.replace('|', '&#124;')
    
    md += f"| {heading} | {missal_text} | {combined_scripture} |\n"
    
with open('README.md', 'w', encoding='utf-8') as f:
    f.write(md)

print("README.md written successfully")
