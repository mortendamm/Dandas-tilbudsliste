from __future__ import annotations


"""
Meget lille og læsbar udgave af CCI -> BaneByg-linket.

I produktionsløsningen læser vi også fra mapping-ark.
Her viser vi kun princippet.
"""


CCI_TO_BANEBYG = {
    "WMG01": [
        {
            "code": "5.3.1.1",
            "beskrivelse": "Gennemlobsbrond, PP, o600",
            "enhed": "stk",
        }
    ],
    "WMG02": [
        {
            "code": "5.3.2.1",
            "beskrivelse": "Gennemlobsbrond, beton, o1000",
            "enhed": "stk",
        }
    ],
    "WMG13": [
        {
            "code": "5.4.1.3",
            "beskrivelse": "Sandfangsbrond, PP, o600",
            "enhed": "stk",
        }
    ],
    "WMF02": [
        {
            "code": "5.1.2.1",
            "beskrivelse": "Draenror, PP, o200",
            "enhed": "m",
        }
    ],
    "WPA02": [
        {
            "code": "5.2.2.1",
            "beskrivelse": "Taet ledning, PP, o200",
            "enhed": "m",
        }
    ],
}


def get_banebyg_for_cci(cci_type: str | None) -> list[dict]:
    if not cci_type:
        return []
    return CCI_TO_BANEBYG.get(cci_type, [])


def explain_link(row: dict) -> dict:
    """
    Returnerer en lille forklaring på hvordan vi tænker koblingen.
    """
    cci_type = row.get("cci_type")
    return {
        "source_name": row.get("name"),
        "source_kind": row.get("kind"),
        "cci_type": cci_type,
        "banebyg_posts": get_banebyg_for_cci(cci_type),
    }

