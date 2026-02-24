"""
Penalties business logic.
Logica de negocios de penalidades.
"""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, NotFoundException
from app.drivers.models import Driver
from app.penalties.models import Penalty
from app.races.models import Race
from app.results.models import RaceResult
from app.teams.models import Team


async def list_penalties_by_race(db: AsyncSession, race_id: uuid.UUID) -> list[Penalty]:
    """
    List all penalties for a race, ordered by created_at.
    Lista todas as penalidades de uma corrida, ordenadas por created_at.
    """
    race_query = await db.execute(select(Race).where(Race.id == race_id))
    if race_query.scalar_one_or_none() is None:
        raise NotFoundException("Race not found")

    stmt = select(Penalty).where(Penalty.race_id == race_id).order_by(Penalty.created_at)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_penalty_by_id(db: AsyncSession, penalty_id: uuid.UUID) -> Penalty:
    """
    Get a penalty by ID. Raises NotFoundException if not found.
    Busca uma penalidade por ID. Lanca NotFoundException se nao encontrada.
    """
    result = await db.execute(select(Penalty).where(Penalty.id == penalty_id))
    penalty = result.scalar_one_or_none()
    if penalty is None:
        raise NotFoundException("Penalty not found")
    return penalty


async def _sync_dsq_flag(db: AsyncSession, result_id: uuid.UUID | None, set_dsq: bool) -> None:
    """
    Sync the DSQ flag on a race result.
    If unsetting, checks for other active DSQ penalties first.

    Sincroniza a flag DSQ em um resultado de corrida.
    Se desativando, verifica outras penalidades DSQ ativas primeiro.
    """
    if result_id is None:
        return

    result_query = await db.execute(select(RaceResult).where(RaceResult.id == result_id))
    race_result = result_query.scalar_one_or_none()
    if race_result is None:
        return

    if set_dsq:
        race_result.dsq = True
    else:
        # Check for other active DSQ penalties on the same result
        # Verifica outras penalidades DSQ ativas no mesmo resultado
        other_dsq = await db.execute(
            select(Penalty).where(
                Penalty.result_id == result_id,
                Penalty.penalty_type == "disqualification",
                Penalty.is_active == True,  # noqa: E712
            )
        )
        if other_dsq.scalar_one_or_none() is None:
            race_result.dsq = False


async def create_penalty(
    db: AsyncSession,
    race_id: uuid.UUID,
    team_id: uuid.UUID,
    penalty_type: str,
    reason: str,
    points_deducted: float = 0.0,
    time_penalty_seconds: int | None = None,
    lap_number: int | None = None,
    driver_id: uuid.UUID | None = None,
    result_id: uuid.UUID | None = None,
) -> Penalty:
    """
    Create a penalty. Validates race, team, driver, result.
    DSQ sync: if type=disqualification AND result_id AND is_active -> set result.dsq=True.

    Cria uma penalidade. Valida corrida, equipe, piloto, resultado.
    Sinc DSQ: se tipo=disqualification E result_id E is_active -> define result.dsq=True.
    """
    # Validate race exists / Valida que a corrida existe
    race_query = await db.execute(select(Race).where(Race.id == race_id))
    if race_query.scalar_one_or_none() is None:
        raise NotFoundException("Race not found")

    # Validate team exists / Valida que a equipe existe
    team_query = await db.execute(select(Team).where(Team.id == team_id))
    if team_query.scalar_one_or_none() is None:
        raise NotFoundException("Team not found")

    # Validate driver if provided / Valida piloto se fornecido
    if driver_id is not None:
        driver_query = await db.execute(select(Driver).where(Driver.id == driver_id))
        if driver_query.scalar_one_or_none() is None:
            raise NotFoundException("Driver not found")

    # Validate result if provided / Valida resultado se fornecido
    if result_id is not None:
        result_query = await db.execute(select(RaceResult).where(RaceResult.id == result_id))
        race_result = result_query.scalar_one_or_none()
        if race_result is None:
            raise NotFoundException("Race result not found")
        if race_result.race_id != race_id:
            raise ConflictException("Race result does not belong to this race")

    penalty = Penalty(
        race_id=race_id,
        team_id=team_id,
        driver_id=driver_id,
        result_id=result_id,
        penalty_type=penalty_type,
        reason=reason,
        points_deducted=points_deducted,
        time_penalty_seconds=time_penalty_seconds,
        lap_number=lap_number,
    )
    db.add(penalty)
    await db.flush()

    # DSQ sync / Sincronizacao DSQ
    if penalty_type == "disqualification" and result_id is not None:
        await _sync_dsq_flag(db, result_id, set_dsq=True)

    await db.commit()
    await db.refresh(penalty)
    return penalty


async def update_penalty(
    db: AsyncSession,
    penalty: Penalty,
    penalty_type: str | None = None,
    reason: str | None = None,
    points_deducted: float | None = None,
    time_penalty_seconds: int | None = None,
    lap_number: int | None = None,
    result_id: uuid.UUID | None = None,
    driver_id: uuid.UUID | None = None,
    is_active: bool | None = None,
) -> Penalty:
    """
    Update penalty fields. Handles DSQ sync for type transitions.
    Atualiza campos da penalidade. Gerencia sinc DSQ para transicoes de tipo.
    """
    old_type = penalty.penalty_type
    old_result_id = penalty.result_id
    old_is_active = penalty.is_active

    if reason is not None:
        penalty.reason = reason
    if points_deducted is not None:
        penalty.points_deducted = points_deducted
    if time_penalty_seconds is not None:
        penalty.time_penalty_seconds = time_penalty_seconds
    if lap_number is not None:
        penalty.lap_number = lap_number
    if result_id is not None:
        penalty.result_id = result_id
    if driver_id is not None:
        penalty.driver_id = driver_id
    if penalty_type is not None:
        penalty.penalty_type = penalty_type
    if is_active is not None:
        penalty.is_active = is_active

    new_type = penalty.penalty_type
    new_result_id = penalty.result_id
    new_is_active = penalty.is_active

    await db.flush()

    # DSQ sync on type/active transitions / Sinc DSQ em transicoes de tipo/ativo
    was_active_dsq = old_type == "disqualification" and old_is_active
    is_active_dsq = new_type == "disqualification" and new_is_active

    if was_active_dsq and not is_active_dsq:
        # Was DSQ, no longer is -> revert old result / Era DSQ, nao e mais -> reverter resultado antigo
        await _sync_dsq_flag(db, old_result_id, set_dsq=False)
    if not was_active_dsq and is_active_dsq:
        # Wasn't DSQ, now is -> set new result / Nao era DSQ, agora e -> definir novo resultado
        await _sync_dsq_flag(db, new_result_id, set_dsq=True)
    if was_active_dsq and is_active_dsq and old_result_id != new_result_id:
        # Result changed but still DSQ -> revert old, set new / Resultado mudou mas ainda DSQ
        await _sync_dsq_flag(db, old_result_id, set_dsq=False)
        await _sync_dsq_flag(db, new_result_id, set_dsq=True)

    await db.commit()
    await db.refresh(penalty)
    return penalty


async def delete_penalty(db: AsyncSession, penalty: Penalty) -> None:
    """
    Delete a penalty. Reverts DSQ flag if needed.
    Exclui uma penalidade. Reverte flag DSQ se necessario.
    """
    result_id = penalty.result_id
    was_active_dsq = penalty.penalty_type == "disqualification" and penalty.is_active

    await db.delete(penalty)
    await db.flush()

    # DSQ revert / Reversao DSQ
    if was_active_dsq:
        await _sync_dsq_flag(db, result_id, set_dsq=False)

    await db.commit()
