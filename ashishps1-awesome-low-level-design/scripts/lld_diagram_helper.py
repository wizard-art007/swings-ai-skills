#!/usr/bin/env python3
"""
LLD Diagram Helper for Low-Level Design and Object-Oriented Modeling.

Converts short textual descriptions and shorthand relationships into
PlantUML and Mermaid class diagrams, with built-in interview design
patterns and Kroki rendering / URL generation support.
"""

import argparse
import base64
import re
import sys
import zlib
from typing import Dict, List, Optional
import requests


# Pre-built Low-Level Design (LLD) interview templates
LLD_TEMPLATES: Dict[str, Dict[str, str]] = {
    "strategy": {
        "title": "Strategy Pattern - Payment Processing",
        "description": (
            "interface PaymentStrategy {\n"
            "  +pay(amount: double): bool\n"
            "}\n"
            "class CreditCardPayment {\n"
            "  -cardNumber: String\n"
            "  +pay(amount: double): bool\n"
            "}\n"
            "class UpiPayment {\n"
            "  -vpaId: String\n"
            "  +pay(amount: double): bool\n"
            "}\n"
            "class ShoppingCart {\n"
            "  -paymentStrategy: PaymentStrategy\n"
            "  +setPaymentStrategy(strategy: PaymentStrategy): void\n"
            "  +checkout(amount: double): bool\n"
            "}\n"
            "CreditCardPayment ..|> PaymentStrategy : implements\n"
            "UpiPayment ..|> PaymentStrategy : implements\n"
            "ShoppingCart o-- PaymentStrategy : uses"
        ),
    },
    "observer": {
        "title": "Observer Pattern - Weather Monitoring Station",
        "description": (
            "interface Observer {\n"
            "  +update(temp: float, humidity: float): void\n"
            "}\n"
            "interface Subject {\n"
            "  +registerObserver(o: Observer): void\n"
            "  +removeObserver(o: Observer): void\n"
            "  +notifyObservers(): void\n"
            "}\n"
            "class WeatherStation {\n"
            "  -observers: List<Observer>\n"
            "  -temperature: float\n"
            "  -humidity: float\n"
            "  +setMeasurements(t: float, h: float): void\n"
            "}\n"
            "class PhoneDisplay {\n"
            "  +update(temp: float, humidity: float): void\n"
            "}\n"
            "class WindowDisplay {\n"
            "  +update(temp: float, humidity: float): void\n"
            "}\n"
            "WeatherStation ..|> Subject : implements\n"
            "PhoneDisplay ..|> Observer : implements\n"
            "WindowDisplay ..|> Observer : implements\n"
            "WeatherStation o-- Observer : notifies"
        ),
    },
    "factory": {
        "title": "Factory Pattern - Notification Service",
        "description": (
            "interface Notification {\n"
            "  +sendUser(message: String): void\n"
            "}\n"
            "class EmailNotification {\n"
            "  +sendUser(message: String): void\n"
            "}\n"
            "class SMSNotification {\n"
            "  +sendUser(message: String): void\n"
            "}\n"
            "class NotificationFactory {\n"
            "  +createNotification(channel: String): Notification\n"
            "}\n"
            "EmailNotification ..|> Notification : implements\n"
            "SMSNotification ..|> Notification : implements\n"
            "NotificationFactory ..> Notification : creates"
        ),
    },
    "singleton": {
        "title": "Singleton Pattern - Database Connection Pool",
        "description": (
            "class DatabasePool {\n"
            "  -DatabasePool instance$ \n"
            "  -DatabasePool()\n"
            "  +getInstance(): DatabasePool$\n"
            "  +getConnection(): Connection\n"
            "}"
        ),
    },
    "decorator": {
        "title": "Decorator Pattern - Coffee Customizer",
        "description": (
            "interface Coffee {\n"
            "  +getCost(): double\n"
            "  +getDescription(): String\n"
            "}\n"
            "class SimpleCoffee {\n"
            "  +getCost(): double\n"
            "  +getDescription(): String\n"
            "}\n"
            "class CoffeeDecorator {\n"
            "  #decoratedCoffee: Coffee\n"
            "  +getCost(): double\n"
            "  +getDescription(): String\n"
            "}\n"
            "class MilkDecorator {\n"
            "  +getCost(): double\n"
            "  +getDescription(): String\n"
            "}\n"
            "SimpleCoffee ..|> Coffee : implements\n"
            "CoffeeDecorator ..|> Coffee : implements\n"
            "CoffeeDecorator o-- Coffee : wraps\n"
            "MilkDecorator --|> CoffeeDecorator : extends"
        ),
    },
    "parking_lot": {
        "title": "LLD - Parking Lot System",
        "description": (
            "class ParkingLot {\n"
            "  -String name\n"
            "  -List<ParkingFloor> floors\n"
            "  +parkVehicle(Vehicle v): Ticket\n"
            "  +vacateSpot(Ticket t): double\n"
            "}\n"
            "class ParkingFloor {\n"
            "  -int floorNumber\n"
            "  -List<ParkingSpot> spots\n"
            "  +findAvailableSpot(VehicleType type): ParkingSpot\n"
            "}\n"
            "class ParkingSpot {\n"
            "  -int spotId\n"
            "  -bool isFree\n"
            "  -Vehicle currentVehicle\n"
            "  +assignVehicle(Vehicle v): void\n"
            "  +removeVehicle(): void\n"
            "}\n"
            "class Vehicle {\n"
            "  -String licensePlate\n"
            "  -VehicleType type\n"
            "}\n"
            "class Car {\n"
            "}\n"
            "class Bike {\n"
            "}\n"
            "class Ticket {\n"
            "  -String ticketId\n"
            "  -long entryTime\n"
            "  -ParkingSpot spot\n"
            "}\n"
            "ParkingLot *-- ParkingFloor : contains\n"
            "ParkingFloor *-- ParkingSpot : contains\n"
            "ParkingSpot o-- Vehicle : parks\n"
            "Car --|> Vehicle : is-a\n"
            "Bike --|> Vehicle : is-a\n"
            "ParkingLot ..> Ticket : generates"
        ),
    },
    "tic_tac_toe": {
        "title": "LLD - Tic Tac Toe Game",
        "description": (
            "class TicTacToeGame {\n"
            "  -Board board\n"
            "  -Deque<Player> players\n"
            "  +initializeGame(): void\n"
            "  +startGame(): String\n"
            "}\n"
            "class Board {\n"
            "  -int size\n"
            "  -PlayingPiece[][] grid\n"
            "  +addPiece(row: int, col: int, piece: PlayingPiece): bool\n"
            "  +printBoard(): void\n"
            "}\n"
            "class Player {\n"
            "  -String name\n"
            "  -PlayingPiece piece\n"
            "}\n"
            "class PlayingPiece {\n"
            "  -PieceType pieceType\n"
            "}\n"
            "class PieceX {\n"
            "}\n"
            "class PieceO {\n"
            "}\n"
            "TicTacToeGame *-- Board : has\n"
            "TicTacToeGame o-- Player : manages\n"
            "Player *-- PlayingPiece : holds\n"
            "PieceX --|> PlayingPiece : is-a\n"
            "PieceO --|> PlayingPiece : is-a"
        ),
    },
}

