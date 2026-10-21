"""Tkinter GUI for the Student Marks Management System.

Uses student_manager.py for CSV loading, validation and saving.
Run: python gui_student_manager.py
"""

import tkinter as tk
from tkinter import messagebox, ttk

from student_manager import (
    add_record,
    calculate_grade,
    delete_record,
    load_records,
    update_record,
)


class StudentManagerGUI:
    def __init__(self, root):
        self.root = root
        root.title("Student Marks Management System")
        root.geometry("850x560")
        root.minsize(750, 480)
        self.records = load_records()
        self.id_var = tk.StringVar()
        self.name_var = tk.StringVar()
        self.subject_var = tk.StringVar()
        self.marks_var = tk.StringVar()
        self.search_var = tk.StringVar()
        self.build_ui()
        self.refresh_table()

    def build_ui(self):
        frame = ttk.LabelFrame(self.root, text="Student details", padding=12)
        frame.pack(fill="x", padx=15, pady=(12, 8))
        fields = [("Student ID", self.id_var), ("Name", self.name_var),
                  ("Subject", self.subject_var), ("Marks (0-100)", self.marks_var)]
        for row, (label, variable) in enumerate(fields):
            ttk.Label(frame, text=label).grid(row=row // 2, column=(row % 2) * 2,
                                                sticky="w", padx=5, pady=7)
            ttk.Entry(frame, textvariable=variable, width=29).grid(
                row=row // 2, column=(row % 2) * 2 + 1, sticky="ew", padx=5, pady=7)
        frame.columnconfigure(1, weight=1)
        frame.columnconfigure(3, weight=1)

        actions = ttk.Frame(self.root, padding=(15, 0))
        actions.pack(fill="x")
        ttk.Button(actions, text="Add", command=self.add).pack(side="left", padx=(0, 7))
        ttk.Button(actions, text="Update", command=self.update).pack(side="left", padx=7)
        ttk.Button(actions, text="Delete", command=self.delete).pack(side="left", padx=7)
        ttk.Button(actions, text="Clear", command=self.clear).pack(side="left", padx=7)
        ttk.Button(actions, text="Show All", command=self.refresh_table).pack(side="left", padx=7)

        search = ttk.Frame(self.root, padding=15)
        search.pack(fill="x")
        ttk.Label(search, text="Search by student ID:").pack(side="left")
        ttk.Entry(search, textvariable=self.search_var, width=24).pack(side="left", padx=8)
        ttk.Button(search, text="Search", command=self.search).pack(side="left")
        ttk.Button(search, text="Statistics", command=self.statistics).pack(side="right")

        table_frame = ttk.Frame(self.root, padding=(15, 0, 15, 10))
        table_frame.pack(fill="both", expand=True)
        columns = ("student_id", "name", "subject", "marks", "grade")
        self.table = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")
        for col, heading, width in zip(columns,
                                       ("Student ID", "Name", "Subject", "Marks", "Grade"),
                                       (110, 230, 180, 90, 85)):
            self.table.heading(col, text=heading)
            self.table.column(col, width=width, anchor="center" if col in ("marks", "grade") else "w")
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.table.yview)
        self.table.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.table.pack(side="left", fill="both", expand=True)
        self.table.bind("<<TreeviewSelect>>", self.select_row)
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(self.root, textvariable=self.status_var, padding=(15, 5)).pack(anchor="w")

    def refresh_table(self, shown=None):
        for item in self.table.get_children():
            self.table.delete(item)
        rows = self.records if shown is None else shown
        for row in rows:
            self.table.insert("", "end", values=(row["student_id"], row["name"],
                         row["subject"], row["marks"], calculate_grade(row["marks"])))
        self.status_var.set(f"Showing {len(rows)} record(s) | Total: {len(self.records)}")

    def select_row(self, _event):
        selection = self.table.selection()
        if not selection:
            return
        student_id, name, subject, marks, _grade = self.table.item(selection[0], "values")
        self.id_var.set(student_id)
        self.name_var.set(name)
        self.subject_var.set(subject)
        self.marks_var.set(marks)

    def clear(self):
        for variable in (self.id_var, self.name_var, self.subject_var, self.marks_var):
            variable.set("")
        self.table.selection_remove(self.table.selection())

    def perform(self, action, success_message):
        try:
            action()
            self.refresh_table()
            self.clear()
            messagebox.showinfo("Success", success_message)
        except (ValueError, OSError) as error:
            messagebox.showerror("Error", str(error))
            try:
                self.records = load_records()
                self.refresh_table()
            except (OSError, ValueError, KeyError):
                messagebox.showerror("Data Error", "Could not reload CSV. Check students.csv.")

    def add(self):
        self.perform(lambda: add_record(self.records, self.id_var.get(), self.name_var.get(),
                                        self.subject_var.get(), self.marks_var.get()),
                     "Student record added.")

    def update(self):
        self.perform(lambda: update_record(self.records, self.id_var.get(), self.subject_var.get(),
                                           self.name_var.get(), self.marks_var.get()),
                     "Student record updated.")

    def delete(self):
        if not self.id_var.get().strip() or not self.subject_var.get().strip():
            messagebox.showwarning("Select record", "Select a record to delete.")
            return
        if messagebox.askyesno("Confirm deletion", "Delete this student/subject record?"):
            self.perform(lambda: delete_record(self.records, self.id_var.get(),
                                               self.subject_var.get()), "Record deleted.")

    def search(self):
        query = self.search_var.get().strip().casefold()
        if not query:
            self.refresh_table()
        else:
            self.refresh_table([r for r in self.records if query in r["student_id"].casefold()])

    def statistics(self):
        if not self.records:
            messagebox.showinfo("Statistics", "No records available.")
            return
        scores = [float(r["marks"]) for r in self.records]
        messagebox.showinfo("Statistics",
                            f"Total records: {len(scores)}\n"
                            f"Average marks: {sum(scores) / len(scores):.2f}\n"
                            f"Highest marks: {max(scores):g}\n"
                            f"Lowest marks: {min(scores):g}")


def main():
    root = tk.Tk()
    try:
        StudentManagerGUI(root)
    except (OSError, ValueError, KeyError) as error:
        messagebox.showerror("Data Error", f"Could not open students.csv:\n{error}")
        root.destroy()
        return
    root.mainloop()


if __name__ == "__main__":
    main()
