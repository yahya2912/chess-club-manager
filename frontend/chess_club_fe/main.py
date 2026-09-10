"""Chess Club Manager — desktop frontend (tkinter). Entry point."""
import os
import tkinter as tk
from tkinter import ttk, messagebox

from chess_club_fe import api_client
from chess_club_fe.tab_players import PlayersTab
from chess_club_fe.tab_standings import StandingsTab
from chess_club_fe.tab_history import HistoryTab
from chess_club_fe.tab_game import GameTab
from chess_club_fe.tab_register import RegisterTab
from chess_club_fe.tab_tournament import TournamentTab


def connection_dialog(root):
    """Ask for API URL and X-API-Key before opening the main application."""
    dialog = tk.Toplevel(root)
    dialog.title("Connect to Chess Club API")
    dialog.resizable(False, False)

    # Keep the dialog independent from the withdrawn root window. On macOS,
    # making it transient to a withdrawn parent can leave the process visible
    # in the Dock while the dialog itself never appears.
    frame = ttk.Frame(dialog, padding=16)
    frame.pack(fill="both", expand=True)

    ttk.Label(frame, text="API URL").grid(row=0, column=0, sticky="w", pady=(0, 6))
    url_var = tk.StringVar(value=os.environ.get("CHESS_API_URL", "http://127.0.0.1:8000"))
    url_entry = ttk.Entry(frame, textvariable=url_var, width=44)
    url_entry.grid(row=1, column=0, sticky="ew", pady=(0, 12))

    ttk.Label(frame, text="X-API-Key").grid(row=2, column=0, sticky="w", pady=(0, 6))
    key_var = tk.StringVar(value=os.environ.get("CHESS_API_KEY", ""))
    key_entry = ttk.Entry(frame, textvariable=key_var, width=44, show="*")
    key_entry.grid(row=3, column=0, sticky="ew", pady=(0, 12))

    connected = {"ok": False}

    def connect():
        url = url_var.get().strip()
        key = key_var.get().strip()
        if not url or not key:
            messagebox.showerror("Connection", "Enter both the API URL and X-API-Key.", parent=dialog)
            return

        api_client.configure(url, key)
        try:
            api_client.get_players()
        except api_client.ApiError as exc:
            messagebox.showerror("Connection failed", str(exc), parent=dialog)
            return

        connected["ok"] = True
        dialog.destroy()

    ttk.Button(frame, text="Connect", command=connect).grid(row=4, column=0, sticky="e")

    dialog.protocol("WM_DELETE_WINDOW", dialog.destroy)
    dialog.bind("<Return>", lambda _event: connect())

    # Ensure the dialog is visible and focused, including when launched from a
    # terminal on macOS where tkinter windows can otherwise open behind others.
    dialog.update_idletasks()
    width = dialog.winfo_reqwidth()
    height = dialog.winfo_reqheight()
    x = max(0, (dialog.winfo_screenwidth() - width) // 2)
    y = max(0, (dialog.winfo_screenheight() - height) // 3)
    dialog.geometry(f"+{x}+{y}")
    dialog.deiconify()
    dialog.lift()
    try:
        dialog.attributes("-topmost", True)
        dialog.after(250, lambda: dialog.attributes("-topmost", False))
    except tk.TclError:
        pass
    dialog.focus_force()
    url_entry.focus_set()
    dialog.grab_set()

    root.wait_window(dialog)
    return connected["ok"]


def build_app():
    root = tk.Tk()
    root.title("Chess Club Manager")
    root.geometry("900x600")
    root.withdraw()

    if not connection_dialog(root):
        root.destroy()
        return None

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

    root.deiconify()
    return root


def main():
    root = build_app()
    if root is not None:
        root.mainloop()


if __name__ == "__main__":
    main()
