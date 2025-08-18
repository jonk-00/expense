import csv
from datetime import datetime

FILE_NAME = "expenses.csv"


# Create the file with headers if not already there
def init_file():
    try:
        with open(FILE_NAME, "x", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Date", "Category", "Amount", "Description"])
    except FileExistsError:
        pass


# Add a new expense
def add_expense():
    category = input("Enter category (Food, Transport, Bills, etc.): ")
    amount = float(input("Enter amount: "))
    description = input("Enter description: ")
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(FILE_NAME, "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([date, category, amount, description])
    print("✅ Expense added!")


# Load all expenses into a list
def load_expenses():
    with open(FILE_NAME, "r") as file:
        reader = csv.reader(file)
        return list(reader)


# Save all expenses back to file
def save_expenses(expenses):
    with open(FILE_NAME, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(expenses)


# View all expenses
def view_expenses():
    expenses = load_expenses()
    for i, row in enumerate(expenses):
        print(f"{i}. {row}")


# Edit an expense
def edit_expense():
    expenses = load_expenses()
    view_expenses()

    try:
        idx = int(input("Enter the number of the expense to edit: "))
        if idx == 0:
            print("⚠️ Cannot edit header row.")
            return
        if idx >= len(expenses):
            print("⚠️ Invalid index.")
            return

        # Show current values
        date, category, amount, description = expenses[idx]
        print(f"Editing: {expenses[idx]}")

        # Get new values (leave blank to keep old)
        new_category = input(f"Enter new category [{category}]: ") or category
        new_amount = input(f"Enter new amount [{amount}]: ") or amount
        new_description = input(f"Enter new description [{description}]: ") or description

        expenses[idx] = [date, new_category, new_amount, new_description]
        save_expenses(expenses)
        print("✏️ Expense updated!")

    except ValueError:
        print("⚠️ Invalid input.")


# Delete an expense
def delete_expense():
    expenses = load_expenses()
    view_expenses()

    try:
        idx = int(input("Enter the number of the expense to delete: "))
        if idx == 0:
            print("⚠️ Cannot delete header row.")
            return
        if idx >= len(expenses):
            print("⚠️ Invalid index.")
            return

        print(f"Deleting: {expenses[idx]}")
        confirm = input("Are you sure? (y/n): ")
        if confirm.lower() == "y":
            expenses.pop(idx)
            save_expenses(expenses)
            print("🗑️ Expense deleted!")
    except ValueError:
        print("⚠️ Invalid input.")


# Show summary totals by category
def summary_by_category():
    totals = {}
    with open(FILE_NAME, "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            category = row["Category"]
            amount = float(row["Amount"])
            totals[category] = totals.get(category, 0) + amount

    print("\n📊 Spending by Category:")
    for category, total in totals.items():
        print(f"{category}: ${total:.2f}")


# Main program
def main():
    init_file()
    while True:
        print("\n--- Expense Tracker ---")
        print("1. Add Expense")
        print("2. View All Expenses")
        print("3. Edit Expense")
        print("4. Delete Expense")
        print("5. Summary by Category")
        print("6. Exit")
        choice = input("Choose an option: ")

        if choice == "1":
            add_expense()
        elif choice == "2":
            view_expenses()
        elif choice == "3":
            edit_expense()
        elif choice == "4":
            delete_expense()
        elif choice == "5":
            summary_by_category()
        elif choice == "6":
            print("Goodbye! 👋")
            break
        else:
            print("⚠️ Invalid choice. Try again.")


if __name__ == "__main__":
    main()