# Mapping natural shorthand keywords to UML relationship symbols
RELATION_KEYWORDS = [
    (r"\bextends\b", "--|>"),
    (r"\bis-a\b", "--|>"),
    (r"\bimplements\b", "..|>"),
    (r"\bcontains\b", "*--"),
    (r"\bcomposes\b", "*--"),
    (r"\bhas-a\b", "o--"),
    (r"\baggregates\b", "o--"),
    (r"\buses\b", "..>"),
    (r"\bdepends-on\b", "..>"),
    (r"\bassociates-with\b", "-->"),
]


class KrokiError(Exception):
    """Raised when rendering via Kroki fails."""
    pass


def encode_kroki(source: str) -> str:
    """Encode diagram text using Kroki's deflate + base64url format."""
    compressed = zlib.compress(source.encode("utf-8"), 9)
    return base64.urlsafe_b64encode(compressed).decode("ascii")


def get_kroki_url(
    diagram_source: str,
    diagram_type: str = "plantuml",
    output_format: str = "svg",
    base_url: str = "https://kroki.io",
) -> str:
    """Generate a Kroki shareable URL for the diagram."""
    encoded = encode_kroki(diagram_source)
    return f"{base_url.rstrip('/')}/{diagram_type}/{output_format}/{encoded}"


