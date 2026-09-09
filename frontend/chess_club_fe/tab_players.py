"""Players tab: view and create chess players."""

import tkinter as tk
from tkinter import ttk, messagebox

from chess_club_fe import api_client


class PlayersTab(ttk.Frame):
    COLUMNS = ("id", "name", "birth_year", "current_elo")
    HEADINGS = ("ID", "Name", "Born", "Elo")

    def __init__(self, parent, on_success=None):
        super().__init__(parent)
        self.on_success = on_success or (lambda: None)

        # Top bar
        bar = ttk.Frame(self)
        bar.pack(fill="x", padx=8, pady=6)

        ttk.Button(
            bar,
            text="Add Player",
            command=self.open_add_player,
        ).pack(side="left")

        ttk.Button(
            bar,
            text="Refresh",
            command=self.load,
        ).pack(side="left", padx=(8, 0))

        self.status = ttk.Label(bar, text="")
        self.status.pack(side="left", padx=10)

        # Player table
        self.tree = ttk.Treeview(
            self,
            columns=self.COLUMNS,
            show="headings",
        )

        for col, heading in zip(self.COLUMNS, self.HEADINGS):
            self.tree.heading(col, text=heading)
            self.tree.column(col, anchor="center", width=120)

        self.tree.column("name", anchor="w", width=240)

        self.tree.pack(
            fill="both",
            expand=True,
            padx=8,
            pady=(0, 8),
        )

        self.load()

    def load(self):
        """Fetch players and repopulate the table."""

        try:
            players = api_client.get_players()

        except api_client.ApiError as e:
            self.status.config(text=f"Error: {e.detail}")
            messagebox.showerror(
                "Failed to load players",
                e.detail,
            )
            return

        for row in self.tree.get_children():
            self.tree.delete(row)

        for p in players:
            self.tree.insert(
                "",
                "end",
                values=(
                    p["id"],
                    p["name"],
                    p.get("birth_year", ""),
                    p["current_elo"],
                ),
            )

        self.status.config(text=f"{len(players)} players")

    def open_add_player(self):
        """Open a dialog for creating a player."""

        window = tk.Toplevel(self)
        window.title("Add Player")
        window.resizable(False, False)
        window.transient(self.winfo_toplevel())
        window.grab_set()

        frame = ttk.Frame(window, padding=15)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Name:").grid(
            row=0,
            column=0,
            sticky="w",
            pady=5,
        )

        name_var = tk.StringVar()

        name_entry = ttk.Entry(
            frame,
            textvariable=name_var,
            width=30,
        )

        name_entry.grid(
            row=0,
            column=1,
            pady=5,
        )

        ttk.Label(frame, text="Birth year:").grid(
            row=1,
            column=0,
            sticky="w",
            pady=5,
        )

        birth_var = tk.StringVar()

        ttk.Entry(
            frame,
            textvariable=birth_var,
            width=30,
        ).grid(
            row=1,
            column=1,
            pady=5,
        )

        ttk.Label(frame, text="Initial Elo:").grid(
            row=2,
            column=0,
            sticky="w",
            pady=5,
        )

        elo_var = tk.StringVar(value="1000")

        ttk.Entry(
            frame,
            textvariable=elo_var,
            width=30,
        ).grid(
            row=2,
            column=1,
            pady=5,
        )

        buttons = ttk.Frame(frame)

        buttons.grid(
            row=3,
            column=0,
            columnspan=2,
            pady=(15, 0),
        )

        def save():
            name = name_var.get().strip()

            if not name:
                messagebox.showerror(
                    "Invalid player",
                    "Name is required.",
                    parent=window,
                )
                return

            birth_text = birth_var.get().strip()

            try:
                birth_year = (
                    int(birth_text)
                    if birth_text
                    else None
                )

                current_elo = int(elo_var.get())

            except ValueError:
                messagebox.showerror(
                    "Invalid player",
                    "Birth year and Elo must be numbers.",
                    parent=window,
                )
                return

            try:
                player = api_client.create_player(
                    name=name,
                    birth_year=birth_year,
                    current_elo=current_elo,
                )

            except api_client.ApiError as e:
                messagebox.showerror(
                    "Failed to create player",
                    e.detail,
                    parent=window,
                )
                return

            window.destroy()

            self.load()
            self.on_success()

            messagebox.showinfo(
                "Player created",
                f'{player["name"]} was added successfully.',
            )

        ttk.Button(
            buttons,
            text="Cancel",
            command=window.destroy,
        ).pack(side="left", padx=5)

        ttk.Button(
            buttons,
            text="Add Player",
            command=save,
        ).pack(side="left", padx=5)

        name_entry.focus_set()
