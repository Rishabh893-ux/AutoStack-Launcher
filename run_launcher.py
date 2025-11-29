import subprocess
import tkinter as tk
from tkinter import scrolledtext
import os
import sys
import threading
import platform


ROOT = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(ROOT, "backend")
FRONTEND_DIR = os.path.join(ROOT, "frontend")

# ---------------------- CROSS-PLATFORM VENV PYTHON PATH ----------------------
if platform.system() == "Windows":
    VENV_PYTHON = os.path.join(BACKEND_DIR, "venv", "Scripts", "python.exe")
else:
    VENV_PYTHON = os.path.join(BACKEND_DIR, "venv", "bin", "python")

class LauncherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Travel Agent — One-Click Launcher")

        self.text = scrolledtext.ScrolledText(root, width=95, height=30)
        self.text.pack()

        frame = tk.Frame(root)
        frame.pack()

        self.start_btn = tk.Button(frame, text="Start", command=self.start_all)
        self.start_btn.pack(side=tk.LEFT, padx=10)

        self.stop_btn = tk.Button(frame, text="Stop", command=self.stop_all)
        self.stop_btn.pack(side=tk.LEFT, padx=10)

        self.backend_proc = None
        self.frontend_proc = None
        self.running = False

    def log(self, msg):
        self.text.insert(tk.END, msg + "\n")
        self.text.see(tk.END)

    # ------------------------------ BACKEND -------------------------------------

    def start_backend(self):
        self.log("[BACKEND] Starting...")

        # Create venv if missing
        if not os.path.exists(VENV_PYTHON):
            self.log("[BACKEND] Creating virtual environment...")
            subprocess.run([sys.executable, "-m", "venv", os.path.join(BACKEND_DIR, "venv")])

        # Install requirements
        self.log("[BACKEND] Installing dependencies...")
        subprocess.run(
            f'"{VENV_PYTHON}" -m pip install -r "{os.path.join(BACKEND_DIR, "requirements.txt")}"',
            shell=True
        )

        # Launch backend server
        self.log("[BACKEND] Launching Uvicorn...")
        self.backend_proc = subprocess.Popen(
            f'"{VENV_PYTHON}" -m uvicorn app.main:app --reload --port 8000',
            cwd=BACKEND_DIR,
            shell=True,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
        )

        threading.Thread(target=self.pipe_output, args=(self.backend_proc, "[BACKEND]")).start()

    # ------------------------------ FRONTEND -------------------------------------

    def start_frontend(self):
        self.log("[FRONTEND] Starting...")

        # Install frontend dependencies if missing
        if not os.path.exists(os.path.join(FRONTEND_DIR, "node_modules")):
            self.log("[FRONTEND] Installing npm packages...")
            subprocess.run("npm install", cwd=FRONTEND_DIR, shell=True)

        # Start Vite dev server
        self.log("[FRONTEND] Launching Vite...")
        self.frontend_proc = subprocess.Popen(
            "npm run dev",
            cwd=FRONTEND_DIR,
            shell=True,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
        )

        threading.Thread(target=self.pipe_output, args=(self.frontend_proc, "[FRONTEND]")).start()

    # ------------------------------ MAIN CONTROL -------------------------------------

    def start_all(self):
        if self.running:
            self.log("[INFO] Already running.")
            return

        self.running = True

        threading.Thread(target=self.start_backend).start()
        threading.Thread(target=self.start_frontend).start()

    def stop_all(self):
        self.running = False
        self.log("[SYSTEM] Stopping all processes...")

        if self.backend_proc:
            self.backend_proc.terminate()

        if self.frontend_proc:
            self.frontend_proc.terminate()

        self.log("[SYSTEM] All stopped.")

    def pipe_output(self, proc, prefix):
        for line in proc.stdout:
            self.log(f"{prefix} {line.strip()}")


if __name__ == "__main__":
    root = tk.Tk()
    app = LauncherApp(root)
    root.mainloop()
