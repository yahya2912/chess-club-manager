"""Register Player tab: POST /registrations."""
import tkinter as tk
from tkinter import ttk, messagebox

from chess_club_fe import api_client


class RegisterTab(ttk.Frame):
    def __init__(self, parent, on_success=None):
        super().__init__(parent)
        self.on_success = on_success or (lambda: None)
        self._player_ids = {}
        self._tournament_ids = {}

        form = ttk.Frame(self)
        form.pack(padx=20, pady=20, anchor="w")

        ttk.Label(form, text="Player:").grid(row=0, column=0, sticky="w", pady=4)
        self.player = ttk.Combobox(form, state="readonly", width=35)
        self.player.grid(row=0, column=1, pady=4)

        ttk.Label(form, text="Tournament:").grid(row=1, column=0, sticky="w", pady=4)
        self.tournament = ttk.Combobox(form, state="readonly", width=35)
        self.tournament.grid(row=1, column=1, pady=4)

        ttk.Label(form, text="Seed (optional):").grid(row=2, column=0, sticky="w", pady=4)
        self.seed = ttk.Entry(form, width=37)
        self.seed.grid(row=2, column=1, pady=4)

        ttk.Button(form, text="Register", command=self.submit).grid(
            row=3, column=1, sticky="e", pady=10)
        self.status = ttk.Label(form, text="")
        self.status.grid(row=4, column=0, columnspan=2, sticky="w")

        self.reload_options()

    def reload_options(self):
        try:
            players = api_client.get_players()
            tournaments = api_client.get_tournaments()
        except api_client.ApiError as e:
            self.status.config(text=f"Error: {e.detail}")
            return
        self._player_ids = {p["name"]: p["id"] for p in players}
        self._tournament_ids = {t["name"]: t["id"] for t in tournaments}
        self.player["values"] = list(self._player_ids.keys())
        self.tournament["values"] = list(self._tournament_ids.keys())
        if players:
            self.player.current(0)
        if tournaments:
            self.tournament.current(0)

    def submit(self):
        if not self.player.get() or not self.tournament.get():
            messagebox.showwarning("Missing", "Pick a player and a tournament.")
            return
        seed_val = self.seed.get().strip()
        try:
            seed = int(seed_val) if seed_val else None
        except ValueError:
            messagebox.showwarning("Invalid", "Seed must be a whole number.")
            return
        try:
            api_client.create_registration(
                self._player_ids[self.player.get()],
                self._tournament_ids[self.tournament.get()],
                seed=seed,
            )
        except api_client.ApiError as e:
            self.status.config(text=f"Error: {e.detail}")
            messagebox.showerror("Registration failed", e.detail)
            return
        self.status.config(text="Registered successfully.")
        self.on_success()
