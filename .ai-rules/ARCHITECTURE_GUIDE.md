# ARCHITECTURE GUIDE FOR AI

## Project Structure

```
RCM_PRICE/
├── app/                    # FastAPI application layer
│   ├── main.py            # Application entry point
│   └── routers/           # API route handlers
│       ├── pricing.py     # Pricing endpoints
│       └── health.py      # Health check endpoints
│
├── domain/                # Business logic (core domain)
│   ├── entities/          # Business entities
│   │   ├── product.py     # Product entity
│   │   ├── customer.py    # Customer entity
│   │   └── order.py       # Order entity
│   ├── value_objects/     # Immutable value objects
│   │   ├── price.py       # Price value object
│   │   └── discount.py    # Discount value object
│   └── services/          # Domain services
│       ├── pricing_service.py      # Core pricing logic
│       └── demand_service.py       # Demand calculation
│
├── application/           # Application logic layer
│   ├── commands/          # Command objects (CQRS)
│   │   ├── update_price_command.py
│   │   └── generate_discount_command.py
│   └── use_cases/         # Use case implementations
│       ├── optimize_pricing_use_case.py
│       └── forecast_demand_use_case.py
│
├── infrastructure/        # External concerns
│   ├── db/               # Database implementations
│   │   ├── models.py     # SQLAlchemy models
│   │   └── repositories.py # Data access layer
│   ├── ml_models/        # Trained AI models
│   │   ├── demand_predictor.pkl
│   │   └── price_optimizer.pkl
│   ├── external/         # External API integrations
│   │   └── competitor_api.py
│   └── schedulers/       # Background tasks
│       └── price_update_scheduler.py
│
├── data/                 # Data storage
│   ├── raw/             # Raw data files
│   ├── processed/       # Cleaned data
│   └── reports/         # Analysis reports
│
├── notebooks/           # Jupyter notebooks for experiments
├── scripts/             # Utility scripts
├── tests/               # Test files
├── configs/             # Configuration files
└── docs/                # Documentation
```

## Layer Responsibilities

### 1. Domain Layer (`domain/`)

- **Purpose:** Contains core business logic
- **Rules:**
  - No external dependencies
  - Pure business logic only
  - Framework agnostic
- **Components:**
  - Entities: Core business objects
  - Value Objects: Immutable values
  - Services: Complex business operations

### 2. Application Layer (`application/`)

- **Purpose:** Orchestrates domain objects
- **Rules:**
  - Uses domain layer
  - No framework dependencies
  - Contains use cases and commands
- **Components:**
  - Use Cases: Application workflows
  - Commands: Request/response objects

### 3. Infrastructure Layer (`infrastructure/`)

- **Purpose:** External system integrations
- **Rules:**
  - Implements domain interfaces
  - Contains all external dependencies
  - Database, APIs, ML models
- **Components:**
  - Database repositories
  - ML model handlers
  - External API clients

### 4. App Layer (`app/`)

- **Purpose:** Web framework specific code
- **Rules:**
  - Depends on application layer
  - FastAPI specific implementations
  - HTTP request/response handling

## Dependency Rules

- **Domain** depends on nothing
- **Application** depends on Domain only
- **Infrastructure** depends on Domain and Application
- **App** depends on all layers

## Data Flow

1. HTTP Request → App Layer (routers)
2. App Layer → Application Layer (use cases)
3. Application Layer → Domain Layer (business logic)
4. Domain Layer → Infrastructure Layer (data access)
5. Response flows back through the layers
