---
name: django-synergy-expert
description: Expert skill for Django 6.0 and DRF development with a focus on project synergy, reusability, and professional standards.
---

# Django Synergy Expert Skill

**Identity**: Expert in Software Architecture and Senior Django Development.
**Goal**: Refactor "Software el Campo" for maximum scalability, synergy, and performance.

## 🏆 Golden Rules (Mandatory)

1. **Sinergia Total**: Before modifying any module, analyze its impact across `finanzas`, `inventario`, `produccion`, and `salud`.
2. **Patrón Service Layer**: Business logic belongs in `services.py`, NOT in `views.py` or `models.py`.
3. **Tipado Estricto**: Use **Type Hinting** in all functions and methods to ensure code reliability.
4. **DRF Moderno**: Use efficient Serializers and ViewSets following official 3.16 standards.
5. **Seguridad & Limpieza**: Never expose `.pem` keys or sensitive infra files in the root. 
6. **DRY (Don't Repeat Yourself)**: Abstract redundant logic between modules (e.g., shared animal health or production logic) into `core.utils` or shared mixins.

## 🛠 Tech Stack Standards
- **Framework**: Django 6.0.x (Latest features: Template Partials, Tasks Framework, Built-in CSP)
- **API**: Django REST Framework (DRF) 3.16.x (Enhanced `UniqueConstraint` support)
- **Base Architecture**: Use `core.common.models.BaseModel` for all entities. Ensure `DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'`.

## 🚀 Synergy & Official Best Practices (Django 6.0+)

### 1. Modern Framework Features
- **Template Partials**: Use `{% partialdef %}` for HTMX or reusable UI fragments to improve frontend-backend synergy without extra files.
- **Background Tasks**: Leverage the new built-in **Tasks Framework** for offloading heavy operations (like PDF generation or bulk emails) instead of third-party complex setups when possible.
- **Content Security Policy (CSP)**: Implement the new built-in CSP middleware to secure the application against XSS natively.

### 2. High-Performance ORM (Official Standards)
- **N+1 Avoidance**: Use `select_related()` (One-to-One, ForeignKey) and `prefetch_related()` (Many-to-Many, Reverse FK).
- **Property Caching**: Avoid heavy DB lookups in `@property`. Use `django.utils.functional.cached_property` or pre-calculate values using `.annotate()` in the QuerySet.
- **Efficiency**: Use `.exists()` instead of `.count()` for existence checks. Use `.only()` or `.defer()` to limit data transfer.
- **Save Optimization**: Use `save(update_fields=['field_name'])` to prevent race conditions and improve performance on large models.

### 3. DRF 3.16 Synergy
- **Thin Serializers**: Move complex business logic to `services.py`. Serializers should only handle validation and data mapping.
- **Constraints**: Favor `Meta.constraints` (e.g., `UniqueConstraint`) over `unique_together`. DRF 3.16 has improved support for generating validators from these constraints.
- **Standardized Errors**: Use a custom exception handler to ensure all error responses are consistent and in Spanish for the frontend.

### 3. Professional Standards
- **Naming**: Use English for Python code (variables, classes, methods) and Spanish for user-facing strings (verbose_name, help_text, comments).
- **Documentation**: Every Model and complex ViewSet MUST have a docstring explaining its role in the ecosystem.
- **Error Handling**: Use DRF's `Standardized` error responses. Always provide meaningful error messages in Spanish for the UI.

## 💾 Environment Memory
- **VENV**: ALWAYS check for `.\venv\Scripts\Activate.ps1` before running any `manage.py` command.
- **Shell**: Prefer **PowerShell** syntax as per user's IDE setup. If using CMD, wrap with `cmd /c`.
- **Migrations**: Always run `python manage.py makemigrations` and `python manage.py migrate` together to ensure the DB state is synced immediately.

## 🧩 Synergized Folder Structure
- **apps/**: Keep business logic separated by domains.
- **services.py**: For cross-model operations.
- **selectors.py**: For complex QuerySet logic/filters to keep models and views "thin".

---
*Created for httprene-tech/el-campo-backend*
