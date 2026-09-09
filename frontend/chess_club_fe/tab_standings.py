"""Standings tab: table from GET /standings for a chosen tournament."""
import tkinter as tk
from tkinter import ttk, messagebox

from chess_club_fe import api_client


class StandingsTab(ttk.Frame):
    COLUMNS = ("player_name", "points", "buchholz", "wins", "draws", "losses", "games_played")
    HEADINGS = ("Player", "Points", "Buchholz", "W", "D", "L", "Games")

    def __init__(self, parent):
        super().__init__(parent)

        bar = ttk.Frame(self)
        bar.pack(fill="x", padx=8, pady=6)
        ttk.Label(bar, text="Tournament:").pack(side="left")
        self.tournament = ttk.Combobox(bar, state="readonly", width=40)
        self.tournament.pack(side="left", padx=6)
        self.tournament.bind("<<ComboboxSelected>>", lambda e: self.load())
        ttk.Button(bar, text="Refresh", command=self.load_tournaments).pack(side="left", padx=6)
        self.status = ttk.Label(bar, text="")
        self.status.pack(side="left", padx=10)

        self.tree = ttk.Treeview(self, columns=self.COLUMNS, show="headings")
        for col, heading in zip(self.COLUMNS, self.HEADINGS):
            self.tree.heading(col, text=heading)
            self.tree.column(col, anchor="center", width=90)
        self.tree.column("player_name", anchor="w", width=220)
        self.tree.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        self._id_by_label = {}
        self.load_tournaments()

    def load_tournaments(self):
        """Refresh the tournament dropdown and keep the current selection if possible."""
        old_label = self.tournament.get()

        try:
            tournaments = api_client.get_tournaments()
        except api_client.ApiError as e:
            self.status.config(text=f"Error: {e.detail}")
            return

        self._id_by_label = {t["name"]: t["id"] for t in tournaments}
        values = list(self._id_by_label.keys())
        self.tournament["values"] = values

        if old_label in self._id_by_label:
            self.tournament.set(old_label)
        elif values:
            self.tournament.current(0)
        else:
            self.tournament.set("")

        self.load()

    def load(self):
        label = self.tournament.get()
        if not label:
            for r in self.tree.get_children():
                self.tree.delete(r)
            self.status.config(text="0 players")
            return

        tid = self._id_by_label[label]
        try:
            rows = api_client.get_standings(tid)
        except api_client.ApiError as e:
            self.status.config(text=f"Error: {e.detail}")
            messagebox.showerror("Failed to load standings", e.detail)
            return
        for r in self.tree.get_children():
            self.tree.delete(r)
        for row in rows:
            self.tree.insert("", "end", values=tuple(row[c] for c in self.COLUMNS))
        self.status.config(text=f"{len(rows)} players")
