import fitz  # PyMuPDF
import os

class PDFProcessor:
    def __init__(self, output_image_dir="data/images"):
        self.output_image_dir = output_image_dir
        os.makedirs(self.output_image_dir, exist_ok=True)

    def process_pdf(self, pdf_path: str):
        """
        Extracts text and images from a PDF.
        Returns a list of dictionaries per page with text and image info.
        """
        doc = fitz.open(pdf_path)
        pages_data = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            
            # Extract raw text
            text = page.get_text("text")
            
            # Extract images (diagrams)
            image_list = page.get_images(full=True)
            images_info = []
            
            for img_index, img in enumerate(image_list):
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]
                
                image_name = f"doc_{os.path.basename(pdf_path)}_page_{page_num+1}_img_{img_index}.{image_ext}"
                image_path = os.path.join(self.output_image_dir, image_name)
                
                # Save the image to disk
                with open(image_path, "wb") as f:
                    f.write(image_bytes)
                    
                # Attempt to get bounding box for highlighting
                rects = page.get_image_rects(xref)
                bbox = [rect.x0, rect.y0, rect.x1, rect.y1] if rects else None
                
                images_info.append({
                    "path": image_path,
                    "bbox": bbox
                })
                
            pages_data.append({
                "page_number": page_num + 1,
                "text": text,
                "images": images_info
            })
            
        doc.close()
        return pages_data

pdf_processor = PDFProcessor()
