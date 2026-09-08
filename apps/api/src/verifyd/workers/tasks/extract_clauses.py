import asyncio
from datetime import datetime, timezone
from verifyd.workers.celery_app import celery_app
from verifyd.db.session import SyncSessionLocal
from verifyd.db.models.contract import Contract
from verifyd.db.models.clause import Clause
from verifyd.db.models.job import Job
from verifyd.ai.gemini import GeminiClient
from verifyd.ingestion.pdf_service import PDFService
from verifyd.storage.storage import get_storage
from verifyd.core.logging import get_logger

logger = get_logger("worker.extract_clauses")


async def run_extract_clauses_async(contract_id: str, job_id: str = None):
    db = SyncSessionLocal()
    gemini = GeminiClient()
    storage = get_storage()

    try:
        contract = db.query(Contract).filter(Contract.id == contract_id).first()
        if not contract:
            logger.error("Contract not found for extraction", contract_id=contract_id)
            return

        contract.status = "extracting"
        job = None
        if job_id:
            job = db.query(Job).filter(Job.id == job_id).first()
            if job:
                job.status = "running"
                job.started_at = datetime.now(timezone.utc)
        db.commit()

        # 1. Read raw contract PDF file content from storage
        doc_bytes = None
        if contract.raw_document_key:
            doc_bytes = storage.get_file_content(contract.raw_document_key)

        extracted_doc = None
        if doc_bytes and doc_bytes.startswith(b"%PDF-"):
            extracted_doc = await PDFService.extract(file_bytes=doc_bytes)
            contract.source_content_hash = extracted_doc.content_hash

        # 2. Extract clauses using Gemini with structured text
        doc_text = extracted_doc.full_text if extracted_doc else None
        extracted_output, meta = await gemini.extract_clauses(
            pdf_content=doc_bytes if (extracted_doc and extracted_doc.is_scanned) else None,
            document_text=doc_text,
        )

        # 3. Clear any existing clauses for this version
        db.query(Clause).filter(Clause.contract_id == contract_id).delete()

        # 4. Save extracted clauses and match bounding boxes
        for i, c in enumerate(extracted_output.clauses):
            source_bbox = None
            source_page = c.source_page or 1

            if extracted_doc and not extracted_doc.is_scanned:
                matched_bbox = PDFService.locate_clause_in_document(c.source_text, extracted_doc)
                if matched_bbox:
                    source_bbox = matched_bbox
                    source_page = matched_bbox.get("page", source_page)

            clause = Clause(
                contract_id=contract_id,
                ordinal=i + 1,
                clause_ref=c.clause_ref or f"C-{i+1:02d}",
                source_text=c.source_text,
                requirement=c.requirement,
                clause_type=c.clause_type,
                params=c.params,
                modality=c.modality,
                severity=c.severity,
                is_auto_checkable=c.is_auto_checkable,
                confidence=c.confidence,
                review_status="unreviewed",
                source_page=source_page,
                source_bbox=source_bbox,
            )
            db.add(clause)

        contract.status = "needs_review"
        if job:
            job.status = "succeeded"
            job.finished_at = datetime.now(timezone.utc)
        db.commit()
        logger.info(
            "Contract clause extraction completed",
            contract_id=contract_id,
            clauses=len(extracted_output.clauses),
            content_hash=contract.source_content_hash,
        )
    except Exception as e:
        db.rollback()
        logger.error("Clause extraction task failed", contract_id=contract_id, error=str(e))
        if contract:
            contract.status = "needs_review"
        if job:
            job.status = "failed"
            job.error_class = type(e).__name__
            job.error_message = str(e)
            job.finished_at = datetime.now(timezone.utc)
        db.commit()
    finally:
        db.close()


@celery_app.task(bind=True, max_retries=3)
def extract_clauses_task(self, contract_id: str, job_id: str = None):
    asyncio.run(run_extract_clauses_async(contract_id, job_id))
