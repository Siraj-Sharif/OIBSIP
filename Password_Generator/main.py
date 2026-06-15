import tkinter as tk
from tkinter import ttk, messagebox
import secrets
import string
import re


class PasswordGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Password Generator")
        self.root.geometry("550x650")
        self.root.resizable(False, False)

        # Variables
        self.length_var = tk.IntVar(value=16)
        self.use_upper = tk.BooleanVar(value=True)
        self.use_lower = tk.BooleanVar(value=True)
        self.use_digits = tk.BooleanVar(value=True)
        self.use_symbols = tk.BooleanVar(value=True)
        self.exclude_ambiguous = tk.BooleanVar(value=False)
        self.custom_exclude = tk.StringVar()

        # Build GUI
        self.create_widgets()

        # Generate default password on start
        self.generate_password()

    def create_widgets(self):
        # ----- Password Length Frame -----
        len_frame = ttk.LabelFrame(self.root, text="Password Length", padding=10)
        len_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(len_frame, text="Length (4-128):").pack(side="left", padx=5)
        self.length_spinbox = ttk.Spinbox(len_frame, from_=4, to=128, textvariable=self.length_var,
                                          width=6, command=self.generate_password)
        self.length_spinbox.pack(side="left", padx=5)
        self.length_spinbox.bind("<KeyRelease>", lambda e: self.validate_length())

        # ----- Character Sets Frame -----
        chars_frame = ttk.LabelFrame(self.root, text="Character Sets", padding=10)
        chars_frame.pack(fill="x", padx=10, pady=5)

        ttk.Checkbutton(chars_frame, text="Uppercase (A-Z)", variable=self.use_upper,
                        command=self.generate_password).pack(anchor="w")
        ttk.Checkbutton(chars_frame, text="Lowercase (a-z)", variable=self.use_lower,
                        command=self.generate_password).pack(anchor="w")
        ttk.Checkbutton(chars_frame, text="Digits (0-9)", variable=self.use_digits,
                        command=self.generate_password).pack(anchor="w")
        ttk.Checkbutton(chars_frame, text="Symbols (!@#$%^&*...)", variable=self.use_symbols,
                        command=self.generate_password).pack(anchor="w")

        # ----- Exclusion Options Frame -----
        exclude_frame = ttk.LabelFrame(self.root, text="Exclusion Options", padding=10)
        exclude_frame.pack(fill="x", padx=10, pady=5)

        ttk.Checkbutton(exclude_frame, text="Exclude ambiguous characters ( l, 1, I, O, 0 )",
                        variable=self.exclude_ambiguous, command=self.generate_password).pack(anchor="w")

        ttk.Label(exclude_frame, text="Custom excluded characters:").pack(anchor="w", pady=(5, 0))
        self.custom_exclude_entry = ttk.Entry(exclude_frame, textvariable=self.custom_exclude, width=40)
        self.custom_exclude_entry.pack(fill="x", pady=5)
        self.custom_exclude_entry.bind("<KeyRelease>", lambda e: self.generate_password())

        # ----- Generated Password Display Frame -----
        display_frame = ttk.LabelFrame(self.root, text="Generated Password", padding=10)
        display_frame.pack(fill="x", padx=10, pady=5)

        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(display_frame, textvariable=self.password_var,
                                        font=("Courier", 12), state="readonly")
        self.password_entry.pack(fill="x", pady=5)

        btn_frame = ttk.Frame(display_frame)
        btn_frame.pack(fill="x", pady=5)

        ttk.Button(btn_frame, text="Generate New", command=self.generate_password).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Copy to Clipboard", command=self.copy_to_clipboard).pack(side="left", padx=5)

        # ----- Password Strength Meter -----
        strength_frame = ttk.LabelFrame(self.root, text="Password Strength", padding=10)
        strength_frame.pack(fill="x", padx=10, pady=5)

        self.strength_bar = ttk.Progressbar(strength_frame, length=400, mode='determinate')
        self.strength_bar.pack(pady=5)

        self.strength_label = ttk.Label(strength_frame, text="", font=("Arial", 10, "bold"))
        self.strength_label.pack()

        # ----- Information Label -----
        info_label = ttk.Label(self.root,
                               text="Tip: Use at least 12 characters and include all character types for a strong password.",
                               foreground="gray", wraplength=500)
        info_label.pack(pady=10)

    def validate_length(self):
        """Ensure length stays within bounds."""
        try:
            length = self.length_var.get()
            if length < 4:
                self.length_var.set(4)
            elif length > 128:
                self.length_var.set(128)
        except tk.TclError:
            self.length_var.set(16)
        finally:
            self.generate_password()

    def build_character_pool(self):
        """Build the set of allowed characters based on user selections."""
        pool = ""
        if self.use_upper.get():
            pool += string.ascii_uppercase
        if self.use_lower.get():
            pool += string.ascii_lowercase
        if self.use_digits.get():
            pool += string.digits
        if self.use_symbols.get():
            pool += string.punctuation  # !"#$%&'()*+,-./:;<=>?@[\]^_`{|}~

        # Remove ambiguous characters if requested
        if self.exclude_ambiguous.get():
            ambiguous = "l1IO0"
            pool = ''.join(ch for ch in pool if ch not in ambiguous)

        # Remove custom excluded characters
        custom_excl = self.custom_exclude.get().strip()
        if custom_excl:
            pool = ''.join(ch for ch in pool if ch not in custom_excl)

        return pool

    def generate_password(self):
        """Generate a cryptographically secure random password."""
        pool = self.build_character_pool()
        length = self.length_var.get()

        if not pool:
            self.password_var.set("ERROR: No character sets selected!")
            self.update_strength("")
            return

        if length < 1:
            length = 4

        # Use secrets.choice for secure randomness
        password = ''.join(secrets.choice(pool) for _ in range(length))
        self.password_var.set(password)
        self.update_strength(password)

    def evaluate_strength(self, password):
        """
        Evaluate password strength based on:
        - Length
        - Character variety (uppercase, lowercase, digits, symbols)
        - Common patterns (simple check)
        Returns a score (0-100) and a label.
        """
        if not password:
            return 0, "No password"

        score = 0
        length = len(password)

        # Length contribution (max 40 points)
        if length >= 8:
            score += 20
        if length >= 12:
            score += 10
        if length >= 16:
            score += 10
        # Extra for very long
        if length >= 20:
            score += 5
        if length >= 24:
            score += 5
        # Cap at 40
        score = min(score, 40)

        # Character variety (max 40 points)
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_symbol = any(c in string.punctuation for c in password)

        variety = sum([has_upper, has_lower, has_digit, has_symbol])
        score += variety * 10  # 10 per type, max 40

        # Bonus for mixing different types well (10 points)
        if variety >= 3 and length >= 12:
            score += 10

        # Penalty for sequential or repeated chars (very simple check)
        if re.search(r'(.)\1{2}', password):  # three identical chars in a row
            score -= 10
        if re.search(r'(012|123|234|345|456|567|678|789|abc|bcd|cde|def|efg)', password.lower()):
            score -= 10

        # Ensure score within 0-100
        score = max(0, min(100, score))

        if score < 40:
            label = "Very Weak"
        elif score < 60:
            label = "Weak"
        elif score < 75:
            label = "Moderate"
        elif score < 90:
            label = "Strong"
        else:
            label = "Very Strong"

        return score, label

    def update_strength(self, password):
        """Update strength bar and label."""
        score, label = self.evaluate_strength(password)
        self.strength_bar['value'] = score
        self.strength_label.config(text=label)

        # Color coding via style (optional, but we'll set text color)
        if score < 40:
            self.strength_label.config(foreground="red")
        elif score < 60:
            self.strength_label.config(foreground="orange")
        elif score < 75:
            self.strength_label.config(foreground="goldenrod")
        elif score < 90:
            self.strength_label.config(foreground="green")
        else:
            self.strength_label.config(foreground="darkgreen")

    def copy_to_clipboard(self):
        """Copy generated password to clipboard."""
        pwd = self.password_var.get()
        if pwd and not pwd.startswith("ERROR"):
            self.root.clipboard_clear()
            self.root.clipboard_append(pwd)
            self.root.update()  # Keep clipboard content after program closes
            messagebox.showinfo("Copied", "Password copied to clipboard!")
        else:
            messagebox.showerror("Error", "No valid password to copy.")


if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordGenerator(root)
    root.mainloop()


# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
