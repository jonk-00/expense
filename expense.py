
def init_file() -> None:
    """Create the CSV file and header if needed."""
    if not FILE_NAME.exists() or FILE_NAME.stat().st_size == 0:
        with FILE_NAME.open("w", newline="", encoding="utf-8") as file:
            csv.writer(file).writerow(HEADERS)


def load_rows() -> list[list[str]]:
    init_file()
    with FILE_NAME.open("r", newline="", encoding="utf-8") as file:
        reader = csv.reader(file)
        rows = list(reader)
    if not rows or rows[0] != HEADERS:
        raise HTTPException(status_code=500, detail="expenses.csv has an unexpected header. Expected: " + ", ".join(HEADERS))
    valid_rows = []
    for row in rows[1:]:
        if len(row) == 4:
            valid_rows.append(row)
    return valid_rows


def save_rows(rows: list[list[str]]) -> None:
    with FILE_NAME.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(HEADERS)
        writer.writerows(rows)


def serialize(rows: list[list[str]]) -> list[dict[str, Any]]:
    expenses = []
    for index, (date, category, amount, description) in enumerate(rows):
        try:
            numeric_amount = float(amount)
        except ValueError:
            numeric_amount = 0.0
        expenses.append({
            "id": index,
            "date": date,
            "category": category,
            "amount": numeric_amount,
            "description": description,
        })
    return expenses


@app.on_event("startup")
def startup() -> None:
    init_file()


@app.get("/", include_in_schema=False)
def frontend() -> FileResponse:
    return FileResponse(BASE_DIR / "index.html")


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/expenses")
def get_expenses() -> list[dict[str, Any]]:
    return serialize(load_rows())


@app.post("/api/expenses", status_code=201)
def add_expense(expense: ExpenseInput) -> dict[str, Any]:
    values = expense.cleaned()
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    rows = load_rows()
    rows.append([date, values["category"], f'{values["amount"]:.2f}', values["description"]])
    save_rows(rows)
    return serialize(rows)[-1]


@app.put("/api/expenses/{expense_id}")
def edit_expense(expense_id: int, expense: ExpenseInput) -> dict[str, Any]:
    values = expense.cleaned()
    rows = load_rows()
    if expense_id < 0 or expense_id >= len(rows):
        raise HTTPException(status_code=404, detail="Expense not found.")
    date, _, _, _ = rows[expense_id]
    rows[expense_id] = [date, values["category"], f'{values["amount"]:.2f}', values["description"]]
    save_rows(rows)
    return serialize(rows)[expense_id]


@app.delete("/api/expenses/{expense_id}", status_code=204)
def delete_expense(expense_id: int) -> None:
    rows = load_rows()
    if expense_id < 0 or expense_id >= len(rows):
        raise HTTPException(status_code=404, detail="Expense not found.")
    rows.pop(expense_id)
    save_rows(rows)
    return None


@app.get("/api/summary")
def summary_by_category() -> dict[str, Any]:
    totals: dict[str, float] = {}
    for expense in serialize(load_rows()):
        category = expense["category"]
        totals[category] = totals.get(category, 0.0) + expense["amount"]
    return {"totals": totals, "total": round(sum(totals.values()), 2)}


