from __future__ import annotations

import xml.etree.ElementTree as ET


MATERIALE_KODE = {
    "1": "Beton",
    "17": "PP",
    "18": "PE",
    "19": "PVC",
    "20": "PP",
}

KNUDE_KODE = {
    "1": "Brond",
    "7": "Sandfang",
}

TYPE_AFLOEB_KODE = {
    "1": "Spildevand",
    "2": "Regnvand",
    "4": "Draen",
    "5": "Trykledning",
}


def _text(el: ET.Element, tag: str) -> str | None:
    node = el.find(tag)
    if node is None or node.text is None:
        return None
    value = node.text.strip()
    return value or None


def _number(el: ET.Element, tag: str) -> float | None:
    value = _text(el, tag)
    if value is None:
        return None
    try:
        return float(value)
    except ValueError:
        return None


def map_knude_cci(
    knude_kode: str | None,
    materiale_kode: str | None,
    diameter_mm: float | None,
    type_afloeb_kode: str | None,
) -> tuple[str, str | None]:
    """
    Reduceret version af vores DANDAS -> CCI-regler for knuder.

    Ideen er:
    - afgør først om vi har sandfang eller almindelig brønd
    - afgør derefter materiale og diameter
    - returner en CCI klasse og en konkret typekode
    """
    materiale = MATERIALE_KODE.get(str(materiale_kode or ""), "Ukendt")
    is_plastic = materiale in {"PP", "PE", "PVC", "Plast"}
    diameter = int(diameter_mm or 0)
    knude = str(knude_kode or "")
    afloeb = str(type_afloeb_kode or "")

    if knude == "7" or (knude == "1" and afloeb == "4" and diameter <= 600):
        if is_plastic:
            return ("WMG", "WMG13")
        return ("WMG", "WMG14")

    if knude == "1":
        if is_plastic:
            return ("WMG", "WMG01")
        if diameter <= 1000:
            return ("WMG", "WMG02")
        return ("WMG", "WMG03")

    return ("WMG", None)


def map_ledning_cci(
    materiale_kode: str | None,
    diameter_mm: float | None,
    type_afloeb_kode: str | None,
) -> tuple[str, str | None]:
    """
    Reduceret version af vores DANDAS -> CCI-regler for ledninger.
    """
    materiale = MATERIALE_KODE.get(str(materiale_kode or ""), "Ukendt")
    is_plastic = materiale in {"PP", "PE", "PVC", "Plast"}
    diameter = int(diameter_mm or 0)
    afloeb = str(type_afloeb_kode or "")

    if afloeb == "5":
        if diameter <= 200:
            return ("WPA", "WPA02")
        return ("WPA", "WPA04")

    if is_plastic:
        if diameter <= 160:
            return ("WMF", "WMF01")
        if diameter <= 200:
            return ("WMF", "WMF02")
        return ("WMF", "WMF03")

    return ("WPA", "WPA08")


def parse_knuder(xml_path: str) -> list[dict]:
    """
    Læser kun de felter, vi behøver for at forstå resten af flowet.
    """
    root = ET.parse(xml_path).getroot()
    rows: list[dict] = []

    for knude in root.findall("Knude"):
        name = knude.get("Knudenavn") or _text(knude, "Knudenavn") or "UkendtKnude"
        knude_kode = _text(knude, "KnudeKode")
        materiale_kode = _text(knude, "MaterialeKode")
        type_afloeb_kode = _text(knude, "TypeAfloebKode")
        bundkote = _number(knude, "Bundkote")
        terraenkote = _number(knude, "Terraenkote")
        diameter_mm = _number(knude, "DiameterBredde")
        x = _number(knude, "XKoordinat")
        y = _number(knude, "YKoordinat")
        depth_m = None
        if bundkote is not None and terraenkote is not None:
            depth_m = round(terraenkote - bundkote, 3)

        cci_class, cci_type = map_knude_cci(
            knude_kode=knude_kode,
            materiale_kode=materiale_kode,
            diameter_mm=diameter_mm,
            type_afloeb_kode=type_afloeb_kode,
        )

        rows.append(
            {
                "kind": "knude",
                "name": name,
                "knude_type": KNUDE_KODE.get(str(knude_kode or ""), "Ukendt"),
                "materiale": MATERIALE_KODE.get(str(materiale_kode or ""), "Ukendt"),
                "type_afloeb": TYPE_AFLOEB_KODE.get(str(type_afloeb_kode or ""), "Ukendt"),
                "diameter_mm": diameter_mm,
                "bundkote": bundkote,
                "terraenkote": terraenkote,
                "depth_m": depth_m,
                "x": x,
                "y": y,
                "cci_class": cci_class,
                "cci_type": cci_type,
            }
        )

    return rows


def parse_ledninger(xml_path: str) -> list[dict]:
    root = ET.parse(xml_path).getroot()
    rows: list[dict] = []

    for ledning in root.findall("Ledning"):
        name = ledning.get("Ledningsnavn") or _text(ledning, "Ledningsnavn")
        fra_knude = ledning.get("OpstroemKnudenavn") or _text(ledning, "FraKnude")
        til_knude = ledning.get("NedstroemKnudenavn") or _text(ledning, "TilKnude")
        materiale_kode = _text(ledning, "MaterialeKode")
        type_afloeb_kode = _text(ledning, "TypeAfloebKode")
        diameter_mm = _number(ledning, "DiameterIndv")
        length_m = _number(ledning, "Laengde")
        if name is None:
            name = f"{fra_knude}->{til_knude}"

        cci_class, cci_type = map_ledning_cci(
            materiale_kode=materiale_kode,
            diameter_mm=diameter_mm,
            type_afloeb_kode=type_afloeb_kode,
        )

        rows.append(
            {
                "kind": "ledning",
                "name": name,
                "fra_knude": fra_knude,
                "til_knude": til_knude,
                "materiale": MATERIALE_KODE.get(str(materiale_kode or ""), "Ukendt"),
                "type_afloeb": TYPE_AFLOEB_KODE.get(str(type_afloeb_kode or ""), "Ukendt"),
                "diameter_indv_mm": diameter_mm,
                "length_m": length_m,
                "cci_class": cci_class,
                "cci_type": cci_type,
            }
        )

    return rows

