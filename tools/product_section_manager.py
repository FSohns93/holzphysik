#!/usr/bin/env python3
"""
Pflegt Produktdaten in JSON und rendert den Produktbereich in die HTML-Seiten zurück.

Aufruf:
    python tools/product_section_manager.py
"""

from __future__ import annotations

import html
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "product_sections"

PAGES = {
    "schneidebretter": {
        "label": "Schneidebretter",
        "html": ROOT / "produkte" / "schneidebretter.html",
        "data": DATA_DIR / "schneidebretter.json",
        "marker": "schneidebretter",
    },
    "pflegeprodukte": {
        "label": "Pflegeprodukte",
        "html": ROOT / "produkte" / "pflegeprodukte.html",
        "data": DATA_DIR / "pflegeprodukte.json",
        "marker": "pflegeprodukte",
    },
    "photon-cuts": {
        "label": "Photon Cuts",
        "html": ROOT / "produkte" / "photon-cuts.html",
        "data": DATA_DIR / "photon_cuts.json",
        "marker": "photon-cuts",
    },
}


def prompt(message: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    value = input(f"{message}{suffix}: ").strip()
    return value if value else default


def prompt_bool(message: str, default: bool = True) -> bool:
    default_text = "j" if default else "n"
    while True:
        value = input(f"{message} [j/n] [{default_text}]: ").strip().lower()
        if not value:
            return default
        if value in {"j", "ja", "y", "yes"}:
            return True
        if value in {"n", "nein", "no"}:
            return False
        print("Bitte mit j oder n antworten.")


def choose_page_key() -> str:
    print("Welche Produktseite möchtest du pflegen?")
    keys = list(PAGES.keys())
    for index, key in enumerate(keys, start=1):
        print(f"  {index}. {PAGES[key]['label']} ({key})")

    while True:
        value = input("Auswahl: ").strip()
        if value.isdigit():
            number = int(value)
            if 1 <= number <= len(keys):
                return keys[number - 1]
        if value in PAGES:
            return value
        print("Bitte eine gültige Zahl oder einen bekannten Schlüssel eingeben.")


def load_page_data(page_key: str) -> dict:
    path = PAGES[page_key]["data"]
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_page_data(page_key: str, data: dict) -> None:
    path = PAGES[page_key]["data"]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
        file.write("\n")


def list_products(products: list[dict]) -> None:
    if not products:
        print("Noch keine Produkte vorhanden.")
        return

    for index, product in enumerate(products, start=1):
        print(f"{index}. {product['name']} | {product['price']} | {product['image']}")


def get_meta_value(meta_rows: list[dict], label: str, default: str = "") -> str:
    for row in meta_rows:
        if row.get("label") == label:
            return row.get("value", default)
    return default


def set_standard_meta_rows(meta_rows: list[dict]) -> list[dict]:
    fokus = prompt("Fokus", get_meta_value(meta_rows, "Fokus"))
    format_value = prompt("Format", get_meta_value(meta_rows, "Format"))
    status = prompt("Status", get_meta_value(meta_rows, "Status"))
    return [
        {"label": "Fokus", "value": fokus},
        {"label": "Format", "value": format_value},
        {"label": "Status", "value": status},
    ]


def edit_product(product: dict | None = None) -> dict:
    current = dict(product or {})
    current.setdefault("product_classes", ["product"])
    current.setdefault("wrap_classes", ["product-image-wrap"])
    current.setdefault("badge", "")
    current.setdefault("image", "")
    current.setdefault("image_alt", "")
    current.setdefault("name", "")
    current.setdefault("price", "")
    current.setdefault("description", "")
    current.setdefault("meta_rows", [])
    current.setdefault("cta", {"label": "Anfragen", "href": "#kontakt", "data_product": ""})

    print("\nProdukt bearbeiten")
    current["price"] = prompt("Preistext", current["price"])
    current["description"] = prompt("Beschreibung", current["description"])
    current["meta_rows"] = set_standard_meta_rows(current["meta_rows"])
    return current


def duplicate_product_template(products: list[dict]) -> dict:
    print("\nVorlage für neues Produkt wählen:")
    list_products(products)
    idx = int(prompt("Welche Nummer als Vorlage nutzen", "1")) - 1
    if not (0 <= idx < len(products)):
        raise ValueError("Ungültige Vorlagen-Nummer.")
    template = json.loads(json.dumps(products[idx]))
    print("\nNeue Produktkarte basiert auf:")
    print(f"  {template['name']} | {template['image']}")
    print("Name, Bild, Badge, CSS-Klassen und CTA werden aus der Vorlage übernommen.")
    return template


def render_product_card(product: dict) -> str:
    product_classes = " ".join(product["product_classes"])
    wrap_classes = " ".join(product["wrap_classes"])
    badge_html = f'\n            <span class="product-badge">{html.escape(product["badge"])}</span>' if product["badge"] else ""
    meta_html = "\n".join(
        "            <div class=\"meta-row\">\n"
        f"              <span>{html.escape(row['label'])}</span>\n"
        f"              <strong>{html.escape(row['value'])}</strong>\n"
        "            </div>"
        for row in product["meta_rows"]
    )
    cta = product["cta"]
    data_product_attr = f' data-product="{html.escape(cta["data_product"])}"' if cta.get("data_product") else ""

    return (
        f"      <article class=\"{product_classes}\">\n"
        f"        <div class=\"{wrap_classes}\">\n"
        f"          <img src=\"{html.escape(product['image'])}\" alt=\"{html.escape(product['image_alt'])}\">{badge_html}\n"
        "        </div>\n\n"
        "        <div class=\"product-content\">\n"
        "          <div class=\"product-top\">\n"
        f"            <h3>{product['name']}</h3>\n"
        f"            <span class=\"price\">{html.escape(product['price'])}</span>\n"
        "          </div>\n\n"
        "          <p>\n"
        f"            {html.escape(product['description'])}\n"
        "          </p>\n\n"
        "          <div class=\"meta\">\n"
        f"{meta_html}\n"
        "          </div>\n\n"
        "          <div class=\"product-actions\">\n"
        f"            <a class=\"btn\" href=\"{html.escape(cta['href'])}\"{data_product_attr}>{html.escape(cta['label'])}</a>\n"
        "          </div>\n"
        "        </div>\n"
        "      </article>"
    )


def render_products_section(products: list[dict]) -> str:
    cards = "\n\n".join(render_product_card(product) for product in products)
    return f"<div class=\"products\">\n{cards}\n    </div>"


def replace_section_in_html(page_key: str, rendered_section: str) -> None:
    page = PAGES[page_key]
    html_path = page["html"]
    marker = page["marker"]
    start_marker = f"<!-- PRODUCT_SECTION_START: {marker} -->"
    end_marker = f"<!-- PRODUCT_SECTION_END: {marker} -->"

    html_text = html_path.read_text(encoding="utf-8")
    pattern = re.compile(
        rf"{re.escape(start_marker)}.*?{re.escape(end_marker)}",
        re.DOTALL,
    )
    replacement = f"{start_marker}\n{rendered_section}\n    {end_marker}"
    updated_text, count = pattern.subn(replacement, html_text, count=1)

    if count != 1:
        raise RuntimeError(f"Marker für {marker} nicht eindeutig gefunden in {html_path}.")

    html_path.write_text(updated_text, encoding="utf-8")


def manage_products(page_key: str) -> None:
    data = load_page_data(page_key)
    products = list(data["products"])

    while True:
        print("\nAktuelle Produkte:")
        list_products(products)
        action = input("\nAktion: [a]dd, [e]dit, [d]elete, [r]ender, [q]uit: ").strip().lower()

        if action in {"q", "quit"}:
            print("Abgebrochen.")
            return

        if action in {"a", "add"}:
            if not products:
                print("Es ist keine Vorlage vorhanden. Bitte zuerst ein bestehendes Produkt anlegen.")
                continue
            template = duplicate_product_template(products)
            products.append(edit_product(template))
            continue

        if action in {"e", "edit"} and products:
            idx = int(prompt("Welche Nummer bearbeiten", "1")) - 1
            if 0 <= idx < len(products):
                products[idx] = edit_product(products[idx])
            continue

        if action in {"d", "delete"} and products:
            idx = int(prompt("Welche Nummer löschen", "1")) - 1
            if 0 <= idx < len(products):
                removed = products.pop(idx)
                print(f"Gelöscht: {removed['name']}")
            continue

        if action in {"r", "render"}:
            data["products"] = products
            save_page_data(page_key, data)
            rendered = render_products_section(products)
            print("\nVorschau des erzeugten HTML-Blocks:\n")
            print(rendered)
            print()
            if prompt_bool("HTML-Datei jetzt überschreiben?", True):
                replace_section_in_html(page_key, rendered)
                print(f"{PAGES[page_key]['html']} wurde aktualisiert.")
            else:
                print("Nur JSON gespeichert, HTML nicht überschrieben.")
            return

        print("Ungültige Eingabe.")


def main() -> None:
    page_key = choose_page_key()
    manage_products(page_key)


if __name__ == "__main__":
    main()
