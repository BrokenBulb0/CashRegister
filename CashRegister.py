#!/usr/bin/env python3.11

import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import csv
import os
from datetime import datetime

# Constants
TAX_PERCENTAGE = 12             
DISCOUNT_PERCENTAGE = 0

class FileManager:
    def __init__(self):
        self.app_folder = os.path.dirname(os.path.abspath(__file__))
        self.INVENTORY_FILE = os.path.join(self.app_folder, 'inventory.csv')
        self.SALES_FILE = os.path.join(self.app_folder, 'sales.csv')

    def create_csv_file(self, filename, header):
        if not os.path.exists(filename):
            with open(filename, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(header)

    def load_csv_data(self, filename):
        data = []
        try:
            with open(filename, newline='') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    data.append(row)
        except FileNotFoundError:
            data = []
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while loading data: {e}")
        return data

    def save_csv_data(self, filename, data, header):
        try:
            with open(filename, 'w', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=header)
                writer.writeheader()
                writer.writerows(data)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while saving data: {e}")

class InventoryItem:
    def __init__(self, Name, Price, Stock, Expiration=None):
        self.name = Name
        self.price = Price
        self.stock = int(Stock)
        self.expiration_date = Expiration

class InventoryManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Inventory Manager")
        self.file_manager = FileManager()
        
        self.items = self.load_items()
        self.cart = []
        self.sales = self.load_sales()
        
        self.create_gui()
        self.update_listbox()
        self.update_cart_display()
        self.update_cart_summary()
        self.update_sales()

    def load_items(self):
        return [InventoryItem(**item) for item in self.file_manager.load_csv_data(self.file_manager.INVENTORY_FILE)]

    def save_items(self):
        data = [{"Name": item.name, "Price": item.price, "Stock": item.stock, "Expiration": item.expiration_date} for item in self.items]
        self.file_manager.save_csv_data(self.file_manager.INVENTORY_FILE, data, ["Name", "Price", "Stock", "Expiration"])

    def add_item(self):
        name = self.name_entry.get()
        price = self.price_entry.get()
        stock = self.stock_entry.get()
        expiration_date = self.expiration_date_entry.get()

        if name and price:
            try:
                price = float(price)
                stock = int(stock) if stock else 0

                if stock < 0:
                    messagebox.showerror("Error", "Stock value cannot be negative.")
                    return

                new_item = InventoryItem(name, price, stock, expiration_date)
                self.items.append(new_item)
                self.save_items()
                self.update_listbox()
            except ValueError:
                messagebox.showerror("Error", "Invalid numeric input for Price or Stock.")
        else:
            messagebox.showerror("Error", "Please fill in all fields.")

    def delete_item(self):
        selected_item = self.get_selected_inventory_item()
        if selected_item:
            quantity_to_delete = simpledialog.askinteger("Delete Item", f"How much of '{selected_item.name}' would you like to delete?")
            if quantity_to_delete is not None:
                if quantity_to_delete <= selected_item.stock:
                    selected_item.stock -= quantity_to_delete
                    if selected_item.stock == 0:
                        self.items.remove(selected_item)
                    self.save_items()
                    self.update_listbox()
                else:
                    messagebox.showerror("Error", "Quantity to delete exceeds current stock.")

    def edit_item(self):
        selected_item = self.get_selected_inventory_item()
        if selected_item:
            new_price = simpledialog.askfloat("Edit Item", "Enter new price:")
            new_stock = simpledialog.askinteger("Edit Item", "Enter new stock:")
            new_expiration = simpledialog.askstring("Edit Item", "Enter new expiration date:")
            
            if new_price is not None:
                selected_item.price = new_price
            if new_stock is not None:
                selected_item.stock = new_stock
            if new_expiration:
                selected_item.expiration_date = new_expiration
            
            self.save_items()
            self.update_listbox()

    def get_selected_inventory_item(self):
        selected_item = self.item_listbox.get(tk.ACTIVE)
        if selected_item:
            for item in self.items:
                item_details = f"{item.name} | Price: ${item.price} | Stock: {item.stock} | Expiration: {item.expiration_date if item.expiration_date else 'N/A'}"
                if item_details == selected_item:
                    return item
        else:
            messagebox.showerror("Error", "Please select an item from the inventory.")
            return None

    def update_listbox(self):
        self.item_listbox.delete(0, tk.END)
        for item in self.items:
            details = f"{item.name} | Price: ${item.price} | Stock: {item.stock} | Expiration: {item.expiration_date if item.expiration_date else 'N/A'}"
            self.item_listbox.insert(tk.END, details)

    def update_cart_display(self):
        self.cart_listbox.delete(0, tk.END)
        for item in self.cart:
            details = f"Item: {item.name} | Stock: {item.stock} | Total Price: ${self.get_item_total_price(item):.2f}\n\n"
            self.cart_listbox.insert(tk.END, details)

    def update_cart_summary(self):
        total_price, subtotal, tax, discount = self.calculate_summary()
        self.total_price_var.set(f"${total_price:.2f}")
        self.subtotal_var.set(f"${subtotal:.2f}")
        self.tax_var.set(f"${tax:.2f} ({TAX_PERCENTAGE}%)")
        self.discount_var.set(f"${discount:.2f} ({DISCOUNT_PERCENTAGE}%)")

    def calculate_summary(self):
        total_price = sum(self.get_item_total_price(item) for item in self.cart)
        subtotal = total_price / (1 + TAX_PERCENTAGE / 100)
        tax = total_price - subtotal
        discount = total_price * (DISCOUNT_PERCENTAGE / 100)
        return total_price, subtotal, tax, discount

    def get_item_total_price(self, item):
        return float(item.price) * item.stock

    def add_to_cart(self):
        selected_item = self.get_selected_inventory_item()
        if selected_item:
            quantity_to_add = simpledialog.askinteger("Add to Cart", f"How much of '{selected_item.name}' would you like to add to the cart?")
            if quantity_to_add is not None:
                selected_item.stock = int(selected_item.stock)
                if quantity_to_add <= selected_item.stock:
                    selected_item.stock -= quantity_to_add
                    self.cart.append(InventoryItem(selected_item.name, selected_item.price, quantity_to_add))
                    self.update_cart_display()
                    self.update_cart_summary()
                else:
                    messagebox.showerror("Error", "Quantity to add exceeds current stock.")
                    messagebox.showinfo("Info", "No items available.")
                    return

                stock = quantity_to_add
                if stock is not None:
                    if stock > 0 and selected_item.stock >= stock:
                        item_name = selected_item.name
                        found = False
                        for cart_item in self.cart:
                            if cart_item.name == item_name:
                                found = True
                                break

                        if not found:
                            self.cart.append(InventoryItem(item_name, selected_item.price, stock, selected_item.expiration_date))

                        self.update_cart_summary()
                        self.update_cart_display()
                        self.save_items()
                    else:
                        messagebox.showerror("Error", "Please enter a valid stock value.")
        self.update_listbox()

    def checkout(self):
        if not self.cart:
            messagebox.showinfo("Info", "Cart is empty.")
            return

        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        total_price, _, _, _ = self.calculate_summary()

        sale_details_list = []

        for item in self.cart:
            sale_item = {
                "Sale Date": current_datetime,
                "Name": item.name,
                "Price": item.price,
                "Stock": item.stock,
            }
            sale_details_list.append(sale_item)

        for sale_item in sale_details_list:
            self.sales.append(sale_item)

        self.file_manager.save_csv_data(self.file_manager.SALES_FILE, self.sales, ["Sale Date", "Name", "Price", "Stock"])
        self.cart = []
        self.update_cart_summary()
        self.update_cart_display()
        self.update_sales()
        self.save_items()
        self.update_listbox()

    def load_sales(self):
        return self.file_manager.load_csv_data(self.file_manager.SALES_FILE)

    def update_sales(self):
        self.sales_listbox.delete(0, tk.END)
        for sale in self.sales:
            sale_details = f"Sale Date: {sale['Sale Date']} | Item: {sale['Name']} | " \
                           f"Price: ${sale['Price']} | Stock: {sale['Stock']} | " \
                           f"Tax: {TAX_PERCENTAGE}% | " \
                           f"Discount: {DISCOUNT_PERCENTAGE}%\n\n"
            self.sales_listbox.insert(tk.END, sale_details)

    def delete_sale(self):
        selected_sale = self.get_selected_sale()
        if selected_sale:
            sale_date = selected_sale["Sale Date"]
            sale_name = selected_sale["Name"]
            sale_stock = int(selected_sale["Stock"])
            self.sales.remove(selected_sale)
            self.file_manager.save_csv_data(self.file_manager.SALES_FILE, self.sales, ["Sale Date", "Name", "Price", "Stock"])

            for item in self.items:
                if item.name == sale_name:
                    item.stock += sale_stock
                    break

            self.update_sales()
            self.update_listbox()
            self.save_items()

    def get_selected_sale(self):
        selected_sale = self.sales_listbox.get(tk.ACTIVE)
        if selected_sale:
            for sale in self.sales:
                sale_details = f"Sale Date: {sale['Sale Date']} | Item: {sale['Name']} | " \
                               f"Price: ${sale['Price']} | Stock: {sale['Stock']} | " \
                               f"Tax: {TAX_PERCENTAGE}% | " \
                               f"Discount: {DISCOUNT_PERCENTAGE}%\n\n"
                if sale_details == selected_sale:
                    return sale
        else:
            messagebox.showerror("Error", "Please select a sale from the list.")
            return None

    def create_gui(self):
        self.tabControl = ttk.Notebook(self.root)
        self.inventory_tab = ttk.Frame(self.tabControl)
        self.cart_tab = ttk.Frame(self.tabControl)
        self.sales_tab = ttk.Frame(self.tabControl)
        self.preferences_tab = ttk.Frame(self.tabControl)
        self.tabControl.add(self.inventory_tab, text='Inventory')
        self.tabControl.add(self.cart_tab, text='Cart')
        self.tabControl.add(self.sales_tab, text='Sales')
        self.tabControl.add(self.preferences_tab, text='Preferences')
        self.tabControl.pack(expand=1, fill='both')
        
        self.name_label = tk.Label(self.inventory_tab, text='Name:')
        self.name_label.grid(row=0, column=0)
        self.name_entry = tk.Entry(self.inventory_tab)
        self.name_entry.grid(row=0, column=1)
        
        self.price_label = tk.Label(self.inventory_tab, text='Price:')
        self.price_label.grid(row=0, column=2)
        self.price_entry = tk.Entry(self.inventory_tab)
        self.price_entry.grid(row=0, column=3)
        
        self.stock_label = tk.Label(self.inventory_tab, text='Stock:')
        self.stock_label.grid(row=0, column=4)
        self.stock_entry = tk.Entry(self.inventory_tab)
        self.stock_entry.grid(row=0, column=5)
        
        self.expiration_date_label = tk.Label(self.inventory_tab, text='Expiration Date:')
        self.expiration_date_label.grid(row=0, column=6)
        self.expiration_date_entry = tk.Entry(self.inventory_tab)
        self.expiration_date_entry.grid(row=0, column=7)
        
        self.add_button = tk.Button(self.inventory_tab, text='Add Item', command=self.add_item)
        self.add_button.grid(row=0, column=8)
        
        self.edit_button = tk.Button(self.inventory_tab, text='Edit Item', command=self.edit_item)
        self.edit_button.grid(row=2, column=0)
        
        self.item_listbox = tk.Listbox(self.inventory_tab, height=10, width=80)
        self.item_listbox.grid(row=1, column=0, columnspan=8)
        
        self.delete_button = tk.Button(self.inventory_tab, text='Delete Item', command=self.delete_item)
        self.delete_button.grid(row=2, column=1)
        
        self.add_to_cart_button = tk.Button(self.inventory_tab, text='Add to Cart', command=self.add_to_cart)
        self.add_to_cart_button.grid(row=2, column=2)
        
        self.cart_listbox = tk.Listbox(self.cart_tab, height=20, width=80)
        self.cart_listbox.grid(row=0, column=0, columnspan=5)
        
        self.delete_from_cart_button = tk.Button(self.cart_tab, text='Delete from Cart', command=self.delete_from_cart)
        self.delete_from_cart_button.grid(row=1, column=0)
        
        self.checkout_button = tk.Button(self.cart_tab, text='Checkout', command=self.checkout)
        self.checkout_button.grid(row=1, column=1)
        
        self.tax_label = tk.Label(self.cart_tab, text='Tax:')
        self.tax_label.grid(row=3, column=0)
        
        self.discount_label = tk.Label(self.cart_tab, text='Discount:')
        self.discount_label.grid(row=4, column=0)
        
        self.total_price_label = tk.Label(self.cart_tab, text='Total Price:')
        self.total_price_label.grid(row=5, column=0)
        
        self.total_price_var = tk.StringVar()
        self.total_price_var.set("$0.00")
       

        self.total_price_display = tk.Label(self.cart_tab, textvariable=self.total_price_var)
        self.total_price_display.grid(row=5, column=1)

        self.delete_sale_button = tk.Button(self.sales_tab, text='Delete Sale', command=self.delete_sale)
        self.delete_sale_button.grid(row=1, column=2)
        
        self.subtotal_label = tk.Label(self.cart_tab, text='Subtotal:')
        self.subtotal_label.grid(row=6, column=0)
        
        self.subtotal_var = tk.StringVar()
        self.subtotal_var.set("$0.00")
        self.subtotal_display = tk.Label(self.cart_tab, textvariable=self.subtotal_var)
        self.subtotal_display.grid(row=6, column=1)
        
        self.tax_var = tk.StringVar()
        self.tax_var.set("$0.00 (0%)")
        self.tax_display = tk.Label(self.cart_tab, textvariable=self.tax_var)
        self.tax_display.grid(row=3, column=1)
        
        self.discount_var = tk.StringVar()
        self.discount_var.set("$0.00 (0%)")
        self.discount_display = tk.Label(self.cart_tab, textvariable=self.discount_var)
        self.discount_display.grid(row=4, column=1)
        
        self.sales_listbox = tk.Listbox(self.sales_tab, height=20, width=80)
        self.sales_listbox.grid(row=0, column=0, columnspan=5)
        
        self.tax_preference_label = tk.Label(self.preferences_tab, text='Tax Percentage:')
        self.tax_preference_label.grid(row=0, column=0)
        
        self.tax_preference_entry = tk.Entry(self.preferences_tab)
        self.tax_preference_entry.insert(0, TAX_PERCENTAGE)
        self.tax_preference_entry.grid(row=0, column=1)
        
        self.discount_preference_label = tk.Label(self.preferences_tab, text='Discount Percentage:')
        self.discount_preference_label.grid(row=1, column=0)
        
        self.discount_preference_entry = tk.Entry(self.preferences_tab)
        self.discount_preference_entry.insert(0, DISCOUNT_PERCENTAGE)
        self.discount_preference_entry.grid(row=1, column=1)
        
        self.update_preferences_button = tk.Button(self.preferences_tab, text='Update Preferences', command=self.update_preferences)
        self.update_preferences_button.grid(row=2, column=0, columnspan=2)

    def delete_from_cart(self):
        selected_item = self.get_selected_cart_item()
        if selected_item:
            quantity_to_delete = simpledialog.askinteger("Delete from Cart", f"How much of '{selected_item.name}' would you like to delete?")
            if quantity_to_delete is not None:
                if quantity_to_delete <= selected_item.stock:
                    selected_item.stock -= quantity_to_delete
                    if selected_item.stock == 0:
                        self.cart.remove(selected_item)

                    for item in self.items:
                        if item.name == selected_item.name:
                            item.stock += quantity_to_delete
                            break

                    self.update_cart_summary()
                    self.update_cart_display()
                    self.save_items()
                    self.update_listbox()
                else:
                    messagebox.showerror("Error", "Quantity to delete exceeds cart stock.")

    def get_selected_cart_item(self):
        selected_item = self.cart_listbox.get(tk.ACTIVE)
        if selected_item:
            for item in self.cart:
                item_details = f"Item: {item.name} | Stock: {item.stock} | Total Price: ${self.get_item_total_price(item):.2f}\n\n"
                if item_details == selected_item:
                    return item
        else:
            messagebox.showerror("Error", "Please select an item from the cart.")
            return None

    def update_preferences(self):
        global TAX_PERCENTAGE, DISCOUNT_PERCENTAGE
        new_tax_percentage = self.tax_preference_entry.get()
        new_discount_percentage = self.discount_preference_entry.get()
        try:
            TAX_PERCENTAGE = float(new_tax_percentage)
            DISCOUNT_PERCENTAGE = float(new_discount_percentage)
            self.update_cart_summary()
        except ValueError:
            messagebox.showerror("Error", "Invalid input for Tax or Discount Percentage.")

if __name__ == "__main__":
    root = tk.Tk()
    app = InventoryManager(root)
    root.mainloop()
