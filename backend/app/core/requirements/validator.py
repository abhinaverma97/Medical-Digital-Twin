import re

# Requirement ID pattern: REQ-<DEVICE>-<OPTIONAL-TAGS>-<NUMBER>
# Supports REQ-VENT-001, REQ-VENT-INT-001, REQ-DIAL-REG-999
_ID_PATTERN = re.compile(r"^REQ(?:-[A-Z0-9]+)+-\d{3,}$")


def validate_requirement(req) -> list[str]:
    """
    Validates a single Requirement against VitaBlueprint's structured rules.
    Rules are deterministic, requirement-type-aware, and ISO-aligned.
    Returns a list of error strings; empty list means valid.
    """
    errors = []

    # ── 1. ID format ──────────────────────────────────────────────────
    if not _ID_PATTERN.match(req.id):
        errors.append(
            f"Invalid ID '{req.id}': must match REQ-<DEVICE>-<NNN> "
            "(e.g. REQ-VENT-001, REQ-POX-012)"
        )

    # ── 2. Every requirement must be assigned to a subsystem ──────────
    if not req.subsystem or not req.subsystem.strip():
        errors.append(
            f"{req.id}: 'subsystem' is required for all requirement types "
            "(needed for design graph construction and traceability)"
        )

    # ── 3. Type-specific mandatory fields ──────────────────────────────
    if req.type in ("functional", "performance"):
        if not req.parameter:
            errors.append(
                f"{req.id}: functional/performance requirement must define 'parameter'"
            )

    if req.type == "performance":
        has_limits = (req.min_value is not None or req.max_value is not None
                      or req.response_time_ms is not None)
        if not has_limits:
            errors.append(
                f"{req.id}: performance requirement must define at least one "
                "measurable limit (min_value, max_value, or response_time_ms)"
            )
        if (req.min_value is not None or req.max_value is not None) and not req.unit:
            errors.append(
                f"{req.id}: performance requirement with numeric limits must specify 'unit'"
            )

    if req.type == "interface":
        if not req.interface:
            errors.append(
                f"{req.id}: interface requirement must define 'interface' "
                "in format 'SourceSubsystem -> TargetSubsystem'"
            )
        if not req.protocol:
            errors.append(
                f"{req.id}: interface requirement must specify 'protocol' "
                "(e.g. SPI, I2C, CAN, UART, RS-232)"
            )
        if not req.parameter:
            errors.append(
                f"{req.id}: interface requirement must define 'parameter' "
                "(the signal or data element crossing the interface)"
            )

    if req.type == "safety":
        if not req.hazard:
            errors.append(f"{req.id}: safety requirement must define 'hazard'")
        if not req.severity:
            errors.append(f"{req.id}: safety requirement must define 'severity'")
        # High and Critical hazards require traceability to an ISO standard
        if req.severity in ("High", "Critical"):
            if not req.standard:
                errors.append(
                    f"{req.id}: High/Critical safety requirement must cite "
                    "'standard' (e.g. ISO 14971)"
                )
            if not req.clause:
                errors.append(
                    f"{req.id}: High/Critical safety requirement must cite "
                    "'clause' (e.g. 4.3.1)"
                )

    if req.type == "regulatory":
        if not req.standard:
            errors.append(
                f"{req.id}: regulatory requirement must cite 'standard'"
            )
        if not req.clause:
            errors.append(
                f"{req.id}: regulatory requirement must cite 'clause'"
            )

    # ── 4. Numeric consistency ─────────────────────────────────────────
    if req.min_value is not None and req.max_value is not None:
        if req.min_value >= req.max_value:
            errors.append(
                f"{req.id}: min_value ({req.min_value}) must be strictly less than "
                f"max_value ({req.max_value})"
            )

    if req.tolerance is not None and req.tolerance <= 0:
        errors.append(
            f"{req.id}: tolerance must be a positive value"
        )

    if req.response_time_ms is not None and req.response_time_ms <= 0:
        errors.append(
            f"{req.id}: response_time_ms must be a positive integer"
        )

    # ── 5. Verification always required ───────────────────────────────
    if not req.verification:
        errors.append(f"{req.id}: verification block is required for all requirements")

    return errors