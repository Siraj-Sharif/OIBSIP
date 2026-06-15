import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from mysql.connector import Error
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ---------- MySQL Database Configuration ----------
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',  # Change to your MySQL username
    'password': 'mysql',  # Change to your MySQL password
    'database': 'bmi_db'  # Database name you created
}


# ---------- Database Helper Functions ----------
def init_db():
    """Create tables if they don't exist."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Users table
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS users
                       (
                           id
                           INT
                           AUTO_INCREMENT
                           PRIMARY
                           KEY,
                           name
                           VARCHAR
                       (
                           100
                       ) UNIQUE NOT NULL
                           )
                       ''')

        # Measurements table
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS measurements
                       (
                           id
                           INT
                           AUTO_INCREMENT
                           PRIMARY
                           KEY,
                           user_id
                           INT
                           NOT
                           NULL,
                           date
                           VARCHAR
                       (
                           30
                       ) NOT NULL,
                           weight FLOAT NOT NULL,
                           height FLOAT NOT NULL,
                           bmi FLOAT NOT NULL,
                           category VARCHAR
                       (
                           50
                       ) NOT NULL,
                           FOREIGN KEY
                       (
                           user_id
                       ) REFERENCES users
                       (
                           id
                       ) ON DELETE CASCADE
                           )
                       ''')

        conn.commit()
        cursor.close()
        conn.close()
    except Error as e:
        messagebox.showerror("Database Error", f"Failed to initialise database:\n{e}")
        raise


def get_users():
    """Return list of (id, name) for all users."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM users ORDER BY name")
        users = cursor.fetchall()
        cursor.close()
        conn.close()
        return users
    except Error as e:
        messagebox.showerror("Database Error", f"Could not fetch users:\n{e}")
        return []


