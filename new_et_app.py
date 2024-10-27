import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import calendar

# Function to set up the SQLite database
def setup_database():
    conn = sqlite3.connect("expenses.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS expenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    amount REAL,
                    recipient TEXT,
                    mode_of_payment TEXT,
                    category TEXT,
                    date TEXT,
                    time TEXT
                )''')
    conn.commit()
    conn.close()

class UserAuth:
    def __init__(self):
        self.current_user_id = 1  # Placeholder for a logged-in user

class ExpenseTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker")
        self.root.geometry("800x600")
        self.root.configure(bg="#f0f0f0")  # Light gray background

        self.user_auth = UserAuth()
        self.remaining_budget = 0.0

        self.create_widgets()

    # Function to create and arrange all widgets
    def create_widgets(self):
        style = ttk.Style()
        style.configure('TButton', font=('Arial', 10), background="#5DADE2", foreground="white")
        style.configure('TLabel', background="#f0f0f0", font=('Arial', 12))

        # Left panel for input and buttons
        self.left_frame = tk.Frame(self.root, bg="#f0f0f0", padx=10, pady=10)
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y)

        self.budget_label = ttk.Label(self.left_frame, text="Set Monthly Budget:")
        self.budget_label.pack(pady=5)

        self.budget_entry = tk.Entry(self.left_frame)
        self.budget_entry.pack(pady=5)

        self.set_budget_button = ttk.Button(self.left_frame, text="Set Budget", command=self.set_budget)
        self.set_budget_button.pack(pady=5)

        self.remaining_budget_label = ttk.Label(self.left_frame, text="Remaining Budget: $0.00")
        self.remaining_budget_label.pack(pady=10)

        self.amount_label = ttk.Label(self.left_frame, text="Amount:")
        self.amount_label.pack(pady=5)

        self.amount_entry = tk.Entry(self.left_frame)
        self.amount_entry.pack(pady=5)

        self.recipient_label = ttk.Label(self.left_frame, text="Sent to:")
        self.recipient_label.pack(pady=5)

        self.recipient_entry = tk.Entry(self.left_frame)
        self.recipient_entry.pack(pady=5)

        self.mode_of_payment_label = ttk.Label(self.left_frame, text="Mode of Payment:")
        self.mode_of_payment_label.pack(pady=5)

        self.mode_of_payment_combobox = ttk.Combobox(self.left_frame, values=["Cash", "Card", "Online", "Other"])
        self.mode_of_payment_combobox.pack(pady=5)

        self.category_label = ttk.Label(self.left_frame, text="Category:")
        self.category_label.pack(pady=5)

        self.category_combobox = ttk.Combobox(self.left_frame, values=["Food", "Transport", "Shopping", "Utilities", "Other"])
        self.category_combobox.pack(pady=5)

        self.add_expense_button = ttk.Button(self.left_frame, text="Add Expense", command=self.add_expense)
        self.add_expense_button.pack(pady=10)

        self.delete_expense_button = ttk.Button(self.left_frame, text="Delete Expense", command=self.delete_expense)
        self.delete_expense_button.pack(pady=10)

        self.analysis_button = ttk.Button(self.left_frame, text="Show Analysis", command=self.show_analysis)
        self.analysis_button.pack(pady=10)

        self.monthly_expense_button = ttk.Button(self.left_frame, text="Show Monthly Expense", command=self.show_monthly_expense)
        self.monthly_expense_button.pack(pady=10)

        self.daily_expense_button = ttk.Button(self.left_frame, text="Show Daily Expenses", command=self.show_daily_expenses)
        self.daily_expense_button.pack(pady=10)

        # Right panel for table
        self.right_frame = tk.Frame(self.root, bg="#f0f0f0", padx=10, pady=10)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.expense_tree = ttk.Treeview(self.right_frame, columns=("id", "amount", "recipient", "mode_of_payment", "category", "date", "time"), show="headings")
        self.expense_tree.heading("id", text="ID")
        self.expense_tree.heading("amount", text="Amount")
        self.expense_tree.heading("recipient", text="Sent to")
        self.expense_tree.heading("mode_of_payment", text="Mode of Payment")
        self.expense_tree.heading("category", text="Category")
        self.expense_tree.heading("date", text="Date")
        self.expense_tree.heading("time", text="Time")
        self.expense_tree.pack(fill=tk.BOTH, expand=True)

        self.expense_tree.bind("<Double-1>", self.show_daily_expenses)

    # Function to set the monthly budget
    def set_budget(self):
        try:
            budget = float(self.budget_entry.get())
            self.remaining_budget = budget
            self.update_remaining_budget_label()
        except ValueError:
            messagebox.showerror("Error", "Invalid budget amount")

    # Function to update the remaining budget label
    def update_remaining_budget_label(self):
        self.remaining_budget_label.config(text=f"Remaining Budget: ${self.remaining_budget:.2f}")

    # Function to add an expense
    def add_expense(self):
        try:
            amount = float(self.amount_entry.get())
            recipient = self.recipient_entry.get()
            mode_of_payment = self.mode_of_payment_combobox.get()
            category = self.category_combobox.get()

            if not recipient or not mode_of_payment or not category:
                messagebox.showerror("Error", "All fields are required")
                return

            if amount > self.remaining_budget:
                messagebox.showerror("Error", "Amount exceeds remaining budget")
                return

            date = datetime.now().strftime("%Y-%m-%d")
            time = datetime.now().strftime("%H:%M:%S")

            conn = sqlite3.connect("expenses.db")
            c = conn.cursor()
            c.execute("INSERT INTO expenses (user_id, amount, recipient, mode_of_payment, category, date, time) VALUES (?, ?, ?, ?, ?, ?, ?)",
                      (self.user_auth.current_user_id, amount, recipient, mode_of_payment, category, date, time))
            conn.commit()
            conn.close()

            self.remaining_budget -= amount
            self.update_remaining_budget_label()

            self.show_expenses()
        except ValueError:
            messagebox.showerror("Error", "Invalid amount")

    # Function to delete an expense and refund the amount to the budget
    def delete_expense(self):
        selected_item = self.expense_tree.selection()
        if selected_item:
            item_id = self.expense_tree.item(selected_item)["values"][0]
            
            conn = sqlite3.connect("expenses.db")
            c = conn.cursor()
            c.execute("SELECT amount FROM expenses WHERE id=?", (item_id,))
            expense = c.fetchone()
            if expense:
                amount_to_refund = expense[0]
                self.remaining_budget += amount_to_refund  # Add back the amount to the remaining budget

                c.execute("DELETE FROM expenses WHERE id=?", (item_id,))
                conn.commit()
                conn.close()

                self.update_remaining_budget_label()
                messagebox.showinfo("Success", "Expense deleted successfully!")
                self.show_expenses()  # Refresh the table view after deletion
            else:
                messagebox.showerror("Error", "Failed to fetch the selected expense")
        else:
            messagebox.showerror("Error", "No expense selected")

    # Function to show all expenses in TreeView
    def show_expenses(self):
        for i in self.expense_tree.get_children():
            self.expense_tree.delete(i)  # Clear the table before showing updated data

        conn = sqlite3.connect("expenses.db")
        c = conn.cursor()
        c.execute("SELECT * FROM expenses WHERE user_id=?", (self.user_auth.current_user_id,))
        expenses = c.fetchall()
        for expense in expenses:
            self.expense_tree.insert("", "end", values=expense)
        conn.close()

    # Function to show analysis using Matplotlib
    def show_analysis(self):
        conn = sqlite3.connect("expenses.db")
        c = conn.cursor()
        c.execute("SELECT category, SUM(amount) FROM expenses WHERE user_id=? GROUP BY category", (self.user_auth.current_user_id,))
        data = c.fetchall()
        conn.close()

        if data:
            categories = [row[0] for row in data]
            amounts = [row[1] for row in data]

            fig, ax = plt.subplots()
            ax.pie(amounts, labels=categories, autopct='%1.1f%%', startangle=90)
            ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

            chart_window = tk.Toplevel()
            chart_window.title("Expense Analysis")

            canvas = FigureCanvasTkAgg(fig, master=chart_window)
            canvas.draw()
            canvas.get_tk_widget().pack()
        else:
            messagebox.showinfo("No Data", "No expenses to analyze")

    # Function to show monthly expenses
    def show_monthly_expense(self):
        current_year = datetime.now().year
        current_month = datetime.now().month

        conn = sqlite3.connect("expenses.db")
        c = conn.cursor()
        c.execute("""
            SELECT SUM(amount) 
            FROM expenses 
            WHERE user_id=? AND strftime('%Y-%m', date) = ?
        """, (self.user_auth.current_user_id, f"{current_year}-{current_month:02d}"))
        total_expense = c.fetchone()[0] or 0.0  # Fetch the total or set to 0 if no expenses
        conn.close()

        messagebox.showinfo("Monthly Expense", f"Total expense for this month: ${total_expense:.2f}")

    # Function to show daily expenses grouped by date
    def show_daily_expenses(self):
        current_year = datetime.now().year
        current_month = datetime.now().month

        conn = sqlite3.connect("expenses.db")
        c = conn.cursor()
        c.execute("""
            SELECT date, SUM(amount)
            FROM expenses 
            WHERE user_id=? AND strftime('%Y-%m', date) = ?
            GROUP BY date
            ORDER BY date
        """, (self.user_auth.current_user_id, f"{current_year}-{current_month:02d}"))
        daily_expenses = c.fetchall()
        conn.close()

        if daily_expenses:
            daily_expense_window = tk.Toplevel(self.root)
            daily_expense_window.title("Daily Expenses")

            text_widget = tk.Text(daily_expense_window, height=15, width=40)
            text_widget.pack()

            for day, total in daily_expenses:
                text_widget.insert(tk.END, f"Date: {day}, Total Expense: ${total:.2f}\n")
        else:
            messagebox.showinfo("No Data", "No daily expenses for this month.")

    # Function to show a monthly calendar (simplified for demo)
    def show_monthly_calendar(self):
        current_year = datetime.now().year
        current_month = datetime.now().month
        month_calendar = calendar.month(current_year, current_month)

        calendar_window = tk.Toplevel(self.root)
        calendar_window.title("Monthly Calendar")

        text_widget = tk.Text(calendar_window, height=10, width=30)
        text_widget.insert(tk.END, month_calendar)
        text_widget.pack()

if __name__ == "__main__":
    setup_database()

    root = tk.Tk()
    app = ExpenseTrackerApp(root)
    app.show_expenses()  # Initial load of expenses
    root.mainloop()
