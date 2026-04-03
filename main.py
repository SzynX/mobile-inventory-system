import customtkinter as ctk
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from logic import InventoryLogic

# Alapértelmezett megjelenés beállítása
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class MobiStockApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.logic = InventoryLogic()
        self.title("MobiStock v1.2 – Inventory & Profit Analytics")
        self.geometry("1100x750")

        # Rács elrendezés (Sidebar és Tartalom)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- OLDALSÁV (SIDEBAR) ---
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        self.logo_label = ctk.CTkLabel(self.sidebar, text="MOBISTOCK v1.2",
                                       font=ctk.CTkFont(size=22, weight="bold"))
        self.logo_label.pack(pady=30, padx=20)

        # Navigációs gombok
        self.btn_dash = ctk.CTkButton(self.sidebar, text="Dashboard", command=self.show_dashboard)
        self.btn_dash.pack(pady=10, padx=20)

        self.btn_list = ctk.CTkButton(self.sidebar, text="Inventory List", command=self.show_inventory)
        self.btn_list.pack(pady=10, padx=20)

        self.btn_add = ctk.CTkButton(self.sidebar, text="Add New Product", command=self.show_add_product)
        self.btn_add.pack(pady=10, padx=20)

        self.btn_stock = ctk.CTkButton(self.sidebar, text="Buy/Sell Stock", command=self.show_stock_update)
        self.btn_stock.pack(pady=10, padx=20)

        # --- FŐ TARTALOM TERÜLET ---
        self.main_view = ctk.CTkFrame(self, corner_radius=15, fg_color="transparent")
        self.main_view.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        # Kezdőképernyő betöltése
        self.show_dashboard()

    def clear_view(self):
        """Minden widget eltávolítása a fő tartalom területről váltáskor."""
        for widget in self.main_view.winfo_children():
            widget.destroy()

    # --- 1. DASHBOARD (FINANCIALS & CHARTS) ---
    def show_dashboard(self):
        self.clear_view()
        data = self.logic.get_financials()

        title = ctk.CTkLabel(self.main_view, text="Financial Performance", font=("Arial", 26, "bold"))
        title.pack(pady=(10, 20))

        # Statisztikai kártyák konténere
        stats_frame = ctk.CTkFrame(self.main_view, fg_color="transparent")
        stats_frame.pack(fill="x", padx=20)

        # Kártya: Bevétel
        card_rev = ctk.CTkFrame(stats_frame, width=250, height=120, border_width=1, border_color="#1fbbff")
        card_rev.grid(row=0, column=0, padx=10)
        card_rev.grid_propagate(False)
        ctk.CTkLabel(card_rev, text="Total Revenue", font=("Arial", 14)).pack(pady=(15, 5))
        ctk.CTkLabel(card_rev, text=f"{data['revenue']:,} Ft", font=("Arial", 22, "bold"), text_color="#1fbbff").pack()

        # Kártya: Profit
        card_profit = ctk.CTkFrame(stats_frame, width=250, height=120, border_width=2, border_color="#2ecc71")
        card_profit.grid(row=0, column=1, padx=10)
        card_profit.grid_propagate(False)
        ctk.CTkLabel(card_profit, text="Net Profit", font=("Arial", 14)).pack(pady=(15, 5))
        ctk.CTkLabel(card_profit, text=f"{data['profit']:,} Ft", font=("Arial", 22, "bold"),
                     text_color="#2ecc71").pack()

        # Kártya: Készletérték
        card_inv = ctk.CTkFrame(stats_frame, width=250, height=120, border_width=1)
        card_inv.grid(row=0, column=2, padx=10)
        card_inv.grid_propagate(False)
        ctk.CTkLabel(card_inv, text="Inventory Value", font=("Arial", 14)).pack(pady=(15, 5))
        ctk.CTkLabel(card_inv, text=f"{data['inventory_value']:,} Ft", font=("Arial", 22, "bold")).pack()

        # Grafikon hívása
        self.create_chart()

    def create_chart(self):
        models, stocks, profits = self.logic.get_model_stats()

        if not models:
            ctk.CTkLabel(self.main_view, text="\nNo data available for charts.", font=("Arial", 14, "italic")).pack()
            return

        # Matplotlib figura létrehozása
        fig, ax1 = plt.subplots(figsize=(7, 4), dpi=100)
        fig.patch.set_facecolor('#2b2b2b')  # Sötét mód háttér
        ax1.set_facecolor('#333333')

        # Oszlopdiagram a készletnek (Bal tengely)
        ax1.bar(models, stocks, color='#1fbbff', alpha=0.7, label="Stock Level")
        ax1.set_ylabel('Stock (qty)', color='#1fbbff', fontsize=10)
        ax1.tick_params(axis='y', labelcolor='#1fbbff')
        ax1.tick_params(axis='x', colors='white', rotation=20)
        ax1.set_title("Stock vs. Profit per Model", color="white", pad=20)

        # Profit vonaldiagram (Jobb tengely)
        ax2 = ax1.twinx()
        ax2.plot(models, profits, color='#2ecc71', marker='o', linewidth=2, markersize=8, label="Profit")
        ax2.set_ylabel('Profit (Ft)', color='#2ecc71', fontsize=10)
        ax2.tick_params(axis='y', labelcolor='#2ecc71')

        plt.tight_layout()

        # Ágyazás CustomTkinter-be
        canvas = FigureCanvasTkAgg(fig, master=self.main_view)
        canvas.draw()
        canvas.get_tk_widget().pack(pady=30, fill="both", expand=True)

    # --- 2. INVENTORY LIST VIEW ---
    def show_inventory(self):
        self.clear_view()
        ctk.CTkLabel(self.main_view, text="Current Stock & Performance", font=("Arial", 24, "bold")).pack(pady=10)

        scroll_frame = ctk.CTkScrollableFrame(self.main_view, width=850, height=500)
        scroll_frame.pack(pady=10, padx=10, fill="both", expand=True)

        header = ["Model", "Storage", "Buy Price", "Sell Price", "Stock", "Sold", "Net Profit"]
        for i, h in enumerate(header):
            ctk.CTkLabel(scroll_frame, text=h, font=("Arial", 12, "bold"), text_color="gray").grid(row=0, column=i,
                                                                                                   padx=15, pady=10)

        products = self.logic.get_all_products()
        for row_idx, p in enumerate(products, start=1):
            profit = p['sold_count'] * (p['sale_price'] - p['purchase_price'])

            ctk.CTkLabel(scroll_frame, text=p['model']).grid(row=row_idx, column=0, padx=15, pady=5)
            ctk.CTkLabel(scroll_frame, text=p['storage']).grid(row=row_idx, column=1, padx=15, pady=5)
            ctk.CTkLabel(scroll_frame, text=f"{p['purchase_price']:,}").grid(row=row_idx, column=2, padx=15, pady=5)
            ctk.CTkLabel(scroll_frame, text=f"{p['sale_price']:,}").grid(row=row_idx, column=3, padx=15, pady=5)
            ctk.CTkLabel(scroll_frame, text=f"{p['stock']}", font=("Arial", 13, "bold")).grid(row=row_idx, column=4,
                                                                                              padx=15, pady=5)
            ctk.CTkLabel(scroll_frame, text=f"{p['sold_count']}", text_color="orange").grid(row=row_idx, column=5,
                                                                                            padx=15, pady=5)
            ctk.CTkLabel(scroll_frame, text=f"{profit:,} Ft", text_color="#2ecc71", font=("Arial", 12, "bold")).grid(
                row=row_idx, column=6, padx=15, pady=5)

    # --- 3. ADD PRODUCT VIEW ---
    def show_add_product(self):
        self.clear_view()
        ctk.CTkLabel(self.main_view, text="Register New Device", font=("Arial", 24, "bold")).pack(pady=20)

        form = ctk.CTkFrame(self.main_view, fg_color="transparent")
        form.pack()

        # Mezők definíciója
        fields = ["Model Name", "Storage (e.g. 128GB)", "Color", "Purchase Price (Ft)", "Sale Price (Ft)",
                  "Initial Stock"]
        self.entries = {}

        for f in fields:
            ent = ctk.CTkEntry(form, placeholder_text=f, width=300, height=40)
            ent.pack(pady=8)
            self.entries[f] = ent

        def save():
            try:
                # Egyszerű validáció és mentés
                self.logic.add_product(
                    self.entries["Model Name"].get(),
                    self.entries["Storage (e.g. 128GB)"].get(),
                    self.entries["Color"].get(),
                    self.entries["Purchase Price (Ft)"].get(),
                    self.entries["Sale Price (Ft)"].get(),
                    self.entries["Initial Stock"].get()
                )
                messagebox.showinfo("Success", "New product added to inventory!")
                self.show_inventory()
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numbers for prices and stock!")

        ctk.CTkButton(self.main_view, text="Add Product", fg_color="#2ecc71", hover_color="#27ae60",
                      width=200, height=40, command=save).pack(pady=30)

    # --- 4. STOCK UPDATE (BUY/SELL) VIEW ---
    def show_stock_update(self):
        self.clear_view()
        ctk.CTkLabel(self.main_view, text="Stock Management", font=("Arial", 24, "bold")).pack(pady=20)

        products = self.logic.get_all_products()
        options = [f"{p['id']} - {p['model']} ({p['storage']})" for p in products]

        if not options:
            ctk.CTkLabel(self.main_view, text="Please add a product first!").pack()
            return

        combo = ctk.CTkComboBox(self.main_view, values=options, width=350, height=40)
        combo.pack(pady=15)

        amount_ent = ctk.CTkEntry(self.main_view, placeholder_text="Enter Quantity", width=200, height=40)
        amount_ent.pack(pady=15)

        def handle_update(is_sell):
            try:
                p_id = int(combo.get().split(" - ")[0])
                qty = int(amount_ent.get())
                if is_sell: qty = -abs(qty)  # Eladásnál negatív irány

                success, msg = self.logic.update_stock(p_id, qty)
                if success:
                    messagebox.showinfo("Success", msg)
                    self.show_dashboard()  # Frissítse a grafikonokat
                else:
                    messagebox.showerror("Error", msg)
            except:
                messagebox.showerror("Error", "Check your inputs!")

        btn_container = ctk.CTkFrame(self.main_view, fg_color="transparent")
        btn_container.pack(pady=20)

        ctk.CTkButton(btn_container, text="📥 Buy Stock", fg_color="#1fbbff", width=160, height=45,
                      command=lambda: handle_update(False)).grid(row=0, column=0, padx=10)

        ctk.CTkButton(btn_container, text="💸 Sell Stock", fg_color="#e74c3c", width=160, height=45,
                      command=lambda: handle_update(True)).grid(row=0, column=1, padx=10)


if __name__ == "__main__":
    app = MobiStockApp()
    app.mainloop()