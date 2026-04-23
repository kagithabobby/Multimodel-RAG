import re
import spacy

class PIIScraper:
    def __init__(self):
        # Load spaCy Japanese model if available for NER, else fallback
        try:
            self.nlp = spacy.load("ja_core_news_sm")
            self.use_ner = True
        except OSError:
            self.use_ner = False
            print("Warning: ja_core_news_sm not found. Falling back to regex-only masking for names.")

        self.patterns = {
            "MY_NUMBER": r"\b\d{12}\b", # 12 digits
            "ZAIKYU_CARD": r"\b[A-Z]{2}\d{7}[A-Z]{2}\b", # 2 Letters, 7 digits, 2 Letters
            "JP_PHONE": r"\b0\d{1,4}-\d{1,4}-\d{4}\b", # standard Japanese phone format
            "IP_ADDRESS": r"\b(?:\d{1,3}\.){3}\d{1,3}\b" # IPv4
        }

    def mask_text(self, text: str) -> str:
        if not text:
            return text
            
        masked_text = text

        # 1. Regex replacements
        for entity_type, pattern in self.patterns.items():
            masked_text = re.sub(pattern, f"[{entity_type}]", masked_text)

        # 2. NER replacements (Names)
        if self.use_ner:
            doc = self.nlp(masked_text)
            # Reconstruct text replacing PERSON entities
            # Iterate backwards to avoid index shifting
            spans = [(ent.start_char, ent.end_char, ent.label_) for ent in doc.ents if ent.label_ == "PERSON"]
            for start, end, label in sorted(spans, reverse=True):
                masked_text = masked_text[:start] + "[PERSON_NAME]" + masked_text[end:]

        return masked_text

pii_scraper = PIIScraper()
