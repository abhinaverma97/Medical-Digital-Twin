class ISO62366UsabilityChecks:
    """
    Usability engineering checks aligned to ISO 62366-1.

    Rules enforced:
    - Every interface requirement must have a non-empty description
      (supports intended use documentation)
    - Every interface requirement must specify a protocol
      (required for IEC 62366 use specification)
    - Regulatory requirements must cite an applicable standard
    """

    def evaluate(self, requirements):
        issues = []

        for req in requirements:
            if req.type == "interface":
                if not req.description or not req.description.strip():
                    issues.append(
                        f"{req.id}: Interface requirement missing description "
                        "(required for use specification under ISO 62366-1)"
                    )
                if not req.protocol:
                    issues.append(
                        f"{req.id}: Interface requirement missing protocol "
                        "(required for interface specification)"
                    )

            if req.type == "regulatory":
                if not req.standard:
                    issues.append(
                        f"{req.id}: Regulatory requirement must cite an applicable standard"
                    )

        status = "FAIL" if issues else "PASS"
        return status, issues