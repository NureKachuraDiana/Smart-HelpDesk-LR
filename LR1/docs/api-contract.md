# Smart HelpDesk — REST API contract v1

**Версія:** 1.0 • **Фаза:** проєкт для ЛР2 (у ЛР1 **не реалізовано**).  
**База:** `http://127.0.0.1:8000` • **Тип даних:** `application/json`.  
**Єдині бізнес-правила:** [`requirements.md`](requirements.md), §5 (поля, нормалізація, 3×3 матриця статусів, PATCH, порядок, пріоритет кодів). Нижче наведені тільки транспортні домовленості, без альтернативних формулювань правил.

## 1. Стислий каталог маршрутів (9 маршрутів)

| # | Метод / шлях | Вхідні параметри | Успішна відповідь | Помилки |
|---|---|---|---|---|
| 1 | `GET /health` | Немає | `200` `{"status":"ok"}` | — |
| 2 | `GET /users` | Немає | `200` масив двох `User` | — |
| 3 | `POST /issues` | JSON: `title` (обов.), `description?`, `priority?`, `assignee_id?` | `201` створений `Issue` | `422` |
| 4 | `GET /issues` | Query `status?`, `priority?` | `200` масив `Issue`, упорядкований за створенням | `422` |
| 5 | `GET /issues/{id}` | Path `id: int>0` | `200` `Issue` | `404`, `422` |
| 6 | `PATCH /issues/{id}` | Path `id`, JSON: будь-яка непорожня підмножина `title`, `description`, `priority`, `assignee_id` | `200` оновлений `Issue` | `404`, `409`, `422` |
| 7 | `PATCH /issues/{id}/status` | Path `id`, JSON: **тільки** `status` (обов.) | `200` `Issue` | `404`, `409`, `422` |
| 8 | `POST /issues/{id}/comments` | Path `id`, JSON: `author_id`, `body` (обидва обов.) | `201` створений `Comment` | `404`, `422` |
| 9 | `GET /issues/{id}/comments` | Path `id` | `200` масив `Comment`, за створенням | `404`, `422` |

**Query:** `status∈{OPEN, IN_PROGRESS, CLOSED}`; `priority∈{low, medium, high}`; регістр важливий; за наявності обох AND. **Path:** `id` — додатне ціле. **POST/PATCH:** усі неописані поля відхиляються як 422; у порожньому JSON `PATCH /issues/{id}` — 422. GET не приймає JSON-тіла як частину контракту.

**Відповіді:** `Issue={id:int,title:str,description:str,status:str,priority:str,assignee_id:int|null,created_at:ISO8601_UTC}`. `User={id:int,name:str}`. `Comment={id:int,issue_id:int,author_id:int,body:str,created_at:ISO8601_UTC}`. Точний контракт полів/обмежень див. вимоги §5.1–5.3.

## 2. Єдиний формат помилки

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request data",
    "details": [{"field": "title", "reason": "length must be 3..120 after trim"}]
  }
}
```

| Код | Семантика | `error.code` |
|---|---|---|
| `422 Unprocessable Content` | Невалідне JSON, відсутнє обов'язкове поле, неправильний тип, enum, надлишкове поле, порожній PATCH або некоректний path/query. | `VALIDATION_ERROR` |
| `404 Not Found` | Валідний позитивний `id` не існує. | `NOT_FOUND` |
| `409 Conflict` | Заборонений перехід стану або редагування CLOSED. | `INVALID_STATE_TRANSITION` / `ISSUE_CLOSED` |

Якщо збігаються кілька проблем, HTTP-код вибирається за послідовністю **422 → 404 → 409** відповідно до вимог §5.5. `details` має містити опис поля для 422; у 404/409 допускається `[]`.

## 3. Конкретні приклади запитів і відповідей

Приклади використовують **синтетичні** записи й умовний час, не представляють результат реально запущеного сервера.

### 3.1. `GET /health`

```http
GET /health
```
```json
{"status":"ok"}
```
HTTP `200`.

### 3.2. `GET /users`

```http
GET /users
```
```json
[{"id":1,"name":"Agent A"},{"id":2,"name":"Agent B"}]
```
HTTP `200`.

### 3.3. `POST /issues`

```http
POST /issues
Content-Type: application/json

{"title":"  Помилка входу в кабінет  ","description":"Сторінка повертає 500","priority":"high"}
```

**HTTP 201**:
```json
{
  "id": 1,
  "title": "Помилка входу в кабінет",
  "description": "Сторінка повертає 500",
  "status": "OPEN",
  "priority": "high",
  "assignee_id": null,
  "created_at": "2026-11-18T12:00:00Z"
}
```

**Приклад помилки створення, HTTP 422:**
```http
POST /issues
Content-Type: application/json

{"title":"Ні","priority":"urgent"}
```
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request data",
    "details": [
      {"field":"title","reason":"length must be 3..120 after trim"},
      {"field":"priority","reason":"allowed: low, medium, high"}
    ]
  }
}
```

### 3.4. `GET /issues`

```http
GET /issues?status=OPEN&priority=high
```
HTTP `200`; масив містить тільки відкриті звернення з високим пріоритетом; приклад:
```json
[{"id":1,"title":"Помилка входу в кабінет","description":"Сторінка повертає 500","status":"OPEN","priority":"high","assignee_id":null,"created_at":"2026-11-18T12:00:00Z"}]
```
Якщо збігів немає: HTTP `200`, `[]`.

### 3.5. `GET /issues/{id}`

```http
GET /issues/1
```
HTTP `200`, повертається об'єкт `Issue`, як у §3.3. Для `GET /issues/999`: HTTP `404`:
```json
{"error":{"code":"NOT_FOUND","message":"Issue 999 does not exist","details":[]}}
```

### 3.6. `PATCH /issues/{id}`

```http
PATCH /issues/1
Content-Type: application/json

{"assignee_id":1,"priority":"medium"}
```
HTTP `200`; відповідь — повний `Issue`, де `assignee_id=1`, `priority=medium`, а решта полів незмінна.

Для `{"assignee_id":null}` — HTTP `200`, агент знятий. Для `{"title":"Підтримка","priority":"urgent"}` — HTTP `422`, **жодне** поле не змінене. Для валідного редагування `CLOSED` — HTTP `409` і `error.code="ISSUE_CLOSED"`.

### 3.7. `PATCH /issues/{id}/status`

```http
PATCH /issues/1/status
Content-Type: application/json

{"status":"IN_PROGRESS"}
```
HTTP `200`; повний `Issue` з `status="IN_PROGRESS"`.

**Приклад помилки зміни статусу, HTTP 409:** якщо існуюче звернення `CLOSED`:
```http
PATCH /issues/1/status
Content-Type: application/json

{"status":"OPEN"}
```
```json
{
  "error": {
    "code": "INVALID_STATE_TRANSITION",
    "message": "Transition CLOSED -> OPEN is forbidden",
    "details": []
  }
}
```
Окремий статус не можна встановлювати через звичайний `PATCH /issues/{id}`. Матриця з дев'яти комбінацій — вимоги §5.4.

### 3.8. `POST /issues/{id}/comments`

```http
POST /issues/1/comments
Content-Type: application/json

{"author_id":2,"body":"Помилку відтворено, перевіряємо сервер"}
```
**HTTP 201**:
```json
{"id":1,"issue_id":1,"author_id":2,"body":"Помилку відтворено, перевіряємо сервер","created_at":"2026-11-18T12:06:00Z"}
```

**Приклад помилки коментування, HTTP 422:**
```http
POST /issues/1/comments
Content-Type: application/json

{"author_id":3,"body":"   "}
```
```json
{
  "error": {
    "code":"VALIDATION_ERROR",
    "message":"Invalid request data",
    "details":[
      {"field":"author_id","reason":"unknown author; allowed: 1, 2"},
      {"field":"body","reason":"must contain 1..1000 non-whitespace characters after trim"}
    ]
  }
}
```
Закриті заявки дозволено коментувати; невідомий коректний `issue_id` → 404.

### 3.9. `GET /issues/{id}/comments`

```http
GET /issues/1/comments
```
HTTP `200`, масив `Comment` за зростанням `id`, наприклад:
```json
[{"id":1,"issue_id":1,"author_id":2,"body":"Помилку відтворено, перевіряємо сервер","created_at":"2026-11-18T12:06:00Z"}]
```
Якщо звернення існує, але коментарів немає, `200 []`; якщо звернення не існує, `404`.

## 4. Відповідність вимогам

- FR-01 → маршрут 3; FR-02 → 4–5; FR-03/FR-05 → 6; FR-04 → 7; FR-06 → 8–9; FR-07 → вся система, перевірка перезапуску та негативних запитів.
- FR-08 не має маршруту у ЛР1: вибір контракту відкладено до ЛР4, відповідно до зафіксованих меж.
- Майбутні тести та критерії приймання перелічені у [`traceability.csv`](traceability.csv).
