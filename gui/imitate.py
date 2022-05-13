import tkinter
import typing

from requests_ja3.decoder import JA3
from requests_ja3.imitate.imitate import generate_imitation_libssl
from requests_ja3.imitate.test import ja3_from_any_ssl
import ssl as system_ssl

class JA3ImitatorGUI:
    def __init__(self):
        self.BG = "#000000"
        self.FG = "#00FF00"
        self.COMMON = {"font": "TkFixedFont", "bg": self.BG, "fg": self.FG}

        self.root = tkinter.Tk()
        self.root.wm_title("JA3 Imitator")

        self.container = tkinter.Frame(self.root, bg = self.BG)
        self.container.grid()

        self.target_fingerprint_label = tkinter.Label(self.container, text = "Target JA3: ", **self.COMMON)
        self.target_fingerprint_label.grid(row = 1, column = 0)
        self.target_fingerprint_var = tkinter.StringVar(self.container)
        self.target_fingerprint_field = tkinter.Entry(self.container, textvariable = self.target_fingerprint_var, **self.COMMON)
        self.target_fingerprint_field.grid(row = 1, column = 1)
        self.regenerate_button = tkinter.Button(self.container, text = "Regenerate fakessl", command = self._regenerate_fakessl, **self.COMMON)
        self.regenerate_button.grid(row = 2, columnspan = 2)

        self.ssl_type: str = "System SSL"
        self.current_ja3: typing.Optional[JA3] = None
        self.fakessl_in_use_var = tkinter.StringVar(self.root)
        self._update_fakessl_in_use_var ()

        self.fakessl_in_use_label = tkinter.Label(self.container, textvariable = self.fakessl_in_use_var, **self.COMMON)
        self.fakessl_in_use_label.grid(row = 0, columnspan = 2)
        self.test_button = tkinter.Button(self.container, text = "Test Current SSL", command = self._test_fakessl, **self.COMMON)
        self.test_button.grid(row = 3, columnspan = 2)
        self.test_result_var = tkinter.StringVar(self.container)
        self.test_result_var.set("JA3 from Test: (n/a)")
        self.test_result = tkinter.Label(self.container, textvariable = self.test_result_var, **self.COMMON)
        self.test_result.grid(row = 4, columnspan = 2)

        self.fakessl = system_ssl
    def _update_fakessl_in_use_var(self):
        new_value = f"Current SSL: {self.ssl_type}"
        if self.current_ja3 is not None:
            new_value += f" --> {self.current_ja3.to_hash()}"
        self.fakessl_in_use_var.set(new_value)
    def run(self):
        self.root.mainloop()
    def _regenerate_fakessl (self):
        target_fingerprint_str = self.target_fingerprint_var.get()
        self.current_ja3 = JA3.from_string(target_fingerprint_str)
        self.fakessl = generate_imitation_libssl(self.current_ja3, True)
        self.ssl_type = "fakessl"
        self._update_fakessl_in_use_var()
    def _test_fakessl (self):
        received_ja3, received_user_agent = ja3_from_any_ssl(self.fakessl, start_server = False)
        result_text = f"JA3 from Test: {received_ja3.to_hash()}"
        if self.ssl_type == "fakessl":
            try:
                self.current_ja3.print_comparison_with(received_ja3)
                result_text += " (MATCHES)"
            except AssertionError as e:
                print(e)
                result_text += " (DOESN'T MATCH)"
        self.test_result_var.set(result_text)

if __name__ == "__main__":
    JA3ImitatorGUI().run()
