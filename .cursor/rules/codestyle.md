---
trigger: always_on
---

# Rules

Keep all third-party client integrations under `app/integrations`.
Only have the clients in `app/integrations`, have the actual functions, wrapper under utils/

Use `utils` only for utility/helper functions. Business logic must live inside `services`, and all database access must go through `repositories`.

Have pydantic models under schemas/

Database calls must never be made directly from handlers, routers, commands, or utility functions. Handlers should call services, and services should interact with repositories.

Store all environment variable access and configuration inside `app/config.py`.

Application-specific exceptions should be defined and raised from `app/exceptions.py`.

Use `logger.loguru` for all logging throughout the project.

Imports should be kept clean and consistent. Prefer imports such as:

```python
from  service import user_service

user_service.create_user()
```

Avoid deep imports such as:

```python
from app.users.services.user_service import create_user
```

And only Top Level imports are allowed, no module level imports allowed

Run the following command whenever new modules or packages are created to automatically generate `__init__.py` files:

```bash
uv run init.py
```

Every function should include a short and meaningful docstring explaining its purpose.

When asking users for input, use the helpers available in `utils/ask`.

If a function is used in more than two places, extract it into a reusable function instead of duplicating logic.

Do not use module-level imports. Import dependencies inside functions when required.

User-facing text should sound natural, professional, and human. Avoid excessive formatting, unnecessary complexity, or excessive emoji usage. Use only minimal emojis when they add clarity.

Always provide users with a clear next step. Never leave a user at a dead end after sending a message. Every response should guide them toward an action, choice, or navigation path using inline buttons


Use implicit string concatenation with parentheses for multiline text to avoid horizontal scrolling, rather than using `\n` in a single line or triple-quoted strings.

Use the following format for user-facing text:

```python
text = "{emoji} {title}\n\n{description}"
```

Example:

```python
text = (
    "📦 Order Created\n\n"
    "Your order has been successfully created and is now being processed."
)
```

Always use the `suppress_send_errors` context manager from `utils.common` when sending messages/notifications in background tasks or services to avoid raising unhandled delivery exceptions.

Do not use `ReplyKeyboardRemove()` when prompting users via `ask()` unless the previous step or active prompt uses custom `ReplyKeyboardMarkup` keyboard buttons. For standard inputs, use inline keyboards with cancel/back buttons instead.

Run ruff check . --preview --select PLC0415 after every file changes and fix the imports, leave the migration files

Every handler must get its own file, if there is handler like view_inquiries, view_inquiry_{product_id},
it must be under handler/inquiry/view_inquiries.py handler/inquiry/view_inquiry.py

For Service, Reposiotyr, and Utils, it must be a class with singleton instance, no func only allowed, everything must be a class


## Strict imports (extra)

Never import deeper than `app.<package>` (or a package-exported submodule). No `app.x.y.z` consumer imports.

Allowed:

```python
from app.domain import models
from app.domain import schemas
from app.service import surcharge
from app.service import CartService
from app.repository import OrderRepository
from app.utils import order_utils
```

Use as:

```python
models.SalesChannel
schemas.ProductListResponseData
surcharge.SurchargeService
```

Forbidden:

```python
from app.domain.models.enums import SalesChannel
from app.domain.schemas.response.product import ProductListResponse
from app.service.surcharge import SurchargeService
from app.repository.order import OrderRepository
from app.utils.order import OrderUtils
```

Wrong → right:

- `from app.domain.models.enums import SalesChannel` → `from app.domain import models` then `models.SalesChannel`
- `from app.service.surcharge import SurchargeService` → `from app.service import surcharge` then `surcharge.SurchargeService`
- `from app.repository.order import OrderRepository` → `from app.repository import OrderRepository`

Exception: files inside `app/domain/models/` may use relative imports (`from .enums import ...`).

log every detail with info, debug, warning, error using loguru like logger.bind(arg=v).info(message) you can use with logfire.span(..) for required part where we want to trace a particular external integration timing, success, failure

write unittests for handler, and utils, and service, not for repostiory, and models, write tests only for logically required functions, not for all functions where the results is obvious
```
