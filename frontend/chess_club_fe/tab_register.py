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

        ttk.Label(
            form,
            text="Player:"
        ).grid(row=0, column=0, sticky="w", pady=4)

        self.player = ttk.Combobox(
            form,
            state="readonly",
            width=35,
            postcommand=self.reload_options,
        )
        self.player.grid(row=0, column=1, pady=4)

        ttk.Label(
            form,
            text="Tournament:"
        ).grid(row=1, column=0, sticky="w", pady=4)

        self.tournament = ttk.Combobox(
            form,
            state="readonly",
            width=35,
            postcommand=self.reload_options,
        )
        self.tournament.grid(row=1, column=1, pady=4)

        ttk.Label(
            form,
            text="Seed (optional):"
        ).grid(row=2, column=0, sticky="w", pady=4)

        self.seed = ttk.Entry(form, width=37)
        self.seed.grid(row=2, column=1, pady=4)

        ttk.Button(
            form,
            text="Refresh",
            command=self.reload_options,
        ).grid(row=3, column=0, sticky="w", pady=10)

        ttk.Button(
            form,
            text="Register",
            command=self.submit,
        ).grid(row=3, column=1, sticky="e", pady=10)

        self.status = ttk.Label(form, text="")
        self.status.grid(
            row=4,
            column=0,
            columnspan=2,
            sticky="w",
        )

        self.reload_options()

    def reload_options(self):
        """Refresh players and tournaments from the API."""

        old_player = self.player.get()
        old_tournament = self.tournament.get()

        try:
            players = api_client.get_players()
            tournaments = api_client.get_tournaments()

        except api_client.ApiError as e:
            self.status.config(text=f"Error: {e.detail}")
            return

        # Use ID + name so duplicate names are safe.
        self._player_ids = {
            f'{p["id"]} - {p["name"]}': p["id"]
            for p in players
        }

        self._tournament_ids = {
            f'{t["id"]} - {t["name"]}': t["id"]
            for t in tournaments
        }

        player_values = list(self._player_ids.keys())
        tournament_values = list(self._tournament_ids.keys())

        self.player["values"] = player_values
        self.tournament["values"] = tournament_values

        if old_player in player_values:
            self.player.set(old_player)
        elif player_values:
            self.player.current(0)

        if old_tournament in tournament_values:
            self.tournament.set(old_tournament)
        elif tournament_values:
            self.tournament.current(0)

        self.status.config(
            text=f"{len(player_values)} players, "
                 f"{len(tournament_values)} tournaments"
        )

    def submit(self):
        if not self.player.get() or not self.tournament.get():
            messagebox.showwarning(
                "Missing",
                "Pick a player and a tournament.",
            )
            return

        seed_val = self.seed.get().strip()

        try:
            seed = int(seed_val) if seed_val else None
        except ValueError:
            messagebox.showwarning(
                "Invalid",
                "Seed must be a whole number.",
            )
            return

        try:
            api_client.create_registration(
                self._player_ids[self.player.get()],
                self._tournament_ids[self.tournament.get()],
                seed=seed,
            )

        except api_client.ApiError as e:
            self.status.config(text=f"Error: {e.detail}")
            messagebox.showerror(
                "Registration failed",
                e.detail,
            )
            return

        self.status.config(text="Registered successfully.")
        self.reload_options()
        self.on_success()
