from __future__ import annotations

import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Optional

import PyPDF2
from docx import Document


@dataclass
class QualitativeChunk:
    chunk_id: str
    document_name: str
    category: str
    source_organization: str
    authority_status: str
    section_title: str
    page_start: Optional[int]
    page_end: Optional[int]
    text: str


class QualitativeDocumentChunker:

    PDF_FRONT_MATTER_PAGES = 5

    def __init__(self, max_chars: int = 6000):
        self.max_chars = max_chars
        self.chunks: List[QualitativeChunk] = []

    # =========================================================
    # OCC SECTION HEADINGS
    # =========================================================

    @staticmethod
    def _get_occ_headings():
        return [
            "Introduction",
            "Overview",
            "Lending Examinations and Ongoing Supervision",
            "Ongoing Supervision",
            "Loan Sampling",
            "Credit Underwriting Reviews",
            "Background",
            "Loan Life Cycle",
            "Risks Associated With Lending",
            "Credit Risk",
            "Concentration Risk",
            "Risk Layering",
            "Refinance Risk",
            "Interest Rate Risk",
            "Liquidity Risk",
            "Price Risk",
            "Operational Risk",
            "Fraud Risk",
            "Compliance Risk",
            "Strategic Risk",
            "Risk Management",
            "Board and Management Oversight",
            "Committees",
            "Credit Culture",
            "Strategic and Operational Planning",
            "Strategic Planning",
            "Operational Planning",
            "Pricing Strategies",
            "Risk Appetite",
            "Risk Assessment",
            "Personnel",
            "Separation of Duties",
            "Training",
            "Loan Officer Compensation",
            "Policies and Procedures",
            "Credit Underwriting",
            "Structural Weaknesses",
            "Capitalization of Interest",
            "Lending Authorities",
            "Automated Credit Approval Processes",
            "Loan Purchase Activities",
            "Model Risk Management",
            "Third-Party Risk Management",
            "Independent Credit Risk Review",
            "Internal and External Audit",
            "Internal Audit",
            "External Audit",
            "Credit Administration",
            "Loan Administration",
            "Pre-Closing Reviews",
            "Loan Closing",
            "Loan Booking",
            "Post-Closing Reviews",
            "Loan Servicing and Monitoring",
            "Secondary Marketing",
            "Problem Loan Management",
            "Collections",
            "Workouts",
            "Foreclosure and Repossession",
            "Postmortem Reviews",
            "Portfolio Management",
            "Exceptions",
            "Unidentified Exceptions",
            "Exception Limits, Monitoring, and Analysis",
            "Management Information Systems",
            "Management and Board Reports",
            "Stress Testing",
            "Loan-Level Stress Testing",
            "Loan-Level Stress Test Example",
            "Portfolio Stress Testing",
            "Credit Risk-Rating Systems",
            "Nonaccrual Status",
            "General Rule for Nonaccrual Status",
            "Exceptions to the General Rule for Nonaccrual Status",
            "Nonaccrual Status for Purchased Credit-Deteriorated Assets",
            "Returning a Loan to Accrual Status",
            "Examination Procedures",
            "Scope",
            "Quantity of Risk",
            "Quality of Risk Management",
            "Internal Controls and Information Systems",
            "Conclusions",
            "Internal Control Questionnaire",
            "Verification Procedures",
            "Appendixes",
            "Appendix A: Quantity of Credit Risk Indicators",
            "Appendix B: Quality of Credit Risk Management Indicators",
            "Appendix C: Sample Request List",
            "Appendix D: Loan Sampling",
            "Loan Sampling Overview",
            "Judgmental Sampling",
            "Determine Population, Areas of Focus, and Sample Size",
            "Evaluating a Judgmental Sample",
            "Statistical Sampling",
            "Appendix E: Assessing Credit Underwriting",
            "Scope of Credit Underwriting Reviews",
            "Assessing Underwriting Policies",
            "Assessing Underwriting Practices",
            "Portfolio-Level Analysis",
            "Loan-Level Transaction Testing",
            "Addressing Liberal Underwriting Practices",
            "Report of Examination and Supervisory Letter Considerations",
            "Appendix F: Commercial Credit Underwriting Assessment Job Aid",
            "Commercial Credit Structure and Sources of Repayment",
            "Commercial Credit Collateral",
            "Commercial Credit Controls",
            "Appendix G: Retail Credit Underwriting Assessment Job Aid",
            "Retail Credit Structure and Sources of Repayment",
            "Retail Credit Collateral",
            "Appendix H: Loan Purchase Review Job Aid",
            "Appendix I: Examples of Lending-Related Laws and Regulations",
            "Appendix J: Interest on Loans",
            "Definitions for 12 CFR 7.4001 (National Banks) and 12 CFR 160.110 (FSAs)",
            "Maximum Interest Rates",
            "Exportation of Interest Rates",
        ]

    # =========================================================
    # BASIC TEXT CLEANING
    # =========================================================

    @staticmethod
    def _clean_text(text: str) -> str:
        text = text.replace("\x00", "")
        text = text.replace("\r\n", "\n")
        text = text.replace("\r", "\n")

        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)

        return text.strip()

    # =========================================================
    # PDF EXTRACTION
    # =========================================================

    @staticmethod
    def _extract_pages(pdf_path: str) -> List[str]:

        path = Path(pdf_path)

        if not path.exists():
            raise FileNotFoundError(
                f"Document not found: {pdf_path}"
            )

        reader = PyPDF2.PdfReader(str(path))

        return [
            page.extract_text() or ""
            for page in reader.pages
        ]

    # =========================================================
    # PDF CLEANING
    # =========================================================

    @staticmethod
    def _clean_page_text(text: str) -> str:

        text = text.replace("\x00", "")

        text = re.sub(
            r"COMPTROLLER.?S HANDBOOK",
            "",
            text,
            flags=re.IGNORECASE
        )

        text = re.sub(
            r"Version\s+1\.0",
            "",
            text,
            flags=re.IGNORECASE
        )

        text = re.sub(
            r"Lending and Loan Portfolio Risk Management",
            "",
            text,
            flags=re.IGNORECASE
        )

        text = re.sub(
            r"[ \t]+",
            " ",
            text
        )

        text = re.sub(
            r"\n{3,}",
            "\n\n",
            text
        )

        return text.strip()

    # =========================================================
    # HEADING NORMALIZATION
    # =========================================================

    @staticmethod
    def _normalize_heading(text: str) -> str:

        text = text.strip()

        text = re.sub(
            r"\s+",
            " ",
            text
        )

        return text.lower()

    # =========================================================
    # FIND OCC HEADINGS
    # =========================================================

    def _find_heading_positions(self, page_text: str):

        positions = []

        lines = page_text.splitlines()

        headings = self._get_occ_headings()

        for line_number, raw_line in enumerate(lines):

            line = raw_line.strip()

            if not line:
                continue

            normalized_line = self._normalize_heading(line)

            for heading in headings:

                normalized_heading = self._normalize_heading(
                    heading
                )

                if normalized_line == normalized_heading:

                    positions.append(
                        (
                            line_number,
                            heading
                        )
                    )

                    break

        return positions

    # =========================================================
    # SPLIT LARGE TEXT
    # =========================================================

    def _split_large_section(self, text: str) -> List[str]:

        text = self._clean_text(text)

        if not text:
            return []

        if len(text) <= self.max_chars:
            return [text]

        paragraphs = re.split(
            r"\n\s*\n",
            text
        )

        chunks = []

        current = ""

        for paragraph in paragraphs:

            paragraph = paragraph.strip()

            if not paragraph:
                continue

            candidate = (
                current + "\n\n" + paragraph
                if current
                else paragraph
            )

            if len(candidate) <= self.max_chars:

                current = candidate

            else:

                if current:
                    chunks.append(
                        current.strip()
                    )

                if len(paragraph) <= self.max_chars:

                    current = paragraph

                else:

                    sentences = re.split(
                        r"(?<=[.!?])\s+",
                        paragraph
                    )

                    current = ""

                    for sentence in sentences:

                        sentence = sentence.strip()

                        if not sentence:
                            continue

                        candidate = (
                            current + " " + sentence
                            if current
                            else sentence
                        )

                        if len(candidate) <= self.max_chars:

                            current = candidate

                        else:

                            if current:
                                chunks.append(
                                    current.strip()
                                )

                            current = sentence

        if current:
            chunks.append(
                current.strip()
            )

        return chunks

    # =========================================================
    # BUILD OCC SECTIONS
    # =========================================================

    def _build_sections(self, pages: List[str]):

        sections = []

        current_section = None
        current_text = []

        current_page_start = None
        current_page_end = None

        content_pages = pages[
            self.PDF_FRONT_MATTER_PAGES:
        ]

        for local_index, raw_page in enumerate(
            content_pages
        ):

            printed_page = local_index + 1

            cleaned_page = self._clean_page_text(
                raw_page
            )

            if not cleaned_page:
                continue

            lines = cleaned_page.splitlines()

            heading_positions = (
                self._find_heading_positions(
                    cleaned_page
                )
            )

            if not heading_positions:

                if current_section is not None:

                    current_text.append(
                        cleaned_page
                    )

                    current_page_end = printed_page

                continue

            for position_index, (
                line_number,
                heading
            ) in enumerate(heading_positions):

                if position_index == 0:

                    before_lines = lines[
                        :line_number
                    ]

                else:

                    previous_line = (
                        heading_positions[
                            position_index - 1
                        ][0]
                    )

                    before_lines = lines[
                        previous_line + 1:
                        line_number
                    ]

                before_text = "\n".join(
                    before_lines
                ).strip()

                if (
                    before_text
                    and current_section is not None
                ):

                    current_text.append(
                        before_text
                    )

                if current_section is not None:

                    final_text = self._clean_page_text(
                        "\n".join(current_text)
                    )

                    if final_text:

                        sections.append(
                            {
                                "section_title":
                                    current_section,

                                "page_start":
                                    current_page_start,

                                "page_end":
                                    current_page_end,

                                "text":
                                    final_text,
                            }
                        )

                current_section = heading

                current_page_start = printed_page
                current_page_end = printed_page

                if position_index + 1 < len(
                    heading_positions
                ):

                    next_line = (
                        heading_positions[
                            position_index + 1
                        ][0]
                    )

                    after_lines = lines[
                        line_number + 1:
                        next_line
                    ]

                else:

                    after_lines = lines[
                        line_number + 1:
                    ]

                current_text = []

                after_text = "\n".join(
                    after_lines
                ).strip()

                if after_text:
                    current_text.append(
                        after_text
                    )

        if current_section is not None:

            final_text = self._clean_page_text(
                "\n".join(current_text)
            )

            if final_text:

                sections.append(
                    {
                        "section_title":
                            current_section,

                        "page_start":
                            current_page_start,

                        "page_end":
                            current_page_end,

                        "text":
                            final_text,
                    }
                )

        return sections

    # =========================================================
    # DOCX EXTRACTION
    # =========================================================

    @staticmethod
    def _extract_docx(docx_path: str) -> str:

        path = Path(docx_path)

        if not path.exists():
            raise FileNotFoundError(
                f"Document not found: {docx_path}"
            )

        document = Document(str(path))

        paragraphs = []

        for paragraph in document.paragraphs:

            text = paragraph.text.strip()

            if text:
                paragraphs.append(text)

        return "\n\n".join(paragraphs)

    # =========================================================
    # TXT EXTRACTION
    # =========================================================

    @staticmethod
    def _extract_txt(txt_path: str) -> str:

        path = Path(txt_path)

        if not path.exists():
            raise FileNotFoundError(
                f"Document not found: {txt_path}"
            )

        return path.read_text(
            encoding="utf-8"
        )

    # =========================================================
    # GENERIC SECTION DETECTION
    # =========================================================

    @staticmethod
    def _looks_like_heading(line: str) -> bool:

        line = line.strip()

        if not line:
            return False

        if len(line) > 100:
            return False

        if line.endswith((".", "?", "!", ":")):
            return False

        words = line.split()

        if len(words) > 12:
            return False

        # Explicit common document headings
        known_headings = {
            "management discussion and analysis",
            "document status",
            "document metadata",
            "financial performance context",
            "management explanation",
            "working capital impact",
            "related analytical flag",
            "context",
            "introduction",
            "overview",
            "background",
            "conclusion",
            "summary",
        }

        if line.lower() in known_headings:
            return True

        # Mostly title case
        title_case_words = sum(
            1
            for word in words
            if word[:1].isupper()
        )

        return (
            len(words) <= 8
            and title_case_words >= max(1, len(words) - 1)
        )

    # =========================================================
    # BUILD GENERIC DOCUMENT SECTIONS
    # =========================================================

    def _build_generic_sections(self, full_text: str):
    
        sections = []

    # ---------------------------------------------------------
    # PAGE-AWARE PROCESSING
    # ---------------------------------------------------------
    # The IFRS branch of chunk_pdf() adds page markers like:
    #
    # [PAGE 1]
    # text from page 1
    #
    # [PAGE 2]
    # text from page 2
    #
    # We split on those markers so that every section keeps
    # its page_start and page_end metadata.
    # ---------------------------------------------------------

        page_blocks = re.split(
            r"\[PAGE\s+(\d+)\]",
            full_text
        )

        current_section = None

    # page_blocks structure:
    #
    # ["", "1", "page 1 text", "2", "page 2 text", ...]

        for i in range(1, len(page_blocks), 2):

            page_number = int(page_blocks[i])
            page_text = page_blocks[i + 1].strip()

            if not page_text:
                continue

        # -----------------------------------------------------
        # Split page into paragraphs
        # -----------------------------------------------------

            paragraphs = [
                paragraph.strip()
                for paragraph in page_text.split("\n\n")
                if paragraph.strip()
            ]

            for paragraph in paragraphs:

                lines = paragraph.splitlines()

                first_line = (
                    lines[0].strip()
                    if lines
                    else ""
                )

                is_heading = False

            # -------------------------------------------------
            # Detect IFRS headings
            # -------------------------------------------------

                if first_line:

                # Common IFRS section headings
                    if re.match(
                        r"^(Objective|Scope|Definitions|Recognition|"
                        r"Measurement|Presentation|Disclosure|"
                        r"Classification|Impairment|Derecognition|"
                        r"Transition|Effective date|Appendix|"
                        r"Basis for Conclusions)",
                        first_line,
                        re.IGNORECASE
                    ):
                        is_heading = True

                # Numbered headings
                #
                # Examples:
                # 1 Scope
                # 2 Recognition
                # 3.1 Measurement
                # 4.2.1 Classification
                #
                    elif re.match(
                        r"^\d+(\.\d+)*\.?\s+",
                        first_line
                    ):
                        is_heading = True

                # Short title-like headings
                    elif (
                        len(first_line) <= 120
                        and len(lines) <= 3
                        and first_line
                        and first_line[0].isupper()
                    ):
                        is_heading = True

            # -------------------------------------------------
            # NEW SECTION
            # -------------------------------------------------

                if is_heading:

                    if current_section:

                        sections.append(
                            current_section
                        )

                    current_section = {
                        "section_title": first_line,
                        "text": paragraph,
                        "page_start": page_number,
                        "page_end": page_number,
                    }

            # -------------------------------------------------
            # CONTINUE CURRENT SECTION
            # -------------------------------------------------

                else:

                # If the document starts with text before
                # the first detected heading.
                    if current_section is None:

                        current_section = {
                            "section_title": "General",
                            "text": paragraph,
                            "page_start": page_number,
                            "page_end": page_number,
                        }

                    else:

                        current_section["text"] += (
                            "\n\n" + paragraph
                        )

                    # Update the ending page as the section
                    # continues across pages.
                        current_section["page_end"] = (
                            page_number
                        )

    # ---------------------------------------------------------
    # ADD FINAL SECTION
    # ---------------------------------------------------------

        if current_section:

            sections.append(
                current_section
            )

        return sections

    # =========================================================
    # CREATE CHUNKS FROM SECTIONS
    # =========================================================

    def _create_chunks(
        self,
        sections,
        category,
        source_organization,
        authority_status,
        document_name
    ):

        self.chunks = []

        counter = 1

        for section in sections:

            pieces = self._split_large_section(
                section["text"]
            )

            for piece in pieces:

                if not piece.strip():
                    continue

                self.chunks.append(
                    QualitativeChunk(
                        chunk_id=(
                            f"{category}_{counter:04d}"
                        ),
                        document_name=document_name,
                        category=category,
                        source_organization=(
                            source_organization
                        ),
                        authority_status=(
                            authority_status
                        ),
                        section_title=(
                            section["section_title"]
                        ),
                        page_start=(
                            section["page_start"]
                        ),
                        page_end=(
                            section["page_end"]
                        ),
                        text=piece,
                    )
                )

                counter += 1

        return self.chunks

    # =========================================================
    # PDF CHUNKING
    # =========================================================

    def chunk_pdf(
        self,
        pdf_path: str,
        category: str,
        source_organization: str,
        authority_status: str,
        document_name: Optional[str] = None,
    ) -> List[QualitativeChunk]:

        path = Path(pdf_path)

        document_name = (
            document_name
            or path.name
        )

        pages = self._extract_pages(
            pdf_path
        )

        # ---------------------------------------------------------
        # IFRS / GENERIC PDF CHUNKING
        # ---------------------------------------------------------
        #
        # OCC documents use the specialized _build_sections()
        # parser. IFRS documents use the generic section parser.
        #
        # This prevents IFRS PDFs from being forced through
        # OCC-specific heading rules.
        # ---------------------------------------------------------

        if category == "IFRS":

            page_text = []

            for page_number, page in enumerate(
                pages,
                start=1
            ):

                cleaned_page = self._clean_page_text(
                    page
                )

                if cleaned_page:

                    page_text.append(
                        f"[PAGE {page_number}]\n"
                        f"{cleaned_page}"
                    )

            full_text = "\n\n".join(
                page_text
            )

            sections = self._build_generic_sections(
                full_text
            )

            return self._create_chunks(
                sections,
                category,
                source_organization,
                authority_status,
                document_name
            )

        # ---------------------------------------------------------
        # EXISTING OCC PDF CHUNKING
        # ---------------------------------------------------------

        sections = self._build_sections(
            pages
        )

        return self._create_chunks(
            sections,
            category,
            source_organization,
            authority_status,
            document_name
        )

    # =========================================================
    # DOCX CHUNKING
    # =========================================================

    def chunk_docx(
        self,
        docx_path: str,
        category: str,
        source_organization: str,
        authority_status: str,
        document_name: Optional[str] = None,
    ) -> List[QualitativeChunk]:

        path = Path(docx_path)

        document_name = (
            document_name
            or path.name
        )

        text = self._extract_docx(
            docx_path
        )

        sections = self._build_generic_sections(
            text
        )

        return self._create_chunks(
            sections,
            category,
            source_organization,
            authority_status,
            document_name
        )

    # =========================================================
    # TXT CHUNKING
    # =========================================================

    def chunk_txt(
        self,
        txt_path: str,
        category: str,
        source_organization: str,
        authority_status: str,
        document_name: Optional[str] = None,
    ) -> List[QualitativeChunk]:

        path = Path(txt_path)

        document_name = (
            document_name
            or path.name
        )

        text = self._extract_txt(
            txt_path
        )

        sections = self._build_generic_sections(
            text
        )

        return self._create_chunks(
            sections,
            category,
            source_organization,
            authority_status,
            document_name
        )

    # =========================================================
    # AUTOMATIC FORMAT DISPATCH
    # =========================================================

    def chunk_document(
        self,
        file_path: str,
        category: str,
        source_organization: str,
        authority_status: str,
        document_name: Optional[str] = None,
    ) -> List[QualitativeChunk]:

        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(
                f"Document not found: {file_path}"
            )

        extension = path.suffix.lower()

        if extension == ".pdf":

            return self.chunk_pdf(
                file_path,
                category=category,
                source_organization=source_organization,
                authority_status=authority_status,
                document_name=document_name,
            )

        if extension == ".docx":

            return self.chunk_docx(
                file_path,
                category=category,
                source_organization=source_organization,
                authority_status=authority_status,
                document_name=document_name,
            )

        if extension == ".txt":

            return self.chunk_txt(
                file_path,
                category=category,
                source_organization=source_organization,
                authority_status=authority_status,
                document_name=document_name,
            )

        raise ValueError(
            f"Unsupported file type: {extension}. "
            f"Supported types: PDF, DOCX, TXT."
        )

    # =========================================================
    # DATAFRAME
    # =========================================================

    def to_dataframe(self):

        import pandas as pd

        return pd.DataFrame(
            [
                asdict(chunk)
                for chunk in self.chunks
            ]
        )


if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "file_path"
    )

    parser.add_argument(
        "--category",
        required=True
    )

    parser.add_argument(
        "--source-organization",
        required=True
    )

    parser.add_argument(
        "--authority-status",
        required=True
    )

    args = parser.parse_args()

    chunker = QualitativeDocumentChunker()

    chunks = chunker.chunk_document(
        args.file_path,
        category=args.category,
        source_organization=args.source_organization,
        authority_status=args.authority_status,
    )

    print("SUCCESS")
    print("TOTAL CHUNKS:", len(chunks))
    print()

    for chunk in chunks[:20]:

        print("=" * 80)

        print(
            "Chunk:",
            chunk.chunk_id
        )

        print(
            "Section:",
            chunk.section_title
        )

        print(
            "Pages:",
            chunk.page_start,
            "-",
            chunk.page_end
        )

        print(
            "Characters:",
            len(chunk.text)
        )

        print(
            chunk.text[:500]
        )
