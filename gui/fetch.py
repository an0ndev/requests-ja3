import copy
import functools
import threading
import tkinter
import datetime
import typing

from requests_ja3.decoder import JA3
from requests_ja3.imitate.imitate import generate_imitation_libssl
from requests_ja3.imitate.test_server import JA3Fetcher

class JA3FetcherGUI:
    def __init__(self):
        self.BG = "#000000"
        self.FG = "#00FF00"
        self.COMMON = {"font": "TkFixedFont", "bg": self.BG, "fg": self.FG}

        self.root = tkinter.Tk()
        self.root.title("JA3 Fetcher")
        self.root.wait_visibility()

        self.startup_msg = tkinter.Label(self.root, text = "Preparing fakessl...", **self.COMMON)
        self.startup_msg.grid()
        self.root.update_idletasks ()
        self.fakessl = generate_imitation_libssl (
            None,
            use_in_tree_libssl = True
        )
        self.startup_msg.grid_forget()
        self.startup_msg.destroy()

        self.container = tkinter.Frame(self.root, bg = self.BG)
        self.container.grid()

        self._fetch_thread = threading.Thread (target = self._fetch_func)
        self.output_header = tkinter.Label (self.container, text = "--- Received JA3s: ---", **self.COMMON)
        self.output_header.grid(row = 0)
        self.output_frame = tkinter.Frame(self.container, bg = self.BG)
        self.output_frame.grid(row = 1)
        self.current_output_frame_row = 0

        self.data_widgets = []
        self.first = True

        self.cancelled = False
        self.shut_down = False
        self.cancel_button = tkinter.Button (self.container, command = self._cancel, text = "Close", **self.COMMON, relief = tkinter.SOLID, borderwidth = 0)
        self.cancel_button.grid(row = 3)
        self.clear_button = tkinter.Button (self.container, command = self._clear, text = "Clear", **self.COMMON,
                                             relief = tkinter.SOLID, borderwidth = 0)
        self.clear_button.grid (row = 2)
        self.last_ja3: typing.Optional[JA3] = None
        self._fetch_thread.start ()
    def run (self):
        try:
            self.root.mainloop ()
        finally:
            self._shutdown_internal()
    def _cancel (self):
        self._shutdown_internal()
        self.root.destroy ()
    def _shutdown_internal(self):
        if self.shut_down: return
        self.fetcher.cancel ()
        self._fetch_thread.join ()
        self.shut_down = True
    def _copy (self, ja3: JA3):
        self.root.clipboard_clear()
        self.root.clipboard_append(ja3.to_string())
    def _clear(self):
        for data_widget in self.data_widgets:
            data_widget.grid_forget()
            data_widget.destroy()
        self.data_widgets = []
        self.current_output_frame_row = 0 if self.first else 1
    def _fetch_func (self):
        while True:
            self.fetcher = JA3Fetcher (self.fakessl)
            resp = self.fetcher.fetch ()
            if self.fetcher.cancelled: break
            ja3, user_agent = resp
            self.last_ja3 = ja3

            now = datetime.datetime.now ().strftime ("%X")

            if self.first:
                tkinter.Label (self.output_frame, text = "Time", **self.COMMON).grid (row = 0, column = 0)
                tkinter.Label (self.output_frame, text = "Reports As", **self.COMMON).grid (row = 0, column = 1)
                tkinter.Label (self.output_frame, text = "JA3 Hash", **self.COMMON).grid (row = 0, column = 2)
                tkinter.Label (self.output_frame, text = "Copy", **self.COMMON).grid (row = 0, column = 3)
                self.current_output_frame_row += 1
                self.first = False

            new_time = tkinter.Label (self.output_frame, text = now, **self.COMMON)
            new_time.grid (row = self.current_output_frame_row, column = 0)
            new_user_agent = tkinter.Label (self.output_frame, text = user_agent, **self.COMMON)
            new_user_agent.grid (row = self.current_output_frame_row, column = 1)
            new_hash = tkinter.Label (self.output_frame, text = ja3.to_hash(), **self.COMMON)
            new_hash.grid (row = self.current_output_frame_row, column = 2)
            new_copy_btn = tkinter.Button (self.output_frame, command = functools.partial (self._copy, ja3), text = "Copy", **self.COMMON,
                                               relief = tkinter.SOLID, borderwidth = 0)
            new_copy_btn.grid(row = self.current_output_frame_row, column = 3)

            self.data_widgets.append(new_time)
            self.data_widgets.append(new_user_agent)
            self.data_widgets.append(new_hash)
            self.data_widgets.append(new_copy_btn)

            self.current_output_frame_row += 1

if __name__ == "__main__":
    JA3FetcherGUI ().run ()
