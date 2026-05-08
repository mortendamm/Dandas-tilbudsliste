from __future__ import annotations

from pathlib import Path
from pprint import pprint

from banebyg_link_inspiration import explain_link
from dandas_parser_inspiration import parse_knuder, parse_ledninger
from manhole_components_inspiration import build_offer_lines


def main() -> None:
    base = Path(__file__).resolve().parent.parent
    knude_xml = base / "demo" / "Knude.synthetic.xml"
    ledning_xml = base / "demo" / "Ledning.synthetic.xml"

    knuder = parse_knuder(str(knude_xml))
    ledninger = parse_ledninger(str(ledning_xml))

    print("=== Parsed knuder ===")
    pprint(knuder)
    print()

    print("=== Parsed ledninger ===")
    pprint(ledninger)
    print()

    if knuder:
        print("=== CCI -> BaneByg for første knude ===")
        pprint(explain_link(knuder[0]))
        print()

        print("=== Komponenter / tilbudslinje for første knude ===")
        pprint(build_offer_lines(knuder[0]))
        print()

    if ledninger:
        print("=== CCI -> BaneByg for første ledning ===")
        pprint(explain_link(ledninger[0]))
        print()

        print("=== Komponenter / tilbudslinje for første ledning ===")
        pprint(build_offer_lines(ledninger[0]))
        print()


if __name__ == "__main__":
    main()

