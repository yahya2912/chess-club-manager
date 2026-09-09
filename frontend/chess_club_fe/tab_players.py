"""Players tab: a sortable table of players fetched from GET /players."""
import tkinter as tk
from tkinter import ttk, messagebox

from chess_club_fe import api_client


class PlayersTab(ttk.Frame):
    COLUMNS = ("id", "name", "birth_year", "current_elo")
    HEADINGS = ("ID", "Name", "Born", "Elo")

    def __init__(self, parent):
        super().__init__(parent)

        # Top bar with a refresh button
        bar = ttk.Frame(self)
        bar.pack(fill="x", padx=8, pady=6)
        ttk.Button(bar, text="Refresh", command=self.load).pack(side="left")
        self.status = ttk.Label(bar, text="")
        self.status.pack(side="left", padx=10)

        # The table
        self.tree = ttk.Treeview(self, columns=self.COLUMNS, show="headings")
        for col, heading in zip(self.COLUMNS, self.HEADINGS):
            self.tree.heading(col, text=heading)
            self.tree.column(col, anchor="center", width=120)
        self.tree.column("name", anchor="w", width=240)
        self.tree.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        self.load()

    def load(self):
        """Fetch players and repopulate the table."""
        try:
            players = api_client.get_players()
        except api_client.ApiError as e:
            self.status.config(text=f"Error: {e.detail}")
            messagebox.showerror("Failed to load players", e.detail)
            return

        # Clear existing rows
        for row in self.tree.get_children():
            self.tree.delete(row)
        # Insert fresh rows
        for p in players:
            self.tree.insert("", "end", values=(
                p["id"], p["name"], p.get("birth_year", ""), p["current_elo"],
            ))
        self.status.config(text=f"{len(players)} players")