def render_kroki(
    diagram_source: str,
    diagram_type: str = "plantuml",
    output_format: str = "svg",
    base_url: str = "https://kroki.io",
    timeout: int = 15,
) -> bytes:
    """Render diagram source to binary output (e.g. SVG or PNG) via Kroki POST."""
    url = f"{base_url.rstrip('/')}/{diagram_type}/{output_format}"
    try:
        response = requests.post(
            url,
            data=diagram_source.encode("utf-8"),
            headers={"Content-Type": "text/plain; charset=utf-8"},
            timeout=timeout,
        )
    except requests.RequestException as exc:
        raise KrokiError(f"Network error while connecting to Kroki at {url}: {exc}") from exc

    if response.status_code != 200:
        error_msg = response.text.strip() or f"HTTP {response.status_code}"
        raise KrokiError(f"Kroki rendering failed ({response.status_code}): {error_msg}")

    return response.content


def parse_dsl_to_elements(text: str):
    """
    Parse shorthand text / DSL lines into title, body lines, and normalized relationships.
    """
    lines = text.strip().splitlines()
    title: Optional[str] = None
    processed_lines: List[str] = []

    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue

        # Check for title
        title_match = re.match(r"^title[:\s]+(.+)$", line, re.IGNORECASE)
        if title_match and title is None:
            title = title_match.group(1).strip()
            continue

        # Ignore standalone comments starting with # or //
        if line.startswith("#") or line.startswith("//"):
            continue

        # Convert natural keywords if arrow is not present
        if not any(sym in line for sym in ["--|>", "<|--", "..|>", "<|..", "*--", "--*", "o--", "--o", "-->", "<--", "..>", "<.."]):
            for pattern, symbol in RELATION_KEYWORDS:
                # e.g.: "Car extends Vehicle : inherits" -> "Car --|> Vehicle : inherits"
                matched = re.search(pattern, line, re.IGNORECASE)
                if matched:
                    line = re.sub(pattern, symbol, line, count=1, flags=re.IGNORECASE)
                    break

        processed_lines.append(line)

    return title, processed_lines


def to_plantuml(text: str, default_title: Optional[str] = None) -> str:
    """Convert input DSL or text description to a PlantUML class diagram."""
    title, lines = parse_dsl_to_elements(text)
    active_title = title or default_title

    out = ["@startuml"]
    out.append("skinparam classAttributeIconSize 0")
    if active_title:
        out.append(f"title {active_title}")

    for line in lines:
        out.append(line)

    out.append("@enduml")
    return "\n".join(out)


def to_mermaid(text: str, default_title: Optional[str] = None) -> str:
    """Convert input DSL or text description to a Mermaid class diagram."""
    title, lines = parse_dsl_to_elements(text)
    active_title = title or default_title

    out = []
    if active_title:
        out.append("---")
        out.append(f"title: {active_title}")
        out.append("---")

    out.append("classDiagram")
    for line in lines:
        out.append(f"  {line}")

    return "\n".join(out)


def get_template(name: str) -> Dict[str, str]:
    """Retrieve an interview design template by key."""
    key = name.lower().replace("-", "_")
    if key not in LLD_TEMPLATES:
        available = ", ".join(sorted(LLD_TEMPLATES.keys()))
        raise KeyError(f"Unknown template '{name}'. Available: {available}")
    return LLD_TEMPLATES[key]


