# CLAUDE.md — Cotizapp

This file provides context for AI assistants working on this codebase.

## Project Overview

**Cotizapp** is a Python Telegram bot that calculates product quotation costs for the Argentine market (specifically targeting Mendoza/Mendocino buyers). It walks users through a guided conversation to collect product details and computes the final price including commission, shipping, and ARS exchange rate conversions (Blue and MEP rates).

## Repository Structure

```
cotizapp/
├── main.py           # Entire application (single file, ~100 lines)
├── Requirements.txt  # Python dependencies (currently empty — see below)
└── README.md         # Minimal readme (title only)
```

This is a small, single-file Python application. There is no build system, no frontend, no database, and no REST API.

## Tech Stack

| Component      | Technology                    |
|----------------|-------------------------------|
| Language       | Python 3.7+                   |
| Bot framework  | `python-telegram-bot` (async) |
| State storage  | In-memory dict (`usuarios`)   |
| Logging        | Python `logging` (stdlib)     |

**Note:** `Requirements.txt` is empty. The actual dependency needed is:
```
python-telegram-bot>=20.0
```

## How to Run

```bash
pip install python-telegram-bot
python main.py
```

The bot uses long-polling (`app.run_polling()`). It requires a valid Telegram bot token from BotFather.

## Application Flow

The bot implements a 4-step guided conversation:

```
User: /start
Bot:  Ask for product name
User: <product name>
Bot:  Ask for product link
User: <link>
Bot:  Ask for weight in kg
User: <weight>
Bot:  Ask for price in USD
User: <price>
Bot:  Display full quotation with totals
```

After displaying the quotation, the user's state is deleted from `usuarios`.

## Key Configuration Constants (main.py lines 5–9)

| Constant             | Value  | Description                         |
|----------------------|--------|-------------------------------------|
| `COMISION_PORCENTAJE`| `0.15` | 15% service commission              |
| `ENVIO_USD_POR_KG`   | `40.0` | Shipping cost in USD per kilogram   |
| `DOLAR_BLUE`         | `1300` | ARS/USD blue market exchange rate   |
| `DOLAR_MEP`          | `1200` | ARS/USD MEP market exchange rate    |

These are hardcoded — update them directly in `main.py` when rates change.

## Quotation Formula

```
commission   = price_usd * 0.15
shipping     = weight_kg * 40.0
total_usd    = price_usd + commission + shipping
total_ars_mep  = total_usd * DOLAR_MEP
total_ars_blue = total_usd * DOLAR_BLUE
```

See `calcular_cotizacion_mendocina()` at `main.py:68`.

## Code Conventions

- **Language of code:** Spanish — all variable names, function names, comments, and user-facing messages are in Spanish (Rioplatense/Argentine informal register).
- **Naming:** snake_case for variables and functions (e.g., `calcular_cotizacion_mendocina`, `precio_usd`, `estado`).
- **Async handlers:** All Telegram handler functions are `async def`.
- **Input sanitization:** User input for numbers cleans commas, `$`, `kg` before `float()` parsing. Always use `try/except ValueError` for numeric inputs.
- **No Markdown in bot replies:** Plain text is used in `reply_text()` calls to avoid Telegram parse errors (see comment at `main.py:59`).
- **Section separators:** `# ---- SECTION NAME ----` comments separate logical blocks.

## State Management

User state is stored in a global in-memory dictionary:

```python
usuarios = {}  # { user_id: { "paso": str, "nombre": str, "link": str, "peso": float, "precio": float } }
```

- `"paso"` tracks the current step: `"nombre"` → `"link"` → `"peso"` → `"precio"`
- All state is lost on bot restart — there is no persistence layer.
- State is deleted after a completed quotation (`del usuarios[user_id]`).

## Known Issues / Technical Debt

1. **Hardcoded bot token** (`main.py:93`) — This is a security vulnerability. The token should be read from an environment variable:
   ```python
   import os
   TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
   ```

2. **Empty Requirements.txt** — Dependencies must be installed manually. Should list `python-telegram-bot>=20.0`.

3. **No tests** — There is zero test coverage. Manual testing via Telegram is the only option.

4. **No persistence** — User session data is lost on restart; users mid-conversation must `/start` again.

5. **Hardcoded exchange rates** — `DOLAR_BLUE` and `DOLAR_MEP` must be updated manually; no automatic fetching.

6. **No graceful shutdown** — No signal handling or state serialization on exit.

## Development Guidelines for AI Assistants

- **Do not break the single-file structure** unless the task explicitly requires splitting it.
- **Keep Spanish naming** — all new variables, functions, and user messages should follow the existing Spanish convention.
- **Preserve the informal tone** in user-facing messages (Rioplatense Argentine Spanish).
- **Use `try/except ValueError`** for any new numeric user input steps.
- **Do not add Markdown formatting** to `reply_text()` calls without also setting `parse_mode` and handling parse errors.
- **When modifying exchange rates or fees**, update only the constants at the top of the file (lines 5–9), not inside functions.
- **If adding persistence**, prefer a lightweight option (SQLite via `aiosqlite`, or a simple JSON file) — avoid heavy ORMs for this scale.
- **If adding environment variable support**, use `os.environ` and document required vars here.

## Environment Variables (Recommended, Not Yet Implemented)

| Variable              | Description                        |
|-----------------------|------------------------------------|
| `TELEGRAM_BOT_TOKEN`  | Bot token from BotFather (required)|
| `COMISION_PORCENTAJE` | Commission rate override (optional)|
| `ENVIO_USD_POR_KG`    | Shipping cost override (optional)  |
| `DOLAR_BLUE`          | Blue rate override (optional)      |
| `DOLAR_MEP`           | MEP rate override (optional)       |

## Branch & Git Workflow

- Main development branch: `master` / `main`
- Feature branches follow the pattern: `claude/<description>-<id>`
- Push with: `git push -u origin <branch-name>`
