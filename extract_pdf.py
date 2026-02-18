from pypdf import PdfReader
reader = PdfReader('c:/Users/HP/Downloads/SAR format - Copy.pdf')
with open('c:/Users/HP/Downloads/Hack-o-Hire/sar_content.txt', 'w', encoding='utf-8') as f:
    for page in reader.pages:
        f.write(page.extract_text())
        f.write('\n')