def add_user(name):
    """Add a new user, return True if success."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (name) VALUES (%s)", (name,))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Error:
        return False


def save_measurement(user_id, weight, height, bmi, category):
    """Save one measurement to database."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        query = """
                INSERT INTO measurements (user_id, date, weight, height, bmi, category)
                VALUES (%s, %s, %s, %s, %s, %s) \
                """
        cursor.execute(query, (user_id, now, weight, height, bmi, category))
        conn.commit()
        cursor.close()
        conn.close()
    except Error as e:
        messagebox.showerror("Database Error", f"Failed to save measurement:\n{e}")


def get_measurements(user_id):
    """Return list of (date, weight, height, bmi, category) for user."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("""
                       SELECT date, weight, height, bmi, category
                       FROM measurements
                       WHERE user_id = %s
                       ORDER BY date
                       """, (user_id,))
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows
    except Error as e:
        messagebox.showerror("Database Error", f"Could not fetch measurements:\n{e}")
        return []


# ---------- Helper Functions ----------
def calculate_bmi(weight, height):
    """Return BMI and category."""
    if height <= 0:
        raise ValueError("Height must be > 0")
    bmi = weight / (height ** 2)
    if bmi < 18.5:
        category = "Underweight"
    elif bmi < 25:
        category = "Normal weight"
    elif bmi < 30:
        category = "Overweight"
    else:
        category = "Obese"
    return round(bmi, 2), category


# ---------- Main GUI Application ----------
class BMIGui:
    def __init__(self, root):
        self.root = root
        self.root.title("BMI Calculator with History & Trends (MySQL)")
        self.root.geometry("900x700")
        self.current_user_id = None
        self.current_user_name = None

        # Create GUI frames
        self.create_user_frame()
        self.create_input_frame()
        self.create_result_frame()
        self.create_history_frame()
        self.create_stats_graph_frame()

        # Refresh user list
        self.refresh_user_list()

    # ----- User Management Frame -----
    def create_user_frame(self):
        frame = ttk.LabelFrame(self.root, text="User Management", padding=10)
        frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(frame, text="Select User:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.user_combo = ttk.Combobox(frame, state="readonly", width=30)
        self.user_combo.grid(row=0, column=1, padx=5, pady=5)
        self.user_combo.bind("<<ComboboxSelected>>", self.on_user_selected)

        ttk.Button(frame, text="Refresh Users", command=self.refresh_user_list).grid(row=0, column=2, padx=5)

        ttk.Label(frame, text="New User Name:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.new_user_entry = ttk.Entry(frame, width=30)
        self.new_user_entry.grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(frame, text="Add User", command=self.add_new_user).grid(row=1, column=2, padx=5)

    # ----- Input Frame -----
    def create_input_frame(self):
        frame = ttk.LabelFrame(self.root, text="New Measurement", padding=10)
        frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(frame, text="Weight (kg):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.weight_entry = ttk.Entry(frame, width=15)
        self.weight_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame, text="Height (m):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.height_entry = ttk.Entry(frame, width=15)
        self.height_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Button(frame, text="Calculate & Save", command=self.calculate_and_save).grid(row=2, column=0, columnspan=2,
                                                                                         pady=10)

    # ----- Result Display Frame -----
    def create_result_frame(self):
        frame = ttk.LabelFrame(self.root, text="Current Result", padding=10)
        frame.pack(fill="x", padx=10, pady=5)
        self.result_label = ttk.Label(frame, text="BMI: --   Category: --", font=("Arial", 12, "bold"))
        self.result_label.pack()

    # ----- History Table Frame -----
    def create_history_frame(self):
        frame = ttk.LabelFrame(self.root, text="Measurement History", padding=10)
        frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("Date", "Weight (kg)", "Height (m)", "BMI", "Category")
        self.history_tree = ttk.Treeview(frame, columns=columns, show="headings", height=8)
        for col in columns:
            self.history_tree.heading(col, text=col)
            self.history_tree.column(col, width=120)

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)
        self.history_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    # ----- Statistics & Graph Frame -----
    def create_stats_graph_frame(self):
        frame = ttk.LabelFrame(self.root, text="Trend Analysis", padding=10)
        frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Statistics sub‑frame
        stats_frame = ttk.Frame(frame)
        stats_frame.pack(fill="x", pady=5)

        self.stats_label = ttk.Label(stats_frame, text="Select a user to see statistics", font=("Arial", 10))
        self.stats_label.pack()

        # Graph sub‑frame (matplotlib figure)
        self.graph_frame = ttk.Frame(frame)
        self.graph_frame.pack(fill="both", expand=True)

        self.figure = plt.Figure(figsize=(6, 3), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.graph_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    # ----- Core Logic Methods -----
    def refresh_user_list(self):
        users = get_users()
        user_names = [f"{name} (ID:{uid})" for uid, name in users]
        self.user_combo["values"] = user_names
        if user_names and not self.current_user_id:
            # Auto‑select first user if none selected
            self.user_combo.current(0)
            self.on_user_selected()

    def on_user_selected(self, event=None):
        selection = self.user_combo.get()
        if not selection:
            return
        # Extract user ID from string like "John (ID:2)"
        try:
            uid = int(selection.split("ID:")[1].rstrip(")"))
            name = selection.split(" (ID:")[0]
            self.current_user_id = uid
            self.current_user_name = name
            self.update_history()
            self.update_statistics_and_graph()
        except Exception:
            pass

    def add_new_user(self):
        name = self.new_user_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "User name cannot be empty.")
            return
        if add_user(name):
            messagebox.showinfo("Success", f"User '{name}' added.")
            self.new_user_entry.delete(0, tk.END)
            self.refresh_user_list()
            # Try to select the new user automatically
            users = get_users()
            for uid, uname in users:
                if uname == name:
                    self.current_user_id = uid
                    self.current_user_name = uname
                    # Set combobox to match
                    self.user_combo.set(f"{uname} (ID:{uid})")
                    self.update_history()
                    self.update_statistics_and_graph()
                    break
        else:
            messagebox.showerror("Error", f"User '{name}' already exists.")

    def calculate_and_save(self):
        if self.current_user_id is None:
            messagebox.showerror("Error", "Please select or add a user first.")
            return

        try:
            weight = float(self.weight_entry.get())
            height = float(self.height_entry.get())
            if weight <= 0 or height <= 0:
                raise ValueError("Weight and height must be positive.")
            if height > 3.0:  # unrealistic for meters, but allow 3m as max
                # Could be entered in cm? Provide hint.
                if messagebox.askyesno("Unit check",
                                       "Height seems very high (>3m). Did you enter centimetres? Click Yes to convert to metres (divide by 100)."):
                    height = height / 100.0
        except ValueError as e:
            messagebox.showerror("Invalid Input", f"Please enter valid positive numbers.\n{e}")
            return

        bmi, category = calculate_bmi(weight, height)
        self.result_label.config(text=f"BMI: {bmi}   Category: {category}")

        # Save to database
        save_measurement(self.current_user_id, weight, height, bmi, category)
        messagebox.showinfo("Saved", "Measurement saved successfully.")

        # Clear input fields
        self.weight_entry.delete(0, tk.END)
        self.height_entry.delete(0, tk.END)

        # Refresh history and graph
        self.update_history()
        self.update_statistics_and_graph()

    def update_history(self):
        """Populate history table for current user."""
        # Clear existing rows
        for row in self.history_tree.get_children():
            self.history_tree.delete(row)

        if self.current_user_id is None:
            return

        measurements = get_measurements(self.current_user_id)
        for date, weight, height, bmi, category in measurements:
            self.history_tree.insert("", tk.END, values=(date, weight, height, bmi, category))

    def update_statistics_and_graph(self):
        """Compute statistics and draw BMI trend line."""
        if self.current_user_id is None:
            self.stats_label.config(text="No user selected.")
            self.ax.clear()
            self.ax.set_title("BMI Trend")
            self.ax.set_xlabel("Measurement #")
            self.ax.set_ylabel("BMI")
            self.ax.text(0.5, 0.5, "Select a user", transform=self.ax.transAxes, ha='center')
            self.canvas.draw()
            return

        measurements = get_measurements(self.current_user_id)
        if not measurements:
            self.stats_label.config(text=f"User: {self.current_user_name} – No measurements yet.")
            self.ax.clear()
            self.ax.set_title("BMI Trend")
            self.ax.set_xlabel("Measurement #")
            self.ax.set_ylabel("BMI")
            self.ax.text(0.5, 0.5, "No data", transform=self.ax.transAxes, ha='center')
            self.canvas.draw()
            return

        # Extract BMI values and dates (for x‑axis we use sequential index)
        bmi_values = [row[3] for row in measurements]  # row: date, weight, height, bmi, category
        dates = [row[0] for row in measurements]
        indices = list(range(1, len(bmi_values) + 1))

        # Statistics
        avg_bmi = sum(bmi_values) / len(bmi_values)
        min_bmi = min(bmi_values)
        max_bmi = max(bmi_values)
        latest_bmi = bmi_values[-1]

        stats_text = (f"User: {self.current_user_name}  |  Entries: {len(bmi_values)}  |  "
                      f"Avg BMI: {avg_bmi:.2f}  |  Min: {min_bmi:.2f}  |  Max: {max_bmi:.2f}  |  "
                      f"Latest: {latest_bmi:.2f}")
        self.stats_label.config(text=stats_text)

        # Plot graph
        self.ax.clear()
        self.ax.plot(indices, bmi_values, marker='o', linestyle='-', color='blue')
        self.ax.axhline(y=18.5, color='green', linestyle='--', label='Underweight threshold')
        self.ax.axhline(y=25, color='orange', linestyle='--', label='Normal/Overweight threshold')
        self.ax.axhline(y=30, color='red', linestyle='--', label='Obesity threshold')
        self.ax.set_title(f"BMI Trend for {self.current_user_name}")
        self.ax.set_xlabel("Measurement Number")
        self.ax.set_ylabel("BMI")
        self.ax.grid(True, linestyle=':', alpha=0.7)
        self.ax.legend(fontsize=8)
        self.canvas.draw()


# ---------- Run Application ----------
if __name__ == "__main__":
    # Initialise database (creates tables if missing)
    init_db()
    root = tk.Tk()
    app = BMIGui(root)
    root.mainloop()