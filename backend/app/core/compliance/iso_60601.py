class ISO60601SafetyChecks:
    """
    ISO 60601-1:2005+AMD1:2012 — General requirements for basic safety
    and essential performance.

    Checks are derived from requirements and the design graph.
    No subsystem names are hardcoded.

    Rules enforced:
    1. Every subsystem in the design graph must be backed by at least
       one requirement (orphan subsystem = traceability gap).
    2. Every safety requirement with High or Critical severity must be
       mitigated by at least one functional or safety requirement in
       the SAME subsystem (i.e. the subsystem has a defined control).
    3. High/Critical hazards must have at least one associated alarm
       or monitoring requirement anywhere in the system
       (essential performance per IEC 60601-1-8).
    4. All performance requirements must carry measurable limits and units.
    """

    def evaluate(self, design_graph, requirements):
        violations = []

        req_subsystems = {r.subsystem for r in requirements if r.subsystem}

        # ── Rule 1: every design-graph subsystem must be requirement-backed ──
        for subsystem_name in design_graph.subsystems:
            if subsystem_name not in req_subsystems:
                violations.append(
                    f"Subsystem '{subsystem_name}' has no associated requirements "
                    "(orphan subsystem — traceability gap per ISO 60601-1 §4.2)"
                )

        # ── Rule 2: High/Critical hazards → mitigation requirement in subsystem ──
        high_critical = [
            r for r in requirements
            if r.type == "safety" and r.severity in ("High", "Critical")
        ]
        for hazard_req in high_critical:
            subsystem = hazard_req.subsystem
            # Check that at least one functional/safety requirement also addresses
            # this subsystem (i.e. the subsystem has a defined control action)
            controls = [
                r for r in requirements
                if r.subsystem == subsystem
                and r.type in ("functional", "safety")
                and r.id != hazard_req.id
            ]
            if not controls:
                violations.append(
                    f"Hazard '{hazard_req.hazard}' ({hazard_req.id}) in subsystem "
                    f"'{subsystem}' has no associated control/functional requirement "
                    "(ISO 60601-1 §9 — risk control measures must be specified)"
                )

        # ── Rule 3: High/Critical hazards require alarm/monitoring coverage ──
        if high_critical:
            alarm_reqs = [
                r for r in requirements
                if r.type in ("functional", "safety")
                and any(
                    keyword in (r.title + " " + r.description).lower()
                    for keyword in ("alarm", "alert", "monitor", "detect", "notify")
                )
            ]
            if not alarm_reqs:
                violations.append(
                    "High/Critical hazards exist but no alarm or monitoring requirement "
                    "is defined anywhere in the system "
                    "(required by IEC 60601-1-8 — Alarm systems)"
                )

        # ── Rule 4: Performance requirements must carry measurable limits + unit ──
        for req in requirements:
            if req.type == "performance":
                has_limits = (
                    req.min_value is not None
                    or req.max_value is not None
                    or req.response_time_ms is not None
                )
                if not has_limits:
                    violations.append(
                        f"{req.id}: performance requirement has no measurable limit — "
                        "essential performance must be quantified (ISO 60601-1 §4.4)"
                    )
                if (req.min_value is not None or req.max_value is not None) and not req.unit:
                    violations.append(
                        f"{req.id}: performance requirement with numeric limits is "
                        "missing 'unit' — units are mandatory (ISO 60601-1 §5.4)"
                    )

        status = "FAIL" if violations else "PASS"
        return status, violations