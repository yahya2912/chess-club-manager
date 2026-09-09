"""Rating History tab: table from GET /rating-history, optional player filter."""
import tkinter as tk
from tkinter import ttk, messagebox

from chess_club_fe import api_client


class HistoryTab(ttk.Frame):
    COLUMNS = ("player_name", "elo", "valid_from")
    HEADINGS = ("Player", "Elo", "Recorded at")

    def __init__(self, parent):
        super().__init__(parent)

        bar = ttk.Frame(self)
        bar.pack(fill="x", padx=8, pady=6)
        ttk.Label(bar, text="Player:").pack(side="left")
        self.player = ttk.Combobox(bar, state="readonly", width=30)
        self.player.pack(side="left", padx=6)
        self.player.bind("<<ComboboxSelected>>", lambda e: self.load())
        ttk.Button(bar, text="Refresh", command=self.load).pack(side="left", padx=6)
        self.status = ttk.Label(bar, text="")
        self.status.pack(side="left", padx=10)

        self.tree = ttk.Treeview(self, columns=self.COLUMNS, show="headings")
        for col, heading in zip(self.COLUMNS, self.HEADINGS):
            self.tree.heading(col, text=heading)
            self.tree.column(col, anchor="center", width=150)
        self.tree.column("player_name", anchor="w", width=220)
        self.tree.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        self._id_by_label = {"All players": None}
        self.load_players()

    def load_players(self):
        try:
            players = api_client.get_players()
        except api_client.ApiError as e:
            self.status.config(text=f"Error: {e.detail}")
            return
        self._id_by_label = {"All players": None}
        for p in players:
            self._id_by_label[p["name"]] = p["id"]
        self.player["values"] = list(self._id_by_label.keys())
        self.player.current(0)
        self.load()

    def load(self):
        label = self.player.get() or "All players"
        pid = self._id_by_label.get(label)
        try:
            rows = api_client.get_rating_history(player_id=pid)
        except api_client.ApiError as e:
            self.status.config(text=f"Error: {e.detail}")
            messagebox.showerror("Failed to load history", e.detail)
            return
        for r in self.tree.get_children():
            self.tree.delete(r)
        for row in rows:
            self.tree.insert("", "end", values=tuple(row[c] for c in self.COLUMNS))
        self.status.config(text=f"{len(rows)} entries")
