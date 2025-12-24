from PIL import Image, ImageDraw, ImageFont
import os

# Define the code snippets
snippets = {
    "code_parser_factory.png": """class ParserFactory:
    @staticmethod
    def get_parser(mime_type: str) -> BaseParser:
        if mime_type == "application/pdf":
            # Check if scanned or text
            return PDFHybridParser()
        elif mime_type == "application/json":
            return FHIRParser()
        elif mime_type == "x-application/hl7":
            return HL7Parser()
        else:
            raise UnsupportedFormatException(mime_type)

class PDFHybridParser(BaseParser):
    def parse(self, stream):
        # Implementation logic
        pass""",

    "code_dockerfile.png": """# Builder Stage
FROM python:3.9-builder as builder
RUN pip wheel --no-cache-dir -r requirements.txt

# Final Stage
FROM python:3.9-slim
COPY --from=builder /wheels /wheels
RUN pip install /wheels/*
CMD ["uvicorn", "main:app", "--host", "0.0.0.0"]""",

    "code_kubernetes.png": """apiVersion: apps/v1
kind: Deployment
metadata:
  name: indexeur
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: indexeur
        image: medbot/indexeur:v1
        resources:
          limits:
            memory: "4Gi"
            cpu: "2000m" """,

    "code_api_spec.png": """{
  "patient_id": "P12345",
  "document": "Base64..."
}"""
}

# Configuration
BG_COLOR = (30, 30, 30)  # VS Code Dark
TEXT_COLOR = (212, 212, 212) # VS Code Light Text
KEYWORD_COLOR = (86, 156, 214) # Blue
STRING_COLOR = (206, 145, 120) # Orange
COMMENT_COLOR = (106, 153, 85) # Green

FONT_SIZE = 24
PADDING = 40
LINE_HEIGHT = 36
OUTPUT_DIR = "images"

# Ensure output directory exists
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# Try to load a font, otherwise default
try:
    font = ImageFont.truetype("arial.ttf", FONT_SIZE)
except IOError:
    # Fallback for Linux/Container if needed, but Windows usually has arial
    font = ImageFont.load_default()

def highlight_line(line):
    # Very basic syntax highlighting logic
    if line.strip().startswith("#"):
        return COMMENT_COLOR
    if "class " in line or "def " in line or "import " in line or "FROM " in line or "RUN " in line or "CMD " in line:
        return KEYWORD_COLOR
    if '"' in line or "'" in line:
        return STRING_COLOR
    return TEXT_COLOR

for filename, code in snippets.items():
    lines = code.split('\n')
    
    # Calculate image size
    max_width = 0
    for line in lines:
        try:
             # getbbox returns (left, top, right, bottom)
            bbox = font.getbbox(line)
            width = bbox[2] - bbox[0]
            if width > max_width:
                max_width = width
        except AttributeError:
             # getsize is deprecated in newer Pillow, fallback
            width = font.getsize(line)[0]
            if width > max_width:
                max_width = width
            
    img_width = max_width + (PADDING * 2)
    img_height = (len(lines) * LINE_HEIGHT) + (PADDING * 2)
    
    image = Image.new('RGB', (img_width, img_height), color=BG_COLOR)
    draw = ImageDraw.Draw(image)
    
    y = PADDING
    for line in lines:
        color = highlight_line(line)
        draw.text((PADDING, y), line, font=font, fill=color)
        y += LINE_HEIGHT
        
    save_path = os.path.join(OUTPUT_DIR, filename)
    image.save(save_path)
    print(f"Generated {save_path}")

print("All code images generated.")
