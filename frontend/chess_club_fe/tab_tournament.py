"""Tournament tab: create tournaments and their rounds."""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date

from chess_club_fe import api_client


class TournamentTab(ttk.Frame):
    def __init__(self, parent, on_success=None):
        super().__init__(parent)
        self.on_success = on_success or (lambda: None)

        form = ttk.Frame(self)
        form.pack(padx=20, pady=20, anchor="w")

        ttk.Label(form, text="Tournament name:").grid(
            row=0, column=0, sticky="w", pady=4
        )
        self.name_var = tk.StringVar()
        self.name_entry = ttk.Entry(form, textvariable=self.name_var, width=37)
        self.name_entry.grid(row=0, column=1, pady=4)

        ttk.Label(form, text="Start date (YYYY-MM-DD):").grid(
            row=1, column=0, sticky="w", pady=4
        )
        self.date_var = tk.StringVar(value=date.today().isoformat())
        ttk.Entry(form, textvariable=self.date_var, width=37).grid(
            row=1, column=1, pady=4
        )

        ttk.Label(form, text="Number of rounds:").grid(
            row=2, column=0, sticky="w", pady=4
        )
        self.rounds_var = tk.StringVar(value="4")
        ttk.Entry(form, textvariable=self.rounds_var, width=37).grid(
            row=2, column=1, pady=4
        )

        ttk.Button(
            form,
            text="Create Tournament",
            command=self.submit,
        ).grid(row=3, column=1, sticky="e", pady=10)

        self.status = ttk.Label(
            form,
            text="",
            wraplength=500,
            justify="left",
        )
        self.status.grid(
            row=4,
            column=0,
            columnspan=2,
            sticky="w",
        )

        self.name_entry.focus_set()

    def submit(self):
        name = self.name_var.get().strip()
        start_date = self.date_var.get().strip()
        rounds_text = self.rounds_var.get().strip()

        if not name:
            messagebox.showwarning("Invalid", "Tournament name is required.")
            return

        try:
            date.fromisoformat(start_date)
        except ValueError:
            messagebox.showwarning(
                "Invalid",
                "Start date must use YYYY-MM-DD format.",
            )
            return

        if not rounds_text.isdigit():
            messagebox.showwarning(
                "Invalid",
                "Number of rounds must be a whole number.",
            )
            return

        num_rounds = int(rounds_text)
        if not 1 <= num_rounds <= 50:
            messagebox.showwarning(
                "Invalid",
                "Number of rounds must be between 1 and 50.",
            )
            return

        try:
            tournament = api_client.create_tournament(
                name=name,
                start_date=start_date,
                num_rounds=num_rounds,
            )
        except api_client.ApiError as e:
            self.status.config(text=f"Error: {e.detail}")
            messagebox.showerror("Failed to create tournament", e.detail)
            return

        round_ids = ", ".join(
            f'R{r["round_no"]}=#{r["id"]}' for r in tournament["rounds"]
        )

        self.status.config(
            text=(
                f'Tournament #{tournament["id"]} created as planned.\n'
                f'Rounds: {round_ids}'
            )
        )

        self.name_var.set("")
        self.on_success()

        messagebox.showinfo(
            "Tournament created",
            f'{tournament["name"]} and {len(tournament["rounds"])} rounds were created.',
        )
