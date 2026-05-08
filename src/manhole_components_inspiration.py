from __future__ import annotations

import math


def _part(
    part_id: str,
    name: str,
    quantity: float,
    unit: str,
    **extra,
) -> dict:
    result = {
        "part_id": part_id,
        "name": name,
        "quantity": round(float(quantity), 3),
        "unit": unit,
    }
    result.update(extra)
    return result


def split_manhole_into_components(
    cci_type: str | None,
    diameter_mm: int | None,
    materiale: str | None,
    depth_m: float | None,
) -> list[dict]:
    """
    Inspireret af vores egentlige stykliste-logik.

    Hovedideen er:
    - bundstykke nederst
    - et antal skaktringe i midten
    - eventuel reduktionskegle
    - justeringsringe
    - dæksel/ramme øverst
    """
    if not cci_type:
        return []

    diameter = int(diameter_mm or 1000)
    depth = float(depth_m or 1.5)
    material = (materiale or "Beton").upper()
    is_pp = material in {"PP", "PE", "PVC", "PLAST"}

    parts: list[dict] = []

    if is_pp:
        reserved_height = 0.20
        ring_height = 0.50
        shaft_height = max(0.0, depth - reserved_height)
        ring_count = max(1, math.ceil(shaft_height / ring_height))

        parts.append(
            _part(
                f"bund-pp-{diameter}",
                f"Bundstykke PP o{diameter}",
                1,
                "stk",
                materiale="PP",
            )
        )
        parts.append(
            _part(
                f"skaktring-pp-{diameter}",
                f"Skaktring PP o{diameter} h500",
                ring_count,
                "stk",
                materiale="PP",
            )
        )
        parts.append(
            _part(
                f"justering-pp-{diameter}",
                f"Justeringsring PP o{diameter}",
                1,
                "stk",
                materiale="PP",
            )
        )
        parts.append(
            _part(
                "daeksel-pp",
                "Daeksel og rammesaet",
                1,
                "saet",
                materiale="GGG/PP",
            )
        )
        return parts

    has_cone = diameter >= 1000
    reserved_height = 0.20 + (0.60 + 0.16 if has_cone else 0.16)
    shaft_height = max(0.0, depth - reserved_height)
    ring_count = max(1, math.ceil(shaft_height / 1.0))

    parts.append(
        _part(
            f"bund-beton-{diameter}",
            f"Bundstykke beton o{diameter}",
            1,
            "stk",
            materiale="Beton",
        )
    )
    parts.append(
        _part(
            f"skaktring-beton-{diameter}",
            f"Skaktring beton o{diameter} h1000",
            ring_count,
            "stk",
            materiale="Beton",
        )
    )

    if has_cone:
        parts.append(
            _part(
                f"reduktionskegle-{diameter}",
                f"Reduktionskegle o{diameter}-o700",
                1,
                "stk",
                materiale="Beton",
            )
        )

    parts.append(
        _part(
            "justeringsring-beton",
            "Justeringsringe",
            2,
            "stk",
            materiale="Beton",
        )
    )
    parts.append(
        _part(
            "daeksel-beton",
            "Daeksel og rammesaet",
            1,
            "saet",
            materiale="GGG",
        )
    )
    return parts


def build_offer_lines(row: dict) -> list[dict]:
    """
    Den enkle tilbudsliste-ide: komponenter er også mængdelinjer.
    """
    if row.get("kind") == "knude":
        return split_manhole_into_components(
            cci_type=row.get("cci_type"),
            diameter_mm=row.get("diameter_mm"),
            materiale=row.get("materiale"),
            depth_m=row.get("depth_m"),
        )

    if row.get("kind") == "ledning":
        length_m = float(row.get("length_m") or 0.0)
        diameter = int(row.get("diameter_indv_mm") or 200)
        material = row.get("materiale") or "PP"
        segment_length = 3.0 if material.upper() in {"PP", "PE", "PVC"} else 2.5
        segment_count = max(1, math.ceil(length_m / segment_length))
        coupling_count = max(0, segment_count - 1)
        lines = [
            _part(
                f"roer-{diameter}",
                f"Roer o{diameter}",
                segment_count,
                "stk",
                materiale=material,
            )
        ]
        if coupling_count:
            lines.append(
                _part(
                    f"samling-{diameter}",
                    f"Samlinger o{diameter}",
                    coupling_count,
                    "stk",
                    materiale=material,
                )
            )
        if str(row.get("cci_type") or "").startswith("WMF"):
            lines.append(
                _part(
                    "geotekstil",
                    "Geotekstil omkring draen",
                    length_m,
                    "m",
                    materiale="PP-filt",
                )
            )
        return lines

    return []

