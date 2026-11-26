---
name: ashishps1-awesome-low-level-design
description: Learn Low Level Design (LLD) and prepare for interviews using free resources.
source: https://github.com/ashishps1/awesome-low-level-design
license: GPL-3.0
stars: 28257
language: Java
topics: awesome, design-patterns, interview, interview-practice, interview-questions, lld, low-level-design, machine-coding, object-oriented-programming, oops, solid-principles, uml
saved: 2026-11-26
---

# Awesome Low-Level Design (LLD) & Machine Coding

A practical reference guide and toolkit for mastering Low-Level Design (LLD), Object-Oriented Design (OOD), Gang of Four (GoF) design patterns, SOLID principles, and machine coding interview challenges.

---

## When to use

Use this skill when you need to:
- **Solve Machine Coding Interview Rounds:** Structure and implement end-to-end object-oriented problems (e.g., Parking Lot, Splitwise, Elevator System, Snake and Ladder, Rate Limiter, Tic-Tac-Toe, Movie Ticket Booking System).
- **Apply Object-Oriented Principles (OOP & SOLID):** Refactor monolithic or tightly coupled code using Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, and Dependency Inversion principles.
- **Select & Implement GoF Design Patterns:** Determine and implement appropriate patterns (e.g., Strategy, Factory, Observer, Decorator, State, Chain of Responsibility, Singleton).
- **Model Class Relationships & UML Diagrams:** Accurately represent class structures using Association, Aggregation, Composition, Inheritance, and Dependency in UML or Mermaid.
- **Design Thread-Safe In-Memory Systems:** Ensure concurrency safety using thread-safe data structures, synchronization primitives, and lock mechanisms in OOP systems.

---

## How to use

### 1. Standard LLD Problem-Solving Workflow

Follow this 5-step approach when addressing LLD and machine coding prompts:

1. **Clarify Requirements & Scope:**
   - Define functional requirements (core actions) and non-functional requirements (thread safety, extensibility, memory bounds).
2. **Identify Core Entities & Models:**
   - Extract primary domain models and value objects (e.g., `User`, `ParkingSlot`, `Vehicle`, `Ticket`).
3. **Map Relationships & Choose Design Patterns:**
   - Establish relationships (e.g., `ParkingLot` *has-a* list of `ParkingFloor` via Composition).
   - Inject behavioral variations using patterns (e.g., `FeeCalculationStrategy`, `PaymentStrategy`).
4. **Define Interfaces & Contracts:**
   - Program to interfaces rather than concrete implementations to uphold DIP and OCP.
5. **Implement with Thread Safety & Extensibility:**
   - Utilize thread-safe collections (`ConcurrentHashMap`, `CopyOnWriteArrayList`) or locking mechanisms where concurrent access is possible.

---

### 2. Utilizing `lld_diagram_helper.py`

Use the included helper script `lld_diagram_helper.py` to generate, parse, or validate UML class diagrams and structural layouts.

```bash
# Display help and available options
python3 lld_diagram_helper.py --help

# Generate a Mermaid class diagram from a Java package or directory
python3 lld_diagram_helper.py generate --source ./repo/parking-lot --format mermaid

# Validate class relationships and detect cyclic dependencies
python3 lld_diagram_helper.py validate --source ./repo/splitwise

# Export an existing model schema to PlantUML
python3 lld_diagram_helper.py export --model ./schema.json --format plantuml --output diagram.puml
```

---

### 3. Common Design Pattern Blueprints (Java)

#### Strategy Pattern (Dynamic Behavior / Policies)
```java
public interface PricingStrategy {
    double calculateCost(long durationMinutes);
}

public class HourlyPricingStrategy implements PricingStrategy {
    @Override
    public double calculateCost(long durationMinutes) {
        return Math.ceil(durationMinutes / 60.0) * 20.0;
    }
}
```

#### State Pattern (Lifecycle Management)
```java
public interface VendingMachineState {
    void insertCoin(VendingMachine machine, double amount);
    void selectProduct(VendingMachine machine, String code);
    void dispense(VendingMachine machine);
}
```

#### Observer Pattern (Event Notification)
```java
public interface NotificationObserver {
    void onUpdate(String message);
}

public class OrderSubject {
    private final List<NotificationObserver> observers = new CopyOnWriteArrayList<>();

    public void addObserver(NotificationObserver observer) { observers.add(observer); }
    public void notifyObservers(String msg) { observers.forEach(o -> o.onUpdate(msg)); }
}
```

---

## Limitations

- **Scope is strictly Low-Level (OOD/LLD):** Does not cover High-Level Design (HLD) topics such as distributed consensus, CDN placement, CAP theorem, or data replication across database clusters.
- **Language Bias:** Core reference implementations and patterns are written in Java; adaptations to dynamically typed or non-class-based languages (e.g., Go, Python, JavaScript) require idiom translation.
- **In-Memory Assumptions:** Machine coding solutions in this repository operate primarily on in-memory data structures and do not integrate external storage engines (SQL/NoSQL) or ORM layers out of the box.
- **External Dependencies:** Some markdown guides link to external web resources and articles which may be unavailable in offline or air-gapped environments.