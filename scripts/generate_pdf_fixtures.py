import os
import io
from pypdf import PdfWriter, PdfReader
from PIL import Image, ImageDraw

fixtures_dir = os.path.join(os.path.dirname(__file__), "..", "apps", "api", "tests", "fixtures")
os.makedirs(fixtures_dir, exist_ok=True)

clean_pdf_path = os.path.join(fixtures_dir, "clean_contract.pdf")
scanned_pdf_path = os.path.join(fixtures_dir, "scanned_contract.pdf")
encrypted_pdf_path = os.path.join(fixtures_dir, "encrypted_contract.pdf")

# 1. Clean Text Layer PDF using pypdf/canvas or blank stream
writer = PdfWriter()
page1 = writer.add_blank_page(width=612, height=792) # Standard Letter points
# Add annotations/text layer
# Write raw PDF stream with valid font and text operations
raw_pdf_page1 = b"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R 4 0 R] /Count 2 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 5 0 R /Resources << /Font << /F1 7 0 R >> >> >>
endobj
4 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 6 0 R /Resources << /Font << /F1 7 0 R >> >> >>
endobj
5 0 obj
<< /Length 260 >>
stream
BT
/F1 14 Tf
50 720 Td
(INFLUENCER SPONSORSHIP AGREEMENT - PAGE 1) Tj
/F1 11 Tf
0 -40 Td
(1. The Creator agrees to feature the Lumen Hydration Serum for a minimum of thirty continuous seconds.) Tj
0 -30 Td
(2. The Creator shall clearly mention the brand name Lumen Skincare at least twice.) Tj
0 -30 Td
(3. The post must include the mandatory disclosure hashtag #ad in the first two lines of caption.) Tj
ET
endstream
endobj
6 0 obj
<< /Length 220 >>
stream
BT
/F1 14 Tf
50 720 Td
(INFLUENCER SPONSORSHIP AGREEMENT - PAGE 2) Tj
/F1 11 Tf
0 -40 Td
(4. No competitor skincare products such as GlowCo or PureSkin may appear anywhere in the deliverable.) Tj
0 -30 Td
(5. The discount code LUMEN20 must be highlighted in the caption.) Tj
ET
endstream
endobj
7 0 obj
<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>
endobj
xref
0 8
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000234 00000 n 
0000000353 00000 n 
0000000665 00000 n 
0000000937 00000 n 
trailer
<< /Size 8 /Root 1 0 R >>
startxref
1008
%%EOF
"""

with open(clean_pdf_path, "wb") as f:
    f.write(raw_pdf_page1)

# 2. Encrypted PDF (Clean contract encrypted with password 'SecretPass2026')
enc_reader = PdfReader(io.BytesIO(raw_pdf_page1))
enc_writer = PdfWriter()
enc_writer.append(enc_reader)
enc_writer.encrypt("SecretPass2026")
with open(encrypted_pdf_path, "wb") as f:
    enc_writer.write(f)

# 3. Scanned PDF (Only raster image, no text stream)
img = Image.new("RGB", (612, 792), color=(245, 245, 245))
d = ImageDraw.Draw(img)
d.text((50, 50), "[SCANNED CONTRACT IMAGE ONLY - NO TEXT LAYER]", fill=(80, 80, 80))
img_byte_arr = io.BytesIO()
img.save(img_byte_arr, format="PDF")
with open(scanned_pdf_path, "wb") as f:
    f.write(img_byte_arr.getvalue())

print("Fixture PDFs created successfully in:", fixtures_dir)
