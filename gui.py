import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import tkinter.font as tkFont
import pandas as pd
from datetime import datetime
from ttkthemes import ThemedTk
from salary_calc import SalaryCalculator
import threading


class SalaryGui:
    def __init__(self, root):
        """
        constructor for the SalaryGui class
        """
        self.root = root
        self.root.title('Salary Calculator for team 3')
        self.root.iconbitmap("Celery.ico")
        #self.root.geometry("1200x900")
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = min(int(screen_width * 0.7), screen_width)
        window_height = min(int(screen_height * 0.7), screen_height)
        self.root.geometry(f"{window_width}x{window_height}")
        self.root.minsize(800, 600)

        self.root.set_theme("arc")
        self.df = None # DataFrame to store the loaded Excel data
        self.salary_calculator = SalaryCalculator()

        # Define a custom font for widgets with increased size and bold weight
        self.custom_font = tkFont.Font(family="Rubik", size=14)

        # Create a custom style
        self.style = ttk.Style()
        self.style.configure("Custom.TButton", font=self.custom_font)
        self.style.configure("Custom.TLabel", font=self.custom_font)
        self.style.configure("Custom.TCheckbutton", font=self.custom_font)
        self.style.configure("Custom.TLabelframe.Label", font=self.custom_font)

        self.create_widgets()






    def create_widgets(self):
        """
        Create the widgets for the GUI.
        """
        # Create a canvas to allow for scrolling if the window is too small
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill='both', expand=True)

        canvas = tk.Canvas(main_frame)
        canvas.pack(side=tk.LEFT, fill='both', expand=True)

        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill='y')

        canvas.configure(yscrollcommand=scrollbar.set)  # Link the scrollbar to the canvas
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))  # Update scroll region

        # Frame for all widgets inside the canvas
        frame_inside_canvas = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=frame_inside_canvas, anchor="nw")

        # Frame for loading the Excel file
        load_frame = ttk.Frame(frame_inside_canvas)
        load_frame.grid(row=0, column=0, pady=15, sticky="ew")
        ttk.Button(load_frame, text="Load Excel File", command=self.load_excel_file, style="Custom.TButton").pack()

        # Frame for Treeview (with a scrollbar)
        tree_frame = ttk.Frame(frame_inside_canvas)
        tree_frame.grid(row=1, column=0, pady=15, sticky="ew")

        # Scrollbar for the Treeview
        tree_scroll = ttk.Scrollbar(tree_frame)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Treeview to display data
        self.tree = ttk.Treeview(tree_frame, columns=("Date", "Day of Week", "Role", "Entry Time", "Exit Time", "Control Room", "Pay", "Travel Charge"),
                                show='headings', selectmode='browse', yscrollcommand=tree_scroll.set)
        self.tree.heading("Date", text="Date", anchor='center')
        self.tree.heading("Day of Week", text="Day of Week", anchor='center')
        self.tree.heading("Role", text="Role", anchor='center')
        self.tree.heading("Entry Time", text="Entry Time", anchor='center')
        self.tree.heading("Exit Time", text="Exit Time", anchor='center')
        self.tree.heading("Control Room", text="Control Room", anchor='center')
        self.tree.heading("Pay", text="Pay", anchor='center')
        self.tree.heading("Travel Charge", text="Travel Charge", anchor='center')

        self.tree.column("Date", anchor='center', width=100)
        self.tree.column("Day of Week", anchor='center', width=120)
        self.tree.column("Role", anchor='center', width=200)
        self.tree.column("Entry Time", anchor='center', width=100)
        self.tree.column("Exit Time", anchor='center', width=100)
        self.tree.column("Control Room", anchor='center', width=100)
        self.tree.column("Pay", anchor='center', width=100)
        self.tree.column("Travel Charge", anchor='center', width=120)

        self.tree.pack(fill='both', expand=True, padx=15)
        tree_scroll.config(command=self.tree.yview)

        # Bind the TreeviewSelect event to the on_row_select method
        self.tree.bind('<<TreeviewSelect>>', self.on_row_select)

        # Frame for editing selected row
        edit_frame = ttk.LabelFrame(frame_inside_canvas, text="Edit Selected Row", style="Custom.TLabelframe")
        edit_frame.grid(row=2, column=0, pady=20, padx=20, sticky="ew")

        # Entry for date
        ttk.Label(edit_frame, text="Date:", style="Custom.TLabel").grid(row=0, column=0, sticky="w", padx=15, pady=10)
        self.date_var = tk.StringVar()
        self.date_entry = ttk.Entry(edit_frame, textvariable=self.date_var, state='readonly', width=25, font=self.custom_font)
        self.date_entry.grid(row=0, column=1, padx=15, pady=10, sticky="ew")

        # Entry for day of the week
        ttk.Label(edit_frame, text="Day of the Week:", style="Custom.TLabel").grid(row=0, column=2, sticky="w", padx=15, pady=10)
        self.date_of_week_var = tk.StringVar()
        self.date_of_week_entry = ttk.Entry(edit_frame, textvariable=self.date_of_week_var, width=25, font=self.custom_font)
        self.date_of_week_entry.grid(row=0, column=3, padx=15, pady=10, sticky="ew")

        # Entry for role
        ttk.Label(edit_frame, text="Role:", style="Custom.TLabel").grid(row=1, column=0, sticky="w", padx=15, pady=10)
        self.role_var = tk.StringVar()
        self.role_entry = ttk.Entry(edit_frame, textvariable=self.role_var, width=25, font=self.custom_font)
        self.role_entry.grid(row=1, column=1, padx=15, pady=10, sticky="ew")

        # Entry for start time
        ttk.Label(edit_frame, text="Entry Time (HH:MM):", style="Custom.TLabel").grid(row=2, column=0, sticky="w", padx=15, pady=10)
        self.entry_time_var = tk.StringVar()
        self.entry_time_entry = ttk.Entry(edit_frame, textvariable=self.entry_time_var, width=25, font=self.custom_font)
        self.entry_time_entry.grid(row=2, column=1, padx=15, pady=10, sticky="ew")

        # Entry for exit time
        ttk.Label(edit_frame, text="Exit Time (HH:MM):", style="Custom.TLabel").grid(row=3, column=0, sticky="w", padx=15, pady=10)
        self.exit_time_var = tk.StringVar()
        self.exit_time_entry = ttk.Entry(edit_frame, textvariable=self.exit_time_var, width=25, font=self.custom_font)
        self.exit_time_entry.grid(row=3, column=1, padx=15, pady=10, sticky="ew")

        # Checkbutton for control room
        self.control_room_var = tk.BooleanVar()
        self.control_room_checkbox = ttk.Checkbutton(edit_frame, text="In Control Room", variable=self.control_room_var, command=self.update_control_room, style="Custom.TCheckbutton")
        self.control_room_checkbox.grid(row=4, column=0, columnspan=2, padx=15, pady=10, sticky="ew")

        # Checkbutton for holiday
        self.holiday_var = tk.BooleanVar()
        ttk.Checkbutton(edit_frame, text="Holiday", variable=self.holiday_var, style="Custom.TCheckbutton").grid(row=4, column=1, columnspan=2, padx=15, pady=10)

        # Checkbutton for last day of holiday
        self.last_day_holiday_var = tk.BooleanVar()
        ttk.Checkbutton(edit_frame, text="Last Day of Holiday", variable=self.last_day_holiday_var, style="Custom.TCheckbutton").grid(row=4, column=2, columnspan=2, padx=15, pady=10)

        # Button to update selected row
        update_button = ttk.Button(edit_frame, text="Update Selected Row", command=self.update_row, style="Custom.TButton")
        update_button.grid(row=5, column=0, columnspan=1, padx=10, pady=20, sticky="w")

        # Button to calculate the pay for each day
        calculate_pay_button = ttk.Button(edit_frame, text="Calculate Pay for Each Day", command=self.calculate_pay, style="Custom.TButton")
        calculate_pay_button.grid(row=5, column=1, padx=10, pady=20, sticky="w")

        # Button to calculate the total pay
        total_pay_button = ttk.Button(edit_frame, text="Calculate Total Pay", command=self.calculate_total_pay, style="Custom.TButton")
        total_pay_button.grid(row=5, column=2, padx=10, pady=20, sticky="w")

        # Button to select all 'In Control Room' checkboxes
        select_all_button = ttk.Button(edit_frame, text="Select All CR", command=self.select_all_in_control_room, style="Custom.TButton")
        select_all_button.grid(row=5, column=3, padx=10, pady=20, sticky="w")

        # Label to display the total pay
        ttk.Label(edit_frame, text="Total Pay:", style="Custom.TLabel").grid(row=5, column=3, padx=10, pady=20, sticky="e")
        self.total_pay_var = tk.StringVar(value="0.00")
        self.total_pay_label = ttk.Label(edit_frame, textvariable=self.total_pay_var, style="Custom.TLabel")
        self.total_pay_label.grid(row=5, column=4, padx=10, pady=20, sticky="w")

    
    

    
    def update_control_room(self):
        """
        Update the 'In Control Room' value in the selected row based on the checkbox state
        and persist the change in both the Treeview and the underlying data structure.
        """
        selected_item = self.tree.selection()  # Get the selected item in the Treeview
        if not selected_item:
            messagebox.showerror("No Selection", "Please select a row to update.")
            return

        # Get the value of the checkbox and set it as "Yes" or "No"
        in_control_room = "Yes" if self.control_room_var.get() else "No"

        # Get existing values from the selected item in the Treeview
        values = self.tree.item(selected_item, 'values')

        # Ensure there are 8 values (in case Travel Charge or Pay columns are missing)
        if len(values) < 8:
            values = list(values) + [''] * (8 - len(values))

        # Create a new tuple with the updated "In Control Room" value
        updated_values = (
            values[0],  # Date
            values[1],  # Day of Week
            values[2],  # Role
            values[3],  # Entry Time
            values[4],  # Exit Time
            in_control_room,  # Updated Control Room value (Yes/No based on checkbox)
            values[6],  # Pay
            values[7]   # Travel Charge
        )

        # Update the Treeview with the new values
        self.tree.item(selected_item, values=updated_values)

        # Persist the change in the underlying data structure (e.g., self.daily_records)
        row_index = self.tree.index(selected_item)  # Get the index of the selected row
        if row_index < len(self.daily_records):
            self.daily_records[row_index]['control_room'] = in_control_room
        




    def select_all_in_control_room(self):
        """
        Set the 'In Control Room' checkbox to 'Yes' for all rows in the Treeview.
        """
        for item in self.tree.get_children():
            values = self.tree.item(item, 'values')

            if len(values) < 8:
                values = list(values) + [''] * (8 - len(values))

            # update control room value to "Yes"
            updated_values = (
                values[0],  # Date
                values[1],  # Day of Week
                values[2],  # Role
                values[3],  # Entry Time
                values[4],  # Exit Time
                "Yes",      # Set 'In Control Room' to "Yes"
                values[6],  # Pay
                values[7]   # Travel Charge
            )

            self.tree.item(item, values=updated_values)





    def load_excel_file(self):
        """
        Load an Excel file and populate the treeview with the data.
        """
        file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
        
        if not file_path:
            return

        if not file_path.endswith(('.xlsx', '.xls')):
            messagebox.showerror("Invalid File", "Please upload a valid Excel file (.xlsx or .xls).")
            return

        try:
            # Offload heavy file loading to a separate thread to keep the GUI responsive
            threading.Thread(target=self._load_file_thread, args=(file_path,)).start()
        except Exception as e:
            messagebox.showerror("Error", f"Error loading Excel file: {e}")






    def _load_file_thread(self, file_path):
        """
        Load the Excel file in a separate thread to keep the GUI responsive.
        """
        try:
            # Load the file and rename columns
            self.df = pd.read_excel(file_path, skiprows=4, header=0, engine='openpyxl')

            column_mapping = {
                'תאריך': 'Date',
                'תפקיד': 'Role',
                'כניסה': 'Entry Time',
                'יציאה': 'Exit Time',
                'סיכום': 'Summary'
            }
            self.df.rename(columns=column_mapping, inplace=True)

            # Check for required columns
            required_columns = {'Date', 'Role'}
            if not required_columns.issubset(self.df.columns):
                messagebox.showerror("Invalid Format", f"Excel file must contain columns: {', '.join(required_columns)}. Current columns are: {', '.join(self.df.columns)}")
                return

            # Update the Treeview on the main thread
            self.root.after(0, self._update_treeview)

        except Exception as e:
            messagebox.showerror("Error", f"Error loading Excel file: {e}")







    def _update_treeview(self):
        """
        Update the Treeview with the data from the loaded Excel file.
        """

        # clear any existing data in the Treeview
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Populate the Treeview
        for index, row in self.df.iterrows():
            if pd.isna(row['Role']) or row['Role'] == 'N/A':
                continue

            # Format the date
            date_str = pd.to_datetime(row['Date']).strftime('%Y-%m-%d') if pd.notna(row['Date']) else "Missing"
            role = row['Role']

            # Format entry and exit times to HH:MM, handle potential parsing issues
            try:
                entry_time = datetime.strptime(str(row['Entry Time']), '%H:%M:%S').strftime('%H:%M') if pd.notna(row['Entry Time']) else "Missing"
            except ValueError:
                entry_time = "Missing"

            try:
                exit_time = datetime.strptime(str(row['Exit Time']), '%H:%M:%S').strftime('%H:%M') if pd.notna(row['Exit Time']) else "Missing"
            except ValueError:
                exit_time = "Missing"

            # Calculate the day of the week from the date
            if pd.notna(row['Date']):
                day_of_week = pd.to_datetime(row['Date']).strftime('%A')  # Get full weekday name
            else:
                day_of_week = "Missing"

            # Insert the row into the Treeview, including the day of the week
            self.tree.insert("", "end", values=(date_str, day_of_week, role, entry_time, exit_time, "No", ""))





    def on_row_select(self, event):
        """
        Handle the event when a row is selected in the Treeview.
        Populate the selected row's data into the input fields.
        """
        selected_item = self.tree.selection()
        if not selected_item:
            return

        values = self.tree.item(selected_item, 'values')  # Get the values from the selected row

        # Ensure there are 8 values (in case Travel Charge or Pay columns are missing)
        if len(values) < 8:
            values = list(values) + [''] * (8 - len(values))

        # Populate the fields with the respective values from the selected row
        self.date_var.set(values[0])  # Date
        self.date_of_week_var.set(values[1])  # Day of Week
        self.role_var.set(values[2])  # Role
        self.entry_time_var.set(values[3])  # Entry Time
        self.exit_time_var.set(values[4])  # Exit Time

        # Update the "In Control Room" checkbox based on the selected row's data
        self.control_room_var.set(True if values[5] == "Yes" else False)







    def update_row(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("No Selection", "Please select a row to update.")
            return

        # Get the updated values from the entry fields and checkbox
        date_str = self.date_var.get()
        role = self.role_var.get()
        entry_time = self.entry_time_var.get()
        exit_time = self.exit_time_var.get()
        in_control_room = "Yes" if self.control_room_var.get() else "No"  # Get the correct value based on checkbox state

        # Update Treeview with new values
        day_of_week = self.get_day_of_week(date_str)  # Get the day of the week for the updated date
        self.tree.item(selected_item, values=(date_str, day_of_week, role, entry_time, exit_time, in_control_room,"0.00", "0.00"))

    # Helper function to get day of the week
    def get_day_of_week(self, date_str):
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").strftime('%A')
        except ValueError:
            return "Missing"







    def calculate_pay(self):
        """
        Calculate the pay for each row in the treeview and update the 'Pay' and 'Travel Charge' columns.
        """
        if self.df is None:
            messagebox.showerror("No Data", "Please load an Excel file first.")
            return

        try:
            for item in self.tree.get_children():
                values = self.tree.item(item, 'values')

                # Ensure the row has 8 values, fill with placeholder if needed
                if len(values) < 8:
                    values = list(values) + [''] * (8 - len(values))  # Add empty placeholders for missing columns

                # The values tuple now has 8 elements: Date, DayOfWeek, Role, Entry Time, Exit Time, Control Room, Pay, Travel Charge
                date_str, day_of_week, role, entry_time_str, exit_time_str, in_control_room, _, _ = values

                if entry_time_str == "Missing" or exit_time_str == "Missing":
                    total_pay_day = 0.0
                    travel_charge_day = 0.0
                else:
                    # Parse the date, start time, and end time
                    date = datetime.strptime(date_str, "%Y-%m-%d").date()
                    start_time = datetime.strptime(entry_time_str, "%H:%M").time()
                    end_time = datetime.strptime(exit_time_str, "%H:%M").time()
                    in_control_room_flag = True if in_control_room == "Yes" else False

                    # Determine if the workday is a Friday, Saturday, holiday, or last day of a holiday
                    is_friday = date.weekday() == 4  # 0 = Monday, 4 = Friday
                    is_saturday = date.weekday() == 5  # 5 = Saturday
                    is_holiday = self.holiday_var.get()  # From checkbox
                    is_last_day_of_holiday = self.last_day_holiday_var.get()  # From checkbox

                    # Use a temporary instance of SalaryCalculator to avoid accumulating pay
                    temp_calculator = SalaryCalculator()
                    temp_calculator.add_work_day(
                        date=date,
                        start_time=start_time,
                        end_time=end_time,
                        in_control_room=in_control_room_flag,
                        is_friday=is_friday,
                        is_saturday=is_saturday,
                        is_holiday=is_holiday,
                        is_last_day_of_holiday=is_last_day_of_holiday
                    )
                    total_pay_day = temp_calculator.total_pay()

                    # Calculate the travel charge using the same logic as in SalaryCalculator
                    travel_charge_day = temp_calculator.calculate_travel_charge(date, start_time, end_time, is_friday, is_saturday)

                # Update Treeview with the calculated pay and travel charge for that specific day
                self.tree.item(item, values=(date_str, day_of_week, role, entry_time_str, exit_time_str, in_control_room, f"{total_pay_day:.2f}", f"{travel_charge_day:.2f}"))

        except Exception as e:
            messagebox.showerror("Error", f"Error calculating pay: {e}")






    def calculate_total_pay(self):
        """
        Calculate the total pay for all days in the treeview.
        """
        total_pay = 0.0  

        try:
            for item in self.tree.get_children():
                values = self.tree.item(item, 'values')
                pay = values[6]  # Assuming 'Pay' is the seventh column (index 6)

                # Attempt to convert the pay value to float if it's not "Missing" or empty
                if pay != "Missing" and pay != "" and pay != "No":
                    try:
                        total_pay += float(pay)
                    except ValueError:
                        # Ignore any value that cannot be converted to a float
                        continue

            # Show the total pay in a message box
            self.total_pay_var.set(f"{total_pay:.2f} shekels")
        except Exception as e:
            messagebox.showerror("Error", f"Error calculating total pay: {e}")


if __name__ == "__main__":
    root = ThemedTk(theme="arc")
    app = SalaryGui(root)
    root.mainloop()

    