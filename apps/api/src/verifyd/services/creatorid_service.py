from typing import Any, Dict, Optional
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from verifyd.db.models.creator_profile import CreatorProfile
from verifyd.db.models.submission import Submission
from verifyd.db.models.compliance_report import ComplianceReport
from verifyd.schemas.creator import CreatorIDResponse


async def compute_creator_metrics(session: AsyncSession, creator_profile: CreatorProfile) -> CreatorIDResponse:
    """Computes CreatorID portable metrics: pass rate, campaigns completed, average revisions."""
    # Submissions query
    sub_query = (
        select(Submission)
        .where(Submission.creator_id == creator_profile.id, Submission.deleted_at.is_(None))
    )
    res = await session.execute(sub_query)
    submissions = res.scalars().all()

    total_submissions = len(submissions)
    if total_submissions == 0:
        return CreatorIDResponse(
            handle=creator_profile.handle,
            full_name=creator_profile.user.full_name if creator_profile.user else creator_profile.handle,
            bio=creator_profile.bio,
            avatar_url=creator_profile.user.avatar_url if creator_profile.user else None,
            is_verified=creator_profile.is_verified,
            pass_rate=100.0,
            campaigns_completed=0,
            average_revisions=1.0,
            total_submissions=0,
            public_id_enabled=creator_profile.public_id_enabled,
            niches=creator_profile.niches or [],
            primary_language=creator_profile.primary_language,
        )

    # Calculate pass rate based on approved or passed reports
    approved_or_passed = sum(1 for s in submissions if s.status == "approved" or (s.report and s.report.verdict == "pass"))
    pass_rate = round((approved_or_passed / total_submissions) * 100.0, 1)

    # Unique campaigns completed
    unique_contracts = set(s.contract_id for s in submissions if s.status == "approved")
    campaigns_completed = len(unique_contracts)

    # Average attempts/revisions per contract
    attempts = [s.attempt_number for s in submissions]
    avg_revisions = round(sum(attempts) / len(attempts), 1) if attempts else 1.0

    return CreatorIDResponse(
        handle=creator_profile.handle,
        full_name=creator_profile.user.full_name if creator_profile.user else creator_profile.handle,
        bio=creator_profile.bio,
        avatar_url=creator_profile.user.avatar_url if creator_profile.user else None,
        is_verified=creator_profile.is_verified,
        pass_rate=pass_rate,
        campaigns_completed=campaigns_completed,
        average_revisions=avg_revisions,
        total_submissions=total_submissions,
        public_id_enabled=creator_profile.public_id_enabled,
        niches=creator_profile.niches or [],
        primary_language=creator_profile.primary_language,
    )
