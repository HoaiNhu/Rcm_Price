# CODING STANDARDS FOR AI

## File Structure Rules

1. **Follow Clean Architecture pattern**

   - `domain/` - Business logic only
   - `application/` - Use cases and commands
   - `infrastructure/` - External dependencies
   - `app/` - Framework specific code

2. **Naming Conventions**

   - Files: snake_case (e.g., `pricing_service.py`)
   - Classes: PascalCase (e.g., `PriceOptimizer`)
   - Functions/Variables: snake_case (e.g., `calculate_price`)
   - Constants: UPPER_SNAKE_CASE (e.g., `MAX_DISCOUNT_RATE`)

3. **Import Organization**
   - Standard library imports first
   - Third-party imports second
   - Local application imports last
   - Use absolute imports when possible

## Code Quality Rules

1. **Type Hints Required**

   - All function parameters must have type hints
   - All function return types must be specified
   - Use `Optional[T]` for nullable values

2. **Docstring Standards**

   - All public classes and functions need docstrings
   - Use Google-style docstrings
   - Include Args, Returns, and Raises sections

3. **Error Handling**

   - Use specific exception types, not generic Exception
   - Always log errors with appropriate level
   - Handle edge cases explicitly

4. **Testing Requirements**
   - Minimum 80% code coverage
   - Unit tests for all business logic
   - Integration tests for API endpoints
   - Mock external dependencies

## AI Model Development Rules

1. **Data Processing**

   - Raw data goes in `data/raw/`
   - Processed data goes in `data/processed/`
   - Always validate data before training

2. **Model Management**

   - Save trained models in `infrastructure/ml_models/`
   - Version control model files
   - Include model metadata (accuracy, training date, etc.)

3. **Experimentation**
   - Use Jupyter notebooks for exploration only
   - Production code must be in Python modules
   - Document experiment results

## Performance Rules

1. **Database Queries**

   - Use connection pooling
   - Implement query optimization
   - Add database indexes for frequently accessed data

2. **API Response Times**

   - Target < 200ms for simple queries
   - Target < 1s for complex pricing calculations
   - Implement caching where appropriate

3. **Memory Usage**
   - Use generators for large datasets
   - Implement pagination for API responses
   - Clean up resources explicitly
