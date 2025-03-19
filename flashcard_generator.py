from __future__ import annotations

from typing import Tuple, List, Dict, Any
try:
    from typing import Self
except ImportError:
    pass

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, Frame
from reportlab.lib.enums import TA_CENTER
import re
import os


class FlashCardGenerator:
    """
    A generator for creating customizable flashcards in PDF format.
    """
    def __init__(self):
        self.filename = "flashcards.pdf"
        self.page_size = A4
        self.margins = (1*cm, 1*cm, 1*cm, 1*cm)
        self.cards_per_row = 2
        self.card_height = 5*cm
        self.entries: List[Dict[str, Any]] = []
        
    def set_filename(self, filename: str) -> Self:
        """Set the output PDF filename."""
        self.filename = filename
        return self
        
    def set_cards_per_row(self, count: int) -> Self:
        """Set the number of cards per row."""
        if count <= 0:
            raise ValueError("Cards per row must be greater than 0")
        self.cards_per_row = count
        return self
        
    def set_page_size(self, size: Tuple[float, float]) -> Self:
        """Set the page size (default is A4)."""
        self.page_size = size
        return self
        
    def set_margins(self, top: float, right: float, bottom: float, left: float) -> Self:
        """Set page margins."""
        self.margins = (top, right, bottom, left)
        return self
        
    def set_card_height(self, height: float) -> Self:
        """Set the height of each card."""
        if height <= 0:
            raise ValueError("Card height must be greater than 0")
        self.card_height = height
        return self
        
    def add_entry(self, original: str, translation: str, extra: str = "", index: str = "") -> Self:
        """
        Add a flashcard entry.
        
        Args:
            original: The text on the front of the card
            translation: The text on the back of the card
            extra: Additional information to display on the front (optional)
            index: An index or identifier for the card (optional)
        """
        print(f"Adding entry: original='{original}', translation='{translation}', extra='{extra}', index='{index}'\n\n")
        self.entries.append({
            "original": original,
            "translation": translation,
            "extra": extra,
            "index": index
        })
        return self
        
    def _parse_markdown(self, text: str) -> str:
        """Convert markdown to HTML for ReportLab Paragraph."""
        text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
        text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
        text = re.sub(r'__(.*?)__', r'<u>\1</u>', text)
        return text
        
    def _calculate_card_dimensions(self) -> Tuple[float, float]:
        """Calculate card width and maximum cards per page."""
        page_width = self.page_size[0]
        page_height = self.page_size[1]
        
        usable_width = page_width - self.margins[1] - self.margins[3]
        usable_height = page_height - self.margins[0] - self.margins[2]
        
        card_width = usable_width / self.cards_per_row
        cards_per_column = int(usable_height / self.card_height)
        
        max_cards_per_page = self.cards_per_row * cards_per_column
        
        return card_width, max_cards_per_page
        
    def generate(self) -> None:
        """Generate the PDF with flashcards in a front-back-front-back pattern."""
        if not self.entries:
            print("Warning: No flashcard entries to generate")
            return
            
        card_width, cards_per_page = self._calculate_card_dimensions()
        cards_per_row = self.cards_per_row
        rows_per_page = cards_per_page // cards_per_row
        
        c = canvas.Canvas(self.filename, pagesize=self.page_size)
        
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'Title',
            parent=styles['Heading2'],
            alignment=TA_CENTER
        )
        extra_style = ParagraphStyle(
            'Extra',
            parent=styles['Italic'],
            fontSize=9,
            leading=11
        )
        normal_style = styles['Normal']
        index_style = ParagraphStyle(
            'Index',
            parent=styles['Normal'],
            fontSize=8,
            alignment=TA_CENTER
        )
        translation_style = ParagraphStyle(
            'Translation',
            parent=styles['Normal'],
            alignment=TA_CENTER,
            fontSize=10,
            leading=12
        )
        
        total_cards = len(self.entries)
        cards_processed = 0
        
        while cards_processed < total_cards:
            remaining_cards = total_cards - cards_processed
            cards_on_current_page = min(cards_per_page, remaining_cards)
            
            for i in range(cards_on_current_page):
                entry_index = cards_processed + i
                entry = self.entries[entry_index]
                
                row = i // cards_per_row
                col = i % cards_per_row
                
                x0 = self.margins[3] + (col * card_width)
                y0 = self.page_size[1] - self.margins[0] - ((row + 1) * self.card_height)
                
                c.setStrokeColorRGB(0.8, 0.8, 0.8)
                c.rect(x0, y0, card_width, self.card_height)
                
                content_margin = 0.3 * cm
                frame_width = card_width - (2 * content_margin)
                frame_height = self.card_height - (2 * content_margin)
                frame_x = x0 + content_margin
                frame_y = y0 + content_margin
                
                original_text = self._parse_markdown(entry["original"])
                original_para = Paragraph(original_text, title_style)
                
                front_frame = Frame(frame_x, frame_y, frame_width, frame_height, 
                                   showBoundary=0, leftPadding=5, rightPadding=5)
                story = [original_para]
                
                if entry["extra"]:
                    extra_text = self._parse_markdown(entry["extra"])
                    extra_para = Paragraph(extra_text, extra_style)
                    story.append(Paragraph("<br/>", normal_style))
                    story.append(extra_para)
                    
                front_frame.addFromList(story, c)
                
                if entry["index"]:
                    index_para = Paragraph(entry["index"], index_style)
                    c.saveState()
                    index_frame = Frame(frame_x, frame_y, frame_width, 0.5*cm, 
                                       showBoundary=0, bottomPadding=2)
                    index_frame.addFromList([index_para], c)
                    c.restoreState()
                    
            c.showPage()
            for i in range(cards_on_current_page):
                entry_index = cards_processed + i
                entry = self.entries[entry_index]
                
                row = i // cards_per_row
                col = cards_per_row - 1 - (i % cards_per_row)
                
                x0 = self.margins[3] + (col * card_width)
                y0 = self.page_size[1] - self.margins[0] - ((row + 1) * self.card_height)
                
                c.setStrokeColorRGB(0.8, 0.8, 0.8)
                c.rect(x0, y0, card_width, self.card_height)
                
                content_margin = 0.3 * cm
                frame_width = card_width - (2 * content_margin)
                frame_height = self.card_height - (2 * content_margin)
                frame_x = x0 + content_margin
                frame_y = y0 + content_margin
                
                translation_text = self._parse_markdown(entry["translation"])
                translation_para = Paragraph(translation_text, translation_style)
                
                back_frame = Frame(frame_x, frame_y, frame_width, frame_height, 
                                  showBoundary=0, leftPadding=5, rightPadding=5)
                back_frame.addFromList([translation_para], c)
                
                if entry["index"]:
                    index_para = Paragraph(entry["index"], index_style)
                    c.saveState()
                    index_frame = Frame(frame_x, frame_y, frame_width, 0.5*cm, 
                                       showBoundary=0, bottomPadding=2)
                    index_frame.addFromList([index_para], c)
                    c.restoreState()
                    
            cards_processed += cards_on_current_page
            
            if cards_processed < total_cards:
                c.showPage()
        
        c.save()
        
        print(f"Generated {len(self.entries)} flashcards in '{self.filename}'")
        print("For correct printing: Use double-sided printing, flip on short edge.")
        
    def generate_pdf(self, flashcards, output_path):
        """
        Generate a PDF from a list of flashcards.
        
        Args:
            flashcards: List of tuples (front, back, extra, index)
            output_path: Path where the PDF will be saved
        """
        self.entries = []
        
        self.set_filename(output_path)
        
        for front, back, extra, index in flashcards:
            self.add_entry(original=front, translation=back, extra=extra, index=index)
        
        self.generate()
        
        return output_path