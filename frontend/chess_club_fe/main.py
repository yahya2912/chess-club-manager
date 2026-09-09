"""Chess Club Manager — desktop frontend (tkinter). Entry point."""
import tkinter as tk
from tkinter import ttk

from chess_club_fe.tab_players import PlayersTab
from chess_club_fe.tab_standings import StandingsTab
from chess_club_fe.tab_history import HistoryTab
from chess_club_fe.tab_game import GameTab
from chess_club_fe.tab_register import RegisterTab
from chess_club_fe.tab_tournament import TournamentTab


def build_app():
    root = tk.Tk()
    root.title("Chess Club Manager")
    root.geometry("900x600")

    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True, padx=8, pady=8)

    standings = StandingsTab(notebook)
    history = HistoryTab(notebook)

    def refresh_reads():
        """Called after a write so dependent read views show fresh data."""
        players.load()
        standings.load_tournaments()
        history.load_players()

    players = PlayersTab(notebook, on_success=refresh_reads)
    game = GameTab(notebook, on_success=refresh_reads)
    register = RegisterTab(notebook, on_success=refresh_reads)
    tournament = TournamentTab(notebook, on_success=refresh_reads)

    notebook.add(players, text="Players")
    notebook.add(standings, text="Standings")
    notebook.add(history, text="Rating History")
    notebook.add(game, text="Record Game")
    notebook.add(register, text="Register Player")
    notebook.add(tournament, text="Create Tournament")

    return root


def main():
    root = build_app()
    root.mainloop()


if __name__ == "__main__":
    main()
