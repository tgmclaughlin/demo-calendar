# CLAUDE.md - AI Helper Reference Guide

## Build & Test Commands
- Install: `pip install -e .`
- Run app: `python run.py`
- Lint: `black app/`
- Type check: `mypy app/`

## Code Style Guidelines
- **Imports**: Group standard library, third-party, and local imports in separate blocks
- **Formatting**: Use Black formatter with 88 character line limit
- **Types**: Use type hints for all function parameters and return values
- **Naming**: snake_case for functions/variables, PascalCase for classes, UPPER_CASE for constants
- **Error Handling**: Use specific FastAPI HTTP exceptions with clear error messages
- **API Structure**: Maintain clean separation between routes, models, and database logic
- **Frontend**: Keep JavaScript well-organized with clear state management
- **Documentation**: Include docstrings for all functions and endpoints

## Project Structure
- FastAPI app with SQLite for persistence
- Single-file UI implementation with a clean, modern design
- Database models in app/models/database.py
- API schemas in app/models/schemas.py