import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import subprocess
import threading
import signal
import os
import getpass

class PackageManagerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Linux Package Manager GUI")
        self.geometry("900x600")
        self.configure(bg="#1e1e1e")

        self.search_var = tk.StringVar()
        self.packages = []
        self.active_process = None

        self.create_widgets()
        self.load_packages()

        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def create_widgets(self):
        top_frame = tk.Frame(self, bg="#1e1e1e")
        top_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(top_frame, text="Search:", fg="white", bg="#1e1e1e").pack(side=tk.LEFT)
        tk.Entry(top_frame, textvariable=self.search_var, width=30).pack(side=tk.LEFT, padx=5)
        tk.Button(top_frame, text="Search", command=self.search_packages).pack(side=tk.LEFT, padx=5)
        tk.Button(top_frame, text="Refresh", command=self.load_packages).pack(side=tk.LEFT, padx=5)
        tk.Button(top_frame, text="Update (apt-get update)", command=self.update_system).pack(side=tk.LEFT, padx=5)

        action_frame = tk.Frame(self, bg="#1e1e1e")
        action_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Button(action_frame, text="Upgrade Selected", command=self.confirm_upgrade).pack(side=tk.LEFT, padx=5)
        tk.Button(action_frame, text="Remove Selected", command=self.confirm_remove).pack(side=tk.LEFT, padx=5)

        self.tree = ttk.Treeview(self, columns=("Package", "Version"), show='headings', height=15)
        self.tree.heading("Package", text="Package")
        self.tree.heading("Version", text="Version")
        self.tree.pack(fill=tk.BOTH, expand=False, padx=10, pady=5)

        self.output_console = scrolledtext.ScrolledText(self, height=12, bg="black", fg="lime", font=("Courier", 10))
        self.output_console.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    def run_command_realtime(self, cmd, ask_password=False):
        def task():
            self.output_console.delete("1.0", tk.END)
            password = ""
            if ask_password:
                password = getpass.getpass("Enter your sudo password: ") + "\n"
            self.output_console.insert(tk.END, f"Running: {' '.join(cmd)}\n\n")

            try:
                self.active_process = subprocess.Popen(
                    cmd,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True
                )

                if ask_password:
                    self.active_process.stdin.write(password)
                    self.active_process.stdin.flush()

                for line in self.active_process.stdout:
                    self.output_console.insert(tk.END, line)
                    self.output_console.see(tk.END)

                self.active_process.wait()
                self.active_process = None
                self.load_packages()
            except Exception as e:
                self.output_console.insert(tk.END, f"\nError: {str(e)}")
                self.active_process = None

        threading.Thread(target=task).start()

    def load_packages(self):
        def task():
            self.tree.delete(*self.tree.get_children())
            try:
                result = subprocess.run(["dpkg-query", "-W", "-f=${Package} ${Version}\n"],
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
                self.packages = [line.split() for line in result.stdout.strip().split('\n') if line.strip()]
                for pkg in self.packages:
                    if len(pkg) == 2:
                        self.tree.insert('', 'end', values=(pkg[0], pkg[1]))
            except subprocess.CalledProcessError as e:
                messagebox.showerror("Error", e.stderr.strip())
        threading.Thread(target=task).start()

    def search_packages(self):
        query = self.search_var.get().lower()
        self.tree.delete(*self.tree.get_children())
        for pkg in self.packages:
            if query in pkg[0].lower():
                self.tree.insert('', 'end', values=(pkg[0], pkg[1]))

    def get_selected_package(self):
        selected = self.tree.focus()
        if selected:
            return self.tree.item(selected)["values"][0]
        return None

    def confirm_upgrade(self):
        pkg = self.get_selected_package()
        if not pkg:
            messagebox.showwarning("No selection", "Please select a package to upgrade.")
            return
        if messagebox.askyesno("Confirm Upgrade", f"Upgrade package: {pkg}?"):
            self.run_command_realtime(["sudo", "-S", "apt", "install", "--only-upgrade", pkg, "-y"], ask_password=True)

    def confirm_remove(self):
        pkg = self.get_selected_package()
        if not pkg:
            messagebox.showwarning("No selection", "Please select a package to remove.")
            return
        if messagebox.askyesno("Confirm Removal", f"Are you sure you want to remove {pkg}?"):
            self.run_command_realtime(["sudo", "-S", "apt", "remove", pkg, "-y"], ask_password=True)

    def update_system(self):
        if messagebox.askyesno("Run apt-get update", "Run system update now (apt-get update)?"):
            self.run_command_realtime(["sudo", "-S", "apt-get", "update"], ask_password=True)

    def on_close(self):
        if self.active_process and self.active_process.poll() is None:
            if messagebox.askyesno("Quit", "A process is still running. Do you want to terminate it?"):
                try:
                    self.active_process.terminate()
                except:
                    pass
        self.destroy()

if __name__ == "__main__":
    app = PackageManagerApp()
    app.mainloop()

