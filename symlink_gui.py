import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import platform


class SymlinkCreator:
    def __init__(self, root):
        self.root = root
        self.root.title("Symlink Creator")
        self.root.geometry("700x500")
        self.root.minsize(600, 400)

        self.selected_files = []
        self.destination_folder = ""

        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        source_frame = ttk.LabelFrame(
            main_frame, text="Source Files", padding="10")
        source_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.files_listbox = tk.Listbox(
            source_frame, selectmode=tk.EXTENDED, height=10)
        self.files_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(
            source_frame, orient=tk.VERTICAL, command=self.files_listbox.yview
        )
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.files_listbox.config(yscrollcommand=scrollbar.set)

        source_buttons_frame = ttk.Frame(main_frame)
        source_buttons_frame.pack(fill=tk.X, padx=5, pady=5)

        add_files_btn = ttk.Button(
            source_buttons_frame, text="Add Files", command=self.add_files
        )
        add_files_btn.pack(side=tk.LEFT, padx=5)

        remove_files_btn = ttk.Button(
            source_buttons_frame, text="Remove Selected", command=self.remove_files
        )
        remove_files_btn.pack(side=tk.LEFT, padx=5)

        clear_files_btn = ttk.Button(
            source_buttons_frame, text="Clear All", command=self.clear_files
        )
        clear_files_btn.pack(side=tk.LEFT, padx=5)

        dest_frame = ttk.LabelFrame(
            main_frame, text="Destination Folder", padding="10")
        dest_frame.pack(fill=tk.X, padx=5, pady=5)

        self.dest_entry = ttk.Entry(dest_frame)
        self.dest_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        dest_btn = ttk.Button(
            dest_frame, text="Browse...", command=self.select_destination
        )
        dest_btn.pack(side=tk.RIGHT, padx=5)

        options_frame = ttk.LabelFrame(
            main_frame, text="Options", padding="10")
        options_frame.pack(fill=tk.X, padx=5, pady=5)

        self.link_type = tk.StringVar(value="symbolic")

        symbolic_radio = ttk.Radiobutton(
            options_frame,
            text="Symbolic Links",
            value="symbolic",
            variable=self.link_type,
        )
        symbolic_radio.pack(side=tk.LEFT, padx=(0, 20))

        hard_radio = ttk.Radiobutton(
            options_frame, text="Hard Links", value="hard", variable=self.link_type
        )
        hard_radio.pack(side=tk.LEFT)

        create_btn = ttk.Button(
            main_frame, text="Create Links", command=self.create_links
        )
        create_btn.pack(pady=10)

        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(
            main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W
        )
        status_bar.pack(fill=tk.X, padx=5, pady=5)

    def add_files(self):
        files = filedialog.askopenfilenames(title="Select Files")
        if files:
            for file in files:
                if file not in self.selected_files:
                    self.selected_files.append(file)
                    self.files_listbox.insert(tk.END, os.path.basename(file))
            self.status_var.set(f"{len(files)} file(s) added")

    def remove_files(self):
        selected_indices = self.files_listbox.curselection()
        if not selected_indices:
            return

        for i in sorted(selected_indices, reverse=True):
            self.files_listbox.delete(i)
            self.selected_files.pop(i)

        self.status_var.set(f"{len(selected_indices)} file(s) removed")

    def clear_files(self):
        self.files_listbox.delete(0, tk.END)
        self.selected_files.clear()
        self.status_var.set("All files cleared")

    def select_destination(self):
        folder = filedialog.askdirectory(title="Select Destination Folder")
        if folder:
            self.destination_folder = folder
            self.dest_entry.delete(0, tk.END)
            self.dest_entry.insert(0, folder)
            self.status_var.set(f"Destination folder set to: {folder}")

    def create_links(self):
        if not self.selected_files:
            messagebox.showwarning(
                "No Files", "Please select at least one source file."
            )
            return

        if not self.destination_folder:
            messagebox.showwarning(
                "No Destination", "Please select a destination folder."
            )
            return

        if not os.path.exists(self.destination_folder):
            messagebox.showerror("Error", "Destination folder does not exist.")
            return

        success_count = 0
        error_count = 0
        error_messages = []

        for source_file in self.selected_files:
            dest_path = os.path.join(
                self.destination_folder, os.path.basename(source_file)
            )

            if os.path.exists(dest_path):
                error_count += 1
                error_messages.append(
                    f"File already exists at destination: {dest_path}"
                )
                continue

            try:
                if self.link_type.get() == "symbolic":
                    self.create_symlink(source_file, dest_path)
                else:
                    self.create_hardlink(source_file, dest_path)
                success_count += 1
            except Exception as e:
                error_count += 1
                error_messages.append(
                    f"Error creating link for {os.path.basename(source_file)}: {str(e)}"
                )

        if error_count == 0:
            messagebox.showinfo(
                "Success", f"Successfully created {success_count} link(s)."
            )
            self.status_var.set(f"Created {success_count} link(s)")
        else:
            error_text = "\n".join(error_messages[:5])
            if len(error_messages) > 5:
                error_text += f"\nAnd {len(error_messages) - 5} more errors..."

            messagebox.showwarning(
                "Partial Success",
                f"Created {success_count} link(s), but encountered {error_count} error(s).\n\n{error_text}",
            )
            self.status_var.set(
                f"Created {success_count} link(s) with {error_count} error(s)"
            )

    def create_symlink(self, source, dest):
        """Create a symbolic link"""
        if platform.system() == "Windows":
            try:
                os.symlink(
                    source, dest, target_is_directory=os.path.isdir(source))
            except OSError as e:
                if "privilege" in str(e).lower() or "permission" in str(e).lower():
                    raise Exception(
                        "Unable to create symbolic link. On Windows, you need to run as Administrator or enable Developer Mode."
                    ) from e
                else:
                    raise
        else:
            os.symlink(source, dest)

    def create_hardlink(self, source, dest):
        """Create a hard link"""
        if os.path.isdir(source):
            raise Exception(
                "Hard links for directories are not supported on most systems."
            )
        os.link(source, dest)


if __name__ == "__main__":
    root = tk.Tk()
    app = SymlinkCreator(root)
    root.mainloop()
