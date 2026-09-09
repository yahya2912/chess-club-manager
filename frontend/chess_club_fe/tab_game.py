"""Record Game tab: POST /games, shows the resulting Elo change."""
import tkinter as tk
from tkinter import ttk, messagebox

from chess_club_fe import api_client


class GameTab(ttk.Frame):
    RESULTS = ("1-0", "0-1", "1/2-1/2")

    def __init__(self, parent, on_success=None):
        super().__init__(parent)
        self.on_success = on_success or (lambda: None)
        self._player_ids = {}

        form = ttk.Frame(self)
        form.pack(padx=20, pady=20, anchor="w")

        ttk.Label(form, text="Round ID:").grid(row=0, column=0, sticky="w", pady=4)
        self.round_id = ttk.Entry(form, width=37)
        self.round_id.grid(row=0, column=1, pady=4)

        ttk.Label(form, text="White:").grid(row=1, column=0, sticky="w", pady=4)
        self.white = ttk.Combobox(form, state="readonly", width=35)
        self.white.grid(row=1, column=1, pady=4)

        ttk.Label(form, text="Black:").grid(row=2, column=0, sticky="w", pady=4)
        self.black = ttk.Combobox(form, state="readonly", width=35)
        self.black.grid(row=2, column=1, pady=4)

        ttk.Label(form, text="ECO code:").grid(row=3, column=0, sticky="w", pady=4)
        self.eco = ttk.Entry(form, width=37)
        self.eco.grid(row=3, column=1, pady=4)
        self.eco.insert(0, "C50")

        ttk.Label(form, text="Result:").grid(row=4, column=0, sticky="w", pady=4)
        self.result = ttk.Combobox(form, state="readonly", width=35,
                                   values=self.RESULTS)
        self.result.grid(row=4, column=1, pady=4)
        self.result.current(0)

        ttk.Button(form, text="Record Game", command=self.submit).grid(
            row=5, column=1, sticky="e", pady=10)
        self.status = ttk.Label(form, text="", wraplength=400, justify="left")
        self.status.grid(row=6, column=0, columnspan=2, sticky="w")

        self.reload_options()

    def reload_options(self):
        try:
            players = api_client.get_players()
        except api_client.ApiError as e:
            self.status.config(text=f"Error: {e.detail}")
            return
        self._player_ids = {p["name"]: p["id"] for p in players}
        names = list(self._player_ids.keys())
        self.white["values"] = names
        self.black["values"] = names
        if len(names) >= 2:
            self.white.current(0)
            self.black.current(1)

    def submit(self):
        round_val = self.round_id.get().strip()
        if not round_val.isdigit():
            messagebox.showwarning("Invalid", "Round ID must be a whole number.")
            return
        if not self.white.get() or not self.black.get():
            messagebox.showwarning("Missing", "Pick both players.")
            return
        try:
            result = api_client.create_game(
                round_id=int(round_val),
                white_id=self._player_ids[self.white.get()],
                black_id=self._player_ids[self.black.get()],
                eco_code=self.eco.get().strip(),
                result=self.result.get(),
            )
        except api_client.ApiError as e:
            self.status.config(text=f"Error: {e.detail}")
            messagebox.showerror("Failed to record game", e.detail)
            return
        ch = result["elo_changes"]
        self.status.config(text=(
            f"Game #{result['id']} recorded.\n"
            f"White: {ch['white']['before']} -> {ch['white']['after']}   "
            f"Black: {ch['black']['before']} -> {ch['black']['after']}"
        ))
        self.on_success()
