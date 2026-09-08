import sys
import os
from datetime import date, datetime, timedelta, timezone

sys.path.insert(0, "apps/api/src")

from verifyd.db.session import SyncSessionLocal, sync_engine
from verifyd.db.models import (
    Base,
    Organization,
    User,
    CreatorProfile,
    Campaign,
    Contract,
    Clause,
    Submission,
    ComplianceReport,
    ClauseVerdict,
    EvidenceItem,
    AnalysisArtifact,
    AuditEvent,
    Job,
)
from verifyd.core.security import hash_password


def seed():
    print("Seeding Verifyd Database...")
    Base.metadata.create_all(bind=sync_engine)
    db = SyncSessionLocal()

    # Clear existing data in reverse order of dependencies
    db.query(EvidenceItem).delete()
    db.query(ClauseVerdict).delete()
    db.query(ComplianceReport).delete()
    db.query(AnalysisArtifact).delete()
    db.query(Job).delete()
    db.query(Submission).delete()
    db.query(Clause).delete()
    db.query(Contract).delete()
    db.query(Campaign).delete()
    db.query(CreatorProfile).delete()
    db.query(AuditEvent).delete()
    db.query(User).delete()
    db.query(Organization).delete()
    db.commit()

    # 1. Organizations
    org_lumen = Organization(
        name="Lumen Skincare",
        org_type="brand",
        settings={"tier": "enterprise", "notifications": True, "country": "IN"},
    )
    org_northlight = Organization(
        name="Northlight Media",
        org_type="agency",
        settings={"tier": "growth", "notifications": True, "country": "IN"},
    )
    db.add_all([org_lumen, org_northlight])
    db.flush()

    pwd = hash_password("Verifyd!2026")

    # 2. Users
    user_lumen_admin = User(
        org_id=org_lumen.id,
        email="admin@lumenskincare.com",
        hashed_password=pwd,
        full_name="Elena Rostova",
        role="company_admin",
    )
    user_lumen_member = User(
        org_id=org_lumen.id,
        email="sarah@lumenskincare.com",
        hashed_password=pwd,
        full_name="Sarah Jenkins",
        role="company_member",
    )
    user_northlight_admin = User(
        org_id=org_northlight.id,
        email="admin@northlightmedia.com",
        hashed_password=pwd,
        full_name="Marcus Vance",
        role="company_admin",
    )
    user_creator_alex = User(
        email="alex@creators.com",
        hashed_password=pwd,
        full_name="Alex Rivers",
        role="creator",
    )
    user_creator_maya = User(
        email="maya@creators.com",
        hashed_password=pwd,
        full_name="Maya Patel",
        role="creator",
    )
    user_creator_rohan = User(
        email="rohan@creators.com",
        hashed_password=pwd,
        full_name="Rohan Sharma",
        role="creator",
    )
    user_platform_admin = User(
        email="ops@verifyd.io",
        hashed_password=pwd,
        full_name="Platform Ops Reviewer",
        role="platform_admin",
    )
    db.add_all([
        user_lumen_admin,
        user_lumen_member,
        user_northlight_admin,
        user_creator_alex,
        user_creator_maya,
        user_creator_rohan,
        user_platform_admin,
    ])
    db.flush()

    # 3. Creator Profiles
    profile_alex = CreatorProfile(
        user_id=user_creator_alex.id,
        handle="alexrivers",
        bio="Skin science & minimalist beauty content creator. Reviewing genuine routines since 2021.",
        primary_language="en",
        niches=["Skincare", "Beauty", "Dermatology"],
        is_verified=True,
        public_id_enabled=True,
    )
    profile_maya = CreatorProfile(
        user_id=user_creator_maya.id,
        handle="mayaskin",
        bio="Ayurvedic beauty, barrier repair, and honest brand reviews.",
        primary_language="en",
        niches=["Clean Beauty", "Lifestyle"],
        is_verified=True,
        public_id_enabled=True,
    )
    profile_rohan = CreatorProfile(
        user_id=user_creator_rohan.id,
        handle="rohancreates",
        bio="Men's grooming, morning routines, and tech reviews.",
        primary_language="en",
        niches=["Men's Grooming", "Fitness"],
        is_verified=False,
        public_id_enabled=True,
    )
    db.add_all([profile_alex, profile_maya, profile_rohan])
    db.flush()

    # 4. Campaigns
    camp_serum = Campaign(
        org_id=org_lumen.id,
        name="Hydration Serum Q3 Global Launch",
        product_name="Lumen Hydration Serum",
        description="Global launch campaign focused on barrier hydration and morning glass-skin routines.",
        starts_on=date(2026, 8, 1),
        ends_on=date(2026, 10, 31),
        status="active",
    )
    camp_spf = Campaign(
        org_id=org_lumen.id,
        name="Sun Shield SPF 50 Summer Push",
        product_name="Invisible Sun Shield SPF 50",
        description="Summertime outdoor creator push emphasizing zero white-cast.",
        starts_on=date(2026, 6, 1),
        ends_on=date(2026, 8, 31),
        status="closed",
    )
    camp_northlight = Campaign(
        org_id=org_northlight.id,
        name="Luxe Cleanse Autumn Campaign",
        product_name="Botanical Oil Cleanser",
        description="Multi-creator influencer campaign highlighting double-cleansing routines.",
        starts_on=date(2026, 9, 1),
        ends_on=date(2026, 11, 30),
        status="active",
    )
    db.add_all([camp_serum, camp_spf, camp_northlight])
    db.flush()

    # 5. Contracts (Including v1 and v2 for Serum Campaign with Alex)
    contract_alex_v1 = Contract(
        campaign_id=camp_serum.id,
        creator_id=profile_alex.id,
        version=1,
        raw_document_key="uploads/contracts/lumen_serum_v1.pdf",
        status="superseded",
        fee_amount=75000.00,
        fee_currency="INR",
    )
    db.add(contract_alex_v1)
    db.flush()

    contract_alex_v2 = Contract(
        campaign_id=camp_serum.id,
        creator_id=profile_alex.id,
        version=2,
        parent_contract_id=contract_alex_v1.id,
        raw_document_key="uploads/contracts/lumen_serum_v2.pdf",
        status="signed",
        fee_amount=85000.00,
        fee_currency="INR",
    )
    contract_maya = Contract(
        campaign_id=camp_serum.id,
        creator_id=profile_maya.id,
        version=1,
        raw_document_key="uploads/contracts/lumen_serum_maya.pdf",
        status="signed",
        fee_amount=50000.00,
        fee_currency="INR",
    )
    contract_rohan = Contract(
        campaign_id=camp_serum.id,
        creator_id=profile_rohan.id,
        version=1,
        raw_document_key="uploads/contracts/lumen_serum_rohan.pdf",
        status="needs_review",  # For demonstrating the clause review screen!
        fee_amount=40000.00,
        fee_currency="INR",
    )
    contract_alex_spf = Contract(
        campaign_id=camp_spf.id,
        creator_id=profile_alex.id,
        version=1,
        raw_document_key="uploads/contracts/lumen_spf_alex.pdf",
        status="signed",
        fee_amount=60000.00,
        fee_currency="INR",
    )
    db.add_all([contract_alex_v2, contract_maya, contract_rohan, contract_alex_spf])
    db.flush()

    # 6. Clauses for Contract Alex v1 & v2 (demonstrating diffs)
    # v1 clauses
    c_v1_1 = Clause(
        contract_id=contract_alex_v1.id,
        ordinal=1,
        clause_ref="C-01",
        source_text="Creator shall speak continuously about the Hydration Serum for a minimum duration of thirty (30) seconds during the sponsorship segment.",
        requirement="Talk about the Hydration Serum for at least 30 seconds",
        clause_type="min_spoken_duration",
        params={"seconds": 30, "subject": "Hydration Serum"},
        modality="audio",
        severity="critical",
        is_auto_checkable=True,
        confidence=0.98,
        review_status="confirmed",
    )
    c_v1_2 = Clause(
        contract_id=contract_alex_v1.id,
        ordinal=2,
        clause_ref="C-02",
        source_text="Creator shall clearly mention the exact brand name 'Lumen Skincare' at least once.",
        requirement="Say 'Lumen Skincare' at least once",
        clause_type="required_phrase",
        params={"phrases": ["Lumen Skincare"], "min_occurrences": 1, "match": "fuzzy"},
        modality="audio",
        severity="critical",
        is_auto_checkable=True,
        confidence=0.96,
        review_status="confirmed",
    )
    c_v1_3 = Clause(
        contract_id=contract_alex_v1.id,
        ordinal=3,
        clause_ref="C-03",
        source_text="The bottle packaging or brand logo must be clearly displayed within the first ten (10) seconds.",
        requirement="Show the logo or bottle in the first 10 seconds",
        clause_type="visual_timing",
        params={"target": "product", "within_seconds": 10, "from": "start"},
        modality="visual",
        severity="standard",
        is_auto_checkable=True,
        confidence=0.94,
        review_status="confirmed",
    )
    db.add_all([c_v1_1, c_v1_2, c_v1_3])

    # v2 clauses (Modified C-02 to 2 occurrences, Added C-04 prohibited, C-05 disclosure, C-06 manual)
    c_v2_1 = Clause(
        contract_id=contract_alex_v2.id,
        ordinal=1,
        clause_ref="C-01",
        source_text="Creator shall speak continuously about the Hydration Serum for a minimum duration of thirty (30) seconds during the sponsorship segment.",
        requirement="Talk about the Hydration Serum for at least 30 seconds",
        clause_type="min_spoken_duration",
        params={"seconds": 30, "subject": "Hydration Serum"},
        modality="audio",
        severity="critical",
        is_auto_checkable=True,
        confidence=0.98,
        review_status="confirmed",
    )
    c_v2_2 = Clause(
        contract_id=contract_alex_v2.id,
        ordinal=2,
        clause_ref="C-02",
        source_text="Creator shall clearly mention the exact brand name 'Lumen Skincare' at least twice throughout the video.",
        requirement="Say 'Lumen Skincare' at least twice",
        clause_type="required_phrase",
        params={"phrases": ["Lumen Skincare"], "min_occurrences": 2, "match": "fuzzy"},
        modality="audio",
        severity="critical",
        is_auto_checkable=True,
        confidence=0.96,
        review_status="confirmed",
    )
    c_v2_3 = Clause(
        contract_id=contract_alex_v2.id,
        ordinal=3,
        clause_ref="C-03",
        source_text="The bottle packaging or brand logo must be clearly displayed within the first ten (10) seconds of the video playback.",
        requirement="Show the logo or bottle in the first 10 seconds",
        clause_type="visual_timing",
        params={"target": "product", "within_seconds": 10, "from": "start"},
        modality="visual",
        severity="standard",
        is_auto_checkable=True,
        confidence=0.94,
        review_status="confirmed",
    )
    c_v2_4 = Clause(
        contract_id=contract_alex_v2.id,
        ordinal=4,
        clause_ref="C-04",
        source_text="Creator must not mention, reference, or visually display any competing skincare brands, specifically GlowLab or DermaPure.",
        requirement="Do not mention competitors (GlowLab, DermaPure)",
        clause_type="prohibited_mention",
        params={"terms": ["GlowLab", "DermaPure"]},
        modality="mixed",
        severity="critical",
        is_auto_checkable=True,
        confidence=0.99,
        review_status="confirmed",
    )
    c_v2_5 = Clause(
        contract_id=contract_alex_v2.id,
        ordinal=5,
        clause_ref="C-05",
        source_text="Creator shall display the product bottle on screen for a cumulative total of at least eight (8) seconds.",
        requirement="Show the product on screen for at least 8 seconds",
        clause_type="visual_presence",
        params={"target": "product", "min_seconds": 8},
        modality="visual",
        severity="standard",
        is_auto_checkable=True,
        confidence=0.92,
        review_status="confirmed",
    )
    c_v2_6 = Clause(
        contract_id=contract_alex_v2.id,
        ordinal=6,
        clause_ref="C-06",
        source_text="Creator must include a clear and conspicuous paid partnership disclosure ('#ad' or 'Paid Partnership') visibly on screen or in the caption within the first 5 seconds.",
        requirement="Include clear paid partnership disclosure (#ad)",
        clause_type="disclosure_tag",
        params={"accepted": ["#ad", "#sponsored", "paid partnership"], "placement": "on_screen_or_caption", "within_seconds": 5},
        modality="text_overlay",
        severity="critical",
        is_auto_checkable=True,
        confidence=0.97,
        review_status="confirmed",
    )
    c_v2_7 = Clause(
        contract_id=contract_alex_v2.id,
        ordinal=7,
        clause_ref="C-07",
        source_text="Creator must ensure high production value and prominent camera framing throughout the video review.",
        requirement="Maintain high production value and prominent framing",
        clause_type="manual_only",
        params={"note": "Subjective production quality requiring human reviewer assessment"},
        modality="visual",
        severity="advisory",
        is_auto_checkable=False,
        confidence=0.45,
        review_status="confirmed",
    )
    db.add_all([c_v2_1, c_v2_2, c_v2_3, c_v2_4, c_v2_5, c_v2_6, c_v2_7])

    # Clauses for Contract Rohan (Needs Review with Amber Pre-Flags)
    c_rohan_1 = Clause(
        contract_id=contract_rohan.id,
        ordinal=1,
        clause_ref="C-01",
        source_text="Creator shall talk about the hydration benefits for at least twenty seconds.",
        requirement="Speak about hydration benefits for 20s",
        clause_type="min_spoken_duration",
        params={"seconds": 20, "subject": "hydration"},
        modality="audio",
        severity="standard",
        is_auto_checkable=True,
        confidence=0.95,
        review_status="unreviewed",
    )
    c_rohan_2 = Clause(
        contract_id=contract_rohan.id,
        ordinal=2,
        clause_ref="C-02",
        source_text="Creator shall prominently feature the bottle during the morning routine.",
        requirement="Prominently feature product in morning routine",
        clause_type="manual_only",
        params={"note": "No measurable second threshold specified in contract text"},
        modality="visual",
        severity="advisory",
        is_auto_checkable=False,
        confidence=0.42,  # Low confidence: amber pre-flag!
        review_status="unreviewed",
    )
    c_rohan_3 = Clause(
        contract_id=contract_rohan.id,
        ordinal=3,
        clause_ref="C-03",
        source_text="Include #ad disclosure clearly in the caption.",
        requirement="Include #ad in caption",
        clause_type="disclosure_tag",
        params={"accepted": ["#ad"]},
        modality="metadata",
        severity="critical",
        is_auto_checkable=True,
        confidence=0.98,
        review_status="unreviewed",
    )
    db.add_all([c_rohan_1, c_rohan_2, c_rohan_3])
    db.flush()

    # 7. Submissions & Reports for Alex v2 (The Star Evidence Timeline Demo!)
    sub_alex_final = Submission(
        contract_id=contract_alex_v2.id,
        contract_version=2,
        creator_id=profile_alex.id,
        kind="final",
        video_file_key="uploads/sample_skincare_review.mp4",
        duration_seconds=30.0,
        caption_text="My daily morning glow step with #ad @lumenskincare Hydration Serum! Check the link in my bio for 20% off your bottle ✨",
        platform_url="https://instagram.com/p/DF931920",
        status="report_ready",
        submitted_at=datetime.now(timezone.utc) - timedelta(hours=3),
        attempt_number=1,
    )
    db.add(sub_alex_final)
    db.flush()

    report_alex = ComplianceReport(
        submission_id=sub_alex_final.id,
        overall_score=94,
        verdict="pass",
        clauses_total=7,
        clauses_passed=6,
        clauses_failed=0,
        clauses_flagged=1,
        model_version="gemini-2.0-flash",
        prompt_version="v1.0.0",
        generated_at=datetime.now(timezone.utc),
        processing_ms=1450,
        cost_estimate_usd=0.00175,
    )
    db.add(report_alex)
    db.flush()

    # Verdicts & Evidence Items for Alex Final Submission
    # C-01 Pass
    v1 = ClauseVerdict(
        report_id=report_alex.id,
        clause_id=c_v2_1.id,
        clause_ref="C-01",
        verdict="pass",
        confidence=0.98,
        rationale="The product is spoken about for 34.2 seconds, meeting the 30.0-second requirement.",
        measured_value={"spoken_seconds": 34.2},
        required_value={"seconds": 30.0},
    )
    db.add(v1)
    db.flush()
    db.add(EvidenceItem(
        verdict_id=v1.id,
        evidence_type="transcript_span",
        start_ms=2100,
        end_ms=28400,
        confidence=0.98,
        payload={"text": "Today is sponsored by Lumen Skincare. I have been testing their new Hydration Serum over the last two weeks, and it honestly gave me that glass-skin glow...", "confidence": 0.98},
    ))

    # C-02 Pass
    v2 = ClauseVerdict(
        report_id=report_alex.id,
        clause_id=c_v2_2.id,
        clause_ref="C-02",
        verdict="pass",
        confidence=0.99,
        rationale="The exact phrase 'Lumen Skincare' was spoken 2 times across the video.",
        measured_value={"occurrences": 2, "phrases_found": ["Lumen Skincare"]},
        required_value={"min_occurrences": 2},
    )
    db.add(v2)
    db.flush()
    db.add_all([
        EvidenceItem(
            verdict_id=v2.id,
            evidence_type="transcript_span",
            start_ms=4100,
            end_ms=5200,
            confidence=0.99,
            payload={"text": "Lumen Skincare", "confidence": 0.99},
        ),
        EvidenceItem(
            verdict_id=v2.id,
            evidence_type="transcript_span",
            start_ms=21700,
            end_ms=22800,
            confidence=0.98,
            payload={"text": "Lumen Skincare", "confidence": 0.98},
        ),
    ])

    # C-03 Pass
    v3 = ClauseVerdict(
        report_id=report_alex.id,
        clause_id=c_v2_3.id,
        clause_ref="C-03",
        verdict="pass",
        confidence=0.95,
        rationale="The product bottle first appeared at 00:03.2, well within the first 10.0 seconds.",
        measured_value={"first_appearance_seconds": 3.2},
        required_value={"within_seconds": 10.0},
    )
    db.add(v3)
    db.flush()
    db.add(EvidenceItem(
        verdict_id=v3.id,
        evidence_type="visual_detection",
        start_ms=3200,
        end_ms=9500,
        confidence=0.95,
        payload={"target": "product", "label": "Hydration Serum Bottle", "bbox": {"x": 0.32, "y": 0.28, "w": 0.36, "h": 0.55}, "confidence": 0.95},
    ))

    # C-04 Pass
    v4 = ClauseVerdict(
        report_id=report_alex.id,
        clause_id=c_v2_4.id,
        clause_ref="C-04",
        verdict="pass",
        confidence=0.99,
        rationale="No mentions or visual logos of competitors (GlowLab, DermaPure) were detected.",
        measured_value={"prohibited_detected": False, "count": 0},
        required_value={"prohibited_terms": ["GlowLab", "DermaPure"]},
    )
    db.add(v4)
    db.flush()
    db.add(EvidenceItem(
        verdict_id=v4.id,
        evidence_type="transcript_span",
        start_ms=0,
        end_ms=30000,
        confidence=0.99,
        payload={"text": "Entire audio verified clean of competitor keywords", "confidence": 0.99},
    ))

    # C-05 Pass
    v5 = ClauseVerdict(
        report_id=report_alex.id,
        clause_id=c_v2_5.id,
        clause_ref="C-05",
        verdict="pass",
        confidence=0.94,
        rationale="The product bottle was visible on screen for 16.5 seconds total, exceeding the 8.0-second requirement.",
        measured_value={"visible_seconds": 16.5},
        required_value={"min_seconds": 8.0},
    )
    db.add(v5)
    db.flush()
    db.add_all([
        EvidenceItem(
            verdict_id=v5.id,
            evidence_type="visual_detection",
            start_ms=3200,
            end_ms=12000,
            confidence=0.95,
            payload={"target": "product", "bbox": {"x": 0.32, "y": 0.28, "w": 0.36, "h": 0.55}, "confidence": 0.95},
        ),
        EvidenceItem(
            verdict_id=v5.id,
            evidence_type="visual_detection",
            start_ms=18000,
            end_ms=25700,
            confidence=0.93,
            payload={"target": "product", "bbox": {"x": 0.28, "y": 0.22, "w": 0.44, "h": 0.58}, "confidence": 0.93},
        ),
    ])

    # C-06 Pass
    v6 = ClauseVerdict(
        report_id=report_alex.id,
        clause_id=c_v2_6.id,
        clause_ref="C-06",
        verdict="pass",
        confidence=0.99,
        rationale="Paid partnership disclosure '#ad' found both on screen at 00:01.0 and in the post caption.",
        measured_value={"on_screen": True, "start_seconds": 1.0, "caption_tag_found": True},
        required_value={"placement": "on_screen_or_caption", "within_seconds": 5},
    )
    db.add(v6)
    db.flush()
    db.add_all([
        EvidenceItem(
            verdict_id=v6.id,
            evidence_type="ocr_text",
            start_ms=1000,
            end_ms=6500,
            confidence=0.99,
            payload={"text": "#ad Paid Partnership with Lumen Skincare", "confidence": 0.99},
        ),
        EvidenceItem(
            verdict_id=v6.id,
            evidence_type="metadata_match",
            start_ms=0,
            end_ms=0,
            confidence=1.0,
            payload={"text": "#ad @lumenskincare", "confidence": 1.0},
        ),
    ])

    # C-07 Flagged (Subjective / Manual only)
    v7 = ClauseVerdict(
        report_id=report_alex.id,
        clause_id=c_v2_7.id,
        clause_ref="C-07",
        verdict="flagged",
        confidence=0.55,
        rationale="Subjective production quality and framing requires human reviewer confirmation.",
        measured_value={"status": "pending_human_review"},
        required_value={"framing": "prominent"},
    )
    db.add(v7)
    db.flush()
    db.add(EvidenceItem(
        verdict_id=v7.id,
        evidence_type="visual_detection",
        start_ms=0,
        end_ms=30000,
        confidence=0.55,
        payload={"target": "framing", "label": "Full Video Frame Review", "confidence": 0.55},
    ))

    # Audit event for Alex review
    db.add(AuditEvent(
        actor_id=user_lumen_admin.id,
        actor_type="user",
        entity_type="submission",
        entity_id=sub_alex_final.id,
        action="submission_created",
        after={"status": "report_ready", "overall_score": 94},
    ))

    # Additional mock submissions across other states
    sub_alex_preflight = Submission(
        contract_id=contract_alex_v2.id,
        contract_version=2,
        creator_id=profile_alex.id,
        kind="preflight",
        video_file_key="uploads/sample_routine.mp4",
        duration_seconds=30.0,
        caption_text="Draft routine test",
        status="report_ready",
        submitted_at=datetime.now(timezone.utc) - timedelta(days=2),
        attempt_number=1,
    )
    db.add(sub_alex_preflight)
    db.flush()

    rep_preflight = ComplianceReport(
        submission_id=sub_alex_preflight.id,
        overall_score=78,
        verdict="needs_review",
        clauses_total=7,
        clauses_passed=5,
        clauses_failed=1,
        clauses_flagged=1,
        model_version="gemini-2.0-flash",
        prompt_version="v1.0.0",
        generated_at=datetime.now(timezone.utc),
        processing_ms=1320,
        cost_estimate_usd=0.0016,
    )
    db.add(rep_preflight)

    # Submission Maya (approved)
    sub_maya = Submission(
        contract_id=contract_maya.id,
        contract_version=1,
        creator_id=profile_maya.id,
        kind="final",
        video_file_key="uploads/sample_unboxing.mp4",
        duration_seconds=30.0,
        caption_text="Loving the hydration serum #ad @lumenskincare",
        status="approved",
        submitted_at=datetime.now(timezone.utc) - timedelta(days=4),
        attempt_number=1,
    )
    db.add(sub_maya)
    db.flush()

    rep_maya = ComplianceReport(
        submission_id=sub_maya.id,
        overall_score=100,
        verdict="pass",
        clauses_total=3,
        clauses_passed=3,
        clauses_failed=0,
        clauses_flagged=0,
        model_version="gemini-2.0-flash",
        prompt_version="v1.0.0",
        generated_at=datetime.now(timezone.utc),
        processing_ms=1100,
        cost_estimate_usd=0.0012,
    )
    db.add(rep_maya)

    # Submission in processing
    sub_proc = Submission(
        contract_id=contract_maya.id,
        contract_version=1,
        creator_id=profile_maya.id,
        kind="preflight",
        video_file_key="uploads/sample_skincare_review.mp4",
        duration_seconds=30.0,
        status="processing",
        submitted_at=datetime.now(timezone.utc) - timedelta(minutes=10),
        attempt_number=2,
    )
    db.add(sub_proc)

    # Submission with changes requested
    sub_changes = Submission(
        contract_id=contract_alex_spf.id,
        contract_version=1,
        creator_id=profile_alex.id,
        kind="final",
        video_file_key="uploads/sample_routine.mp4",
        duration_seconds=30.0,
        caption_text="Summer SPF essentials",
        status="changes_requested",
        submitted_at=datetime.now(timezone.utc) - timedelta(days=15),
        attempt_number=1,
    )
    db.add(sub_changes)

    # Submission failed with error
    sub_failed = Submission(
        contract_id=contract_alex_spf.id,
        contract_version=1,
        creator_id=profile_alex.id,
        kind="final",
        video_file_key="uploads/sample_unboxing.mp4",
        duration_seconds=30.0,
        status="failed",
        submitted_at=datetime.now(timezone.utc) - timedelta(days=16),
        attempt_number=2,
    )
    db.add(sub_failed)

    # Pipeline Job entries
    db.add_all([
        Job(submission_id=sub_alex_final.id, task_name="score_submission", status="succeeded", started_at=datetime.now(timezone.utc) - timedelta(hours=3), finished_at=datetime.now(timezone.utc) - timedelta(hours=3, minutes=-1)),
        Job(submission_id=sub_maya.id, task_name="score_submission", status="succeeded", started_at=datetime.now(timezone.utc) - timedelta(days=4), finished_at=datetime.now(timezone.utc) - timedelta(days=4, minutes=-1)),
        Job(submission_id=sub_proc.id, task_name="transcribe", status="running", started_at=datetime.now(timezone.utc) - timedelta(minutes=5)),
        Job(submission_id=sub_failed.id, task_name="score_submission", status="failed", error_class="CorruptMediaHeaderError", error_message="Container audio stream missing valid timestamps", attempt=3, max_attempts=3),
    ])

    db.commit()
    db.close()

    print("\n==================================================================")
    print("VERIFYD SEED DATA POPULATED SUCCESSFULLY!")
    print("==================================================================")
    print("Test User Accounts (Password for all: Verifyd!2026):")
    print("  1. Brand Admin:       admin@lumenskincare.com   (Company Admin)")
    print("  2. Brand Member:      sarah@lumenskincare.com   (Company Member)")
    print("  3. Agency Admin:      admin@northlightmedia.com (Agency Admin)")
    print("  4. Verified Creator:  alex@creators.com         (Handle: alexrivers)")
    print("  5. Creator:           maya@creators.com         (Handle: mayaskin)")
    print("  6. Creator:           rohan@creators.com        (Handle: rohancreates)")
    print("  7. Platform Admin:    ops@verifyd.io            (Platform Admin)")
    print("==================================================================\n")


if __name__ == "__main__":
    seed()