def list_templates() -> List[str]:
    """Return sorted list of available interview design template names."""
    return sorted(LLD_TEMPLATES.keys())


def generate_diagram(
    source_text: str,
    target_format: str = "plantuml",
    default_title: Optional[str] = None,
) -> str:
    """Generate PlantUML or Mermaid diagram source from input text."""
    fmt = target_format.lower().strip()
    if fmt == "plantuml":
        return to_plantuml(source_text, default_title=default_title)
    elif fmt == "mermaid":
        return to_mermaid(source_text, default_title=default_title)
    else:
        raise ValueError(f"Unsupported format '{target_format}'. Choose 'plantuml' or 'mermaid'.")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="LLD Diagram Helper: Convert OOP/LLD descriptions into PlantUML/Mermaid and render with Kroki."
    )
    parser.add_argument(
        "-t", "--template",
        help="Use a pre-built LLD template (e.g. strategy, observer, parking_lot, singleton, tic_tac_toe, etc.) or 'list' to show all."
    )
    parser.add_argument(
        "-i", "--input",
        help="Path to file containing diagram text / DSL description."
    )
    parser.add_argument(
        "--text",
        help="Inline text / DSL description."
    )
    parser.add_argument(
        "-f", "--format",
        choices=["plantuml", "mermaid"],
        default="plantuml",
        help="Target diagram syntax (default: plantuml)."
    )
    parser.add_argument(
        "-o", "--output",
        help="Save output to file instead of printing to stdout."
    )
    parser.add_argument(
        "--kroki-url",
        action="store_true",
        help="Generate and print Kroki URL for the diagram."
    )
    parser.add_argument(
        "--render",
        metavar="EXT",
        help="Render diagram via Kroki to format (svg, png, pdf) and output binary/save to -o."
    )
    parser.add_argument(
        "--endpoint",
        default="https://kroki.io",
        help="Kroki endpoint (default: https://kroki.io)."
    )
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    if args.template == "list":
        print("Available LLD templates:")
        for t in list_templates():
            info = LLD_TEMPLATES[t]
            print(f"  - {t}: {info['title']}")
        return 0

    source_text = ""
    default_title = None

    if args.template:
        try:
            tmpl = get_template(args.template)
            source_text = tmpl["description"]
            default_title = tmpl["title"]
        except KeyError as err:
            sys.stderr.write(f"Error: {err}\n")
            return 1
    elif args.input:
        try:
            with open(args.input, "r", encoding="utf-8") as f:
                source_text = f.read()
        except OSError as err:
            sys.stderr.write(f"Error reading file '{args.input}': {err}\n")
            return 1
    elif args.text:
        source_text = args.text
    else:
        # Check if stdin has data
        if not sys.stdin.isatty():
            source_text = sys.stdin.read()
        else:
            parser.print_help()
            return 1

    if not source_text.strip():
        sys.stderr.write("Error: Diagram description is empty.\n")
        return 1

    try:
        diagram_code = generate_diagram(source_text, target_format=args.format, default_title=default_title)
    except Exception as exc:
        sys.stderr.write(f"Error generating diagram: {exc}\n")
        return 1

    if args.kroki_url:
        url = get_kroki_url(diagram_code, diagram_type=args.format, output_format="svg", base_url=args.endpoint)
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(url + "\n")
        else:
            print(url)
        return 0

    if args.render:
        try:
            rendered = render_kroki(
                diagram_code,
                diagram_type=args.format,
                output_format=args.render,
                base_url=args.endpoint,
            )
            if args.output:
                with open(args.output, "wb") as f:
                    f.write(rendered)
            else:
                sys.stdout.buffer.write(rendered)
            return 0
        except KrokiError as exc:
            sys.stderr.write(f"Render error: {exc}\n")
            return 1

    # Output diagram source
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(diagram_code + "\n")
    else:
        print(diagram_code)

    return 0


if __name__ == "__main__":
    sys.exit(main())
