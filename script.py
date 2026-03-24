import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import sqlite3
from datetime import datetime


class FinanceTracker:
    def __init__(self, root):  # Corectat: __init__
        self.root = root
        self.root.title("Finance Tracker")
        self.root.geometry("1920x1080")
        self.transactions = []
        self.balance = 0

        # Asigură-te că ai background.jpg în folder sau comentează linia de mai jos
        try:
            self.set_background("background.jpg")
        except:
            print("Imaginea background.jpg nu a fost găsită. Rulez fără fundal.")
            self.canvas = tk.Canvas(self.root, width=1920, height=1080)
            self.canvas.pack(fill="both", expand=True)

        self.initialize_database()
        self.load_transactions()
        self.create_ui()

    def initialize_database(self):
        self.conn = sqlite3.connect("finance_tracker.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
                            CREATE TABLE IF NOT EXISTS transactions
                            (
                                id
                                INTEGER
                                PRIMARY
                                KEY
                                AUTOINCREMENT,
                                type
                                TEXT
                                NOT
                                NULL,
                                description
                                TEXT
                                NOT
                                NULL,
                                amount
                                REAL
                                NOT
                                NULL,
                                transaction_date
                                TEXT
                                NOT
                                NULL
                            );
                            """)
        self.conn.commit()

    def load_transactions(self):
        self.cursor.execute("SELECT type, description, amount, transaction_date FROM transactions;")
        rows = self.cursor.fetchall()
        self.transactions = [(row[0], row[1], row[2]) for row in rows]
        self.balance = sum(row[2] if row[0] == "Income" else -row[2] for row in rows)

    def set_background(self, image_path):
        self.canvas = tk.Canvas(self.root, width=600, height=400)
        self.canvas.pack(fill="both", expand=True)
        bg_image = Image.open(image_path)
        bg_image = bg_image.resize((1920, 1080), Image.LANCZOS)
        self.bg_photo = ImageTk.PhotoImage(bg_image)
        self.canvas.create_image(0, 0, image=self.bg_photo, anchor="nw")

    def create_ui(self):
        title_label = tk.Label(self.canvas, text="Finance Tracker", font=("Arial", 16, "bold"))
        self.canvas.create_window(700, 30, window=title_label)

        self.balance_label = tk.Label(self.canvas, text=f"Total Balance: ${self.balance:.2f}", font=("Arial", 14),
                                      bg="#ffffff", fg="#333333")
        self.canvas.create_window(700, 60, window=self.balance_label)

        input_frame = tk.Frame(self.root, bg="#f9f9f9", bd=2, relief="ridge")
        self.canvas.create_window(700, 120, window=input_frame, width=550, height=50)

        tk.Label(input_frame, text="Type:", bg="#f9f9f9").grid(row=0, column=0, padx=5, pady=5)
        self.type_var = tk.StringVar(value="Expense")
        ttk.Combobox(input_frame, textvariable=self.type_var, values=["Income", "Expense"], width=10).grid(row=0,
                                                                                                           column=1,
                                                                                                           padx=5,
                                                                                                           pady=5)

        tk.Label(input_frame, text="Description:", bg="#f9f9f9").grid(row=0, column=2, padx=5, pady=5)
        self.desc_entry = tk.Entry(input_frame, width=20)
        self.desc_entry.grid(row=0, column=3, padx=5, pady=5)

        tk.Label(input_frame, text="Amount:", bg="#f9f9f9").grid(row=0, column=4, padx=5, pady=5)
        self.amount_entry = tk.Entry(input_frame, width=10)
        self.amount_entry.grid(row=0, column=5, padx=5, pady=5)

        add_button = ttk.Button(self.canvas, text="Add Transaction", command=self.add_transaction,
                                style="Accent.TButton")
        self.canvas.create_window(700, 180, window=add_button)

        clear_button = ttk.Button(self.canvas, text="Clear History", command=self.clear_history, style="Accent.TButton")
        self.canvas.create_window(700, 220, window=clear_button)

        history_label = tk.Label(self.canvas, text="Transaction History", font=("Arial", 14), bg="#ffffff",
                                 fg="#333333")
        self.canvas.create_window(700, 260, window=history_label)

        self.tree = ttk.Treeview(self.root, columns=("Type", "Description", "Amount"), show="headings", height=5)
        self.tree.heading("Type", text="Type")
        self.tree.heading("Description", text="Description")
        self.tree.heading("Amount", text="Amount")
        self.tree.column("Type", width=100)
        self.tree.column("Description", width=300)
        self.tree.column("Amount", width=100, anchor="e")
        self.canvas.create_window(700, 330, window=self.tree, width=550, height=100)

        self.update_history()
        self.add_styles()

    def add_styles(self):
        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure("Accent.TButton", font=("Arial", 12), background="#4CAF50", padding=5)
        style.map("Accent.TButton", background=[("active", "#45A049")])

    def add_transaction(self):
        t_type = self.type_var.get()
        description = self.desc_entry.get()
        try:
            amount = float(self.amount_entry.get())
        except ValueError:
            messagebox.showerror("Invalid Input", "Amount must be a number.")
            return

        if not description:
            messagebox.showerror("Invalid Input", "Description cannot be empty.")
            return

        if t_type == "Income":
            self.balance += amount
        else:
            self.balance -= amount

        transaction_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute("""
                            INSERT INTO transactions (type, description, amount, transaction_date)
                            VALUES (?, ?, ?, ?);
                            """, (t_type, description, amount, transaction_date))
        self.conn.commit()

        self.transactions.append((t_type, description, amount))
        self.update_balance()
        self.update_history()

        self.desc_entry.delete(0, tk.END)
        self.amount_entry.delete(0, tk.END)

    def update_balance(self):
        self.balance_label.config(text=f"Total Balance: ${self.balance:.2f}")

    def update_history(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for t in self.transactions:
            self.tree.insert("", "end", values=t)

    def clear_history(self):
        self.transactions.clear()
        self.balance = 0
        self.cursor.execute("DELETE FROM transactions;")
        self.conn.commit()
        self.update_balance()
        self.update_history()
        messagebox.showinfo("Clear History", "Transaction history has been cleared.")


if __name__ == "__main__":  
    root = tk.Tk()
    app = FinanceTracker(root)
    root.mainloop()