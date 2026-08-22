from core.fpa.qualitative_document_ingestion import QualitativeDocumentIngestion


# Create the existing ingestion engine
ingestion = QualitativeDocumentIngestion()


# ---------------------------------------------------------
# IFRS 1
# ---------------------------------------------------------

ifrs1 = ingestion.ingest(
    file_path="../DATASET/True_data/qualitative_corpus/IFRS/ifrs-1-first-time-adoption.pdf",
    category="IFRS",
    source_organization="IFRS Foundation",
    source_type="IFRS Standard",
    authority_status="official_IFRS",
    topic="First-time Adoption of IFRS",
    title="IFRS 1 First-time Adoption of International Financial Reporting Standards",
)


# ---------------------------------------------------------
# IFRS 7
# ---------------------------------------------------------

ifrs7 = ingestion.ingest(
    file_path="../DATASET/True_data/qualitative_corpus/IFRS/ifrs-7-financial-instruments.pdf",
    category="IFRS",
    source_organization="IFRS Foundation",
    source_type="IFRS Standard",
    authority_status="official_IFRS",
    topic="Financial Instruments",
    title="IFRS 7 Financial Instruments: Disclosures",
)


# ---------------------------------------------------------
# IFRS 9
# ---------------------------------------------------------

ifrs9 = ingestion.ingest(
    file_path="../DATASET/True_data/qualitative_corpus/IFRS/ifrs-9-financial-instruments.pdf",
    category="IFRS",
    source_organization="IFRS Foundation",
    source_type="IFRS Standard",
    authority_status="official_IFRS",
    topic="Financial Instruments",
    title="IFRS 9 Financial Instruments",
)


# ---------------------------------------------------------
# DISPLAY RESULTS
# ---------------------------------------------------------

print("\n========== IFRS INGESTION RESULTS ==========\n")

for document in ingestion.documents:

    print(f"Filename          : {document.filename}")
    print(f"File Type         : {document.file_type}")
    print(f"Category          : {document.category}")
    print(f"Source            : {document.source_organization}")
    print(f"Source Type       : {document.source_type}")
    print(f"Authority Status  : {document.authority_status}")
    print(f"Topic             : {document.topic}")
    print(f"Title             : {document.title}")
    print(f"Page Count        : {document.page_count}")
    print(f"Character Count   : {document.character_count}")
    print(f"Ingestion Status  : {document.ingestion_status}")
    print("-" * 60)