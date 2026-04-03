import customtkinter as ctk
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from logic import InventoryLogic

# Megjelenési beállítások
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class MobiStockV15(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Logikai modul példányosítása
        self.logic = InventoryLogic()

        # Ablak alapbeállításai
        self.title("MobiStock v1.5 - Professional Edition")
        self.geometry("1200x800")

        # Fő rács elrendezés (Oldalsáv + Tartalom)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- OLDALSÁV (SIDEBAR) ---
        self.sidebar = ctk.CTkFrame(self, width=260, corner_radius=0, fg_color="#1a1a1a")
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        # Logo és Verziószám
        self.logo_label = ctk.CTkLabel(self.sidebar, text="📱 MOBISTOCK",
                                       font=ctk.CTkFont(family="Verdana", size=24, weight="bold"),
                                       text_color="#3498db")
        self.logo_label.pack(pady=(30, 10), padx=20)

        self.version_label = ctk.CTkLabel(self.sidebar, text="Version 1.5 PRO",
                                          font=("Arial", 10), text_color="gray")
        self.version_label.pack(pady=(0, 30))

        # Navigációs gombok (padx eltávolítva a konstruktorból a hiba elkerülése végett)
        menu_items = [
            ("📊  Dashboard", self.show_dashboard),
            ("📦  Inventory List", self.show_inventory),
            ("➕  Add New Product", self.show_add_product),
            ("🔄  Stock Control", self.show_stock_update)
        ]

        for text, command in menu_items:
            btn = ctk.CTkButton(self.sidebar, text=text, command=command,
                                height=45, corner_radius=10,
                                font=("Arial", 14, "bold"),
                                fg_color="transparent", hover_color="#2c3e50",
                                anchor="w")
            btn.pack(pady=8, padx=15, fill="x")

        # --- FŐ TARTALOM TERÜLET ---
        self.main_view = ctk.CTkFrame(self, corner_radius=20, fg_color="#242424")
        self.main_view.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        # Kezdőoldal megjelenítése
        self.show_dashboard()

    def clear_view(self):
        """Minden widget eltávolítása a fő nézetből váltáskor."""
        for widget in self.main_view.winfo_children():
            widget.destroy()

    # --- 1. DASHBOARD NÉZET ---
    def show_dashboard(self):
        self.clear_view()
        data = self.logic.get_financials()

        ctk.CTkLabel(self.main_view, text="Business Performance Dashboard",
                     font=("Arial", 28, "bold")).pack(pady=(20, 20), padx=30, anchor="w")

        # Statisztikai kártyák (Grid elrendezésben)
        cards_frame = ctk.CTkFrame(self.main_view, fg_color="transparent")
        cards_frame.pack(fill="x", padx=20)

        self.create_card(cards_frame, 0, "TOTAL REVENUE", f"{data['revenue']:,} Ft", "#3498db")
        self.create_card(cards_frame, 1, "NET PROFIT", f"{data['profit']:,} Ft", "#2ecc71")
        self.create_card(cards_frame, 2, "STOCK VALUE", f"{data['inv_value']:,} Ft", "#9b59b6")

        warn_color = "#e74c3c" if data['low_stock_count'] > 0 else "#2ecc71"
        self.create_card(cards_frame, 3, "LOW STOCK ALERTS", str(data['low_stock_count']), warn_color)

        self.render_chart()

    def create_card(self, master, col, title, value, color):
        """Kártya widget generálása a statisztikákhoz."""
        card = ctk.CTkFrame(master, width=220, height=130, corner_radius=15, border_width=2, border_color=color)
        card.grid(row=0, column=col, padx=10, pady=10)
        card.grid_propagate(False)

        ctk.CTkLabel(card, text=title, font=("Arial", 11, "bold"), text_color="gray").pack(pady=(20, 5))
        ctk.CTkLabel(card, text=value, font=("Arial", 22, "bold"), text_color=color).pack(pady=5)

    def render_chart(self):
        """Márka megoszlás grafikon kirajzolása."""
        brands, counts = self.logic.get_chart_data()

        if not brands:
            ctk.CTkLabel(self.main_view, text="No inventory data to display charts.",
                         font=("Arial", 14, "italic")).pack(pady=50)
            return

        fig, ax = plt.subplots(figsize=(8, 4), dpi=100)
        fig.patch.set_facecolor('#242424')
        ax.set_facecolor('#242424')

        colors = ['#3498db', '#2ecc71', '#e67e22', '#9b59b6', '#e74c3c', '#1abc9c']
        ax.bar(brands, counts, color=colors[:len(brands)], alpha=0.8)

        ax.set_title("Stock Levels by Brand", color="white", fontsize=14, pad=15)
        ax.tick_params(axis='both', colors='white', labelsize=9)

        for spine in ax.spines.values():
            spine.set_visible(False)
        ax.grid(axis='y', linestyle='--', alpha=0.2)

        plt.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.main_view)
        canvas.draw()
        canvas.get_tk_widget().pack(pady=30, fill="both", expand=True, padx=40)

    # --- 2. KÉSZLET LISTA ---
    def show_inventory(self):
        self.clear_view()
        ctk.CTkLabel(self.main_view, text="Detailed Inventory Status", font=("Arial", 26, "bold")).pack(pady=20,
                                                                                                        padx=30,
                                                                                                        anchor="w")

        table_frame = ctk.CTkScrollableFrame(self.main_view, fg_color="#1a1a1a", corner_radius=15)
        table_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Táblázat fejlécek
        headers = ["BRAND", "MODEL", "STORAGE", "STOCK", "MIN", "PROFIT", "LAST UPDATE"]
        for i, h in enumerate(headers):
            ctk.CTkLabel(table_frame, text=h, font=("Arial", 11, "bold"), text_color="#3498db").grid(row=0, column=i,
                                                                                                     padx=20, pady=15)

        # Adatsorok generálása
        for idx, p in enumerate(self.logic.get_all_products(), start=1):
            stock_color = "#e74c3c" if p['stock'] <= p['min_stock'] else "#ffffff"
            profit = p['sold_count'] * (p['sale_price'] - p['purchase_price'])

            ctk.CTkLabel(table_frame, text=p['brand'], font=("Arial", 12, "bold")).grid(row=idx, column=0, padx=20,
                                                                                        pady=10)
            ctk.CTkLabel(table_frame, text=p['model']).grid(row=idx, column=1, padx=20)
            ctk.CTkLabel(table_frame, text=p['storage']).grid(row=idx, column=2, padx=20)
            ctk.CTkLabel(table_frame, text=str(p['stock']), text_color=stock_color, font=("Arial", 14, "bold")).grid(
                row=idx, column=3, padx=20)
            ctk.CTkLabel(table_frame, text=f"({p['min_stock']})", text_color="gray").grid(row=idx, column=4, padx=10)
            ctk.CTkLabel(table_frame, text=f"{profit:,} Ft", text_color="#2ecc71", font=("Arial", 12, "bold")).grid(
                row=idx, column=5, padx=20)
            ctk.CTkLabel(table_frame, text=p.get('last_update', '-'), font=("Arial", 10), text_color="gray").grid(
                row=idx, column=6, padx=20)

    # --- 3. ÚJ TERMÉK HOZZÁADÁSA ---
    def show_add_product(self):
        self.clear_view()
        ctk.CTkLabel(self.main_view, text="Add New Device", font=("Arial", 26, "bold")).pack(pady=20, padx=30,
                                                                                             anchor="w")

        form_container = ctk.CTkFrame(self.main_view, fg_color="transparent")
        form_container.pack(pady=10)

        # Beviteli mezők definiálása
        fields = [
            ("Brand (e.g. APPLE)", "brand"), ("Model Name", "model"),
            ("Storage", "storage"), ("Color", "color"),
            ("Purchase Price (Ft)", "p_price"), ("Sale Price (Ft)", "s_price"),
            ("Stock Quantity", "stock"), ("Min. Stock Warning", "min_stock")
        ]

        self.inputs = {}
        for i, (label_text, key) in enumerate(fields):
            row, col = divmod(i, 2)
            ctk.CTkLabel(form_container, text=label_text, font=("Arial", 12)).grid(row=row * 2, column=col, padx=25,
                                                                                   pady=(15, 0), sticky="w")
            entry = ctk.CTkEntry(form_container, width=300, height=40, corner_radius=8)
            entry.grid(row=row * 2 + 1, column=col, padx=25, pady=(5, 10))
            self.inputs[key] = entry

        def handle_save():
            try:
                self.logic.add_product(
                    self.inputs['brand'].get(), self.inputs['model'].get(),
                    self.inputs['storage'].get(), self.inputs['color'].get(),
                    self.inputs['p_price'].get(), self.inputs['s_price'].get(),
                    self.inputs['stock'].get(), self.inputs['min_stock'].get()
                )
                messagebox.showinfo("Success", "Product successfully added.")
                self.show_inventory()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save. Check numerical values! {e}")

        ctk.CTkButton(self.main_view, text="SAVE PRODUCT", fg_color="#2ecc71", hover_color="#27ae60",
                      height=50, width=350, font=("Arial", 16, "bold"), command=handle_save).pack(pady=50)

    # --- 4. KÉSZLET KEZELÉS (BESZERZÉS/ELADÁS) ---
    def show_stock_update(self):
        self.clear_view()
        ctk.CTkLabel(self.main_view, text="Inventory Transaction", font=("Arial", 26, "bold")).pack(pady=20, padx=30,
                                                                                                    anchor="w")

        prods = self.logic.get_all_products()
        options = [f"{p['id']} | {p['brand']} {p['model']} ({p['storage']})" for p in prods]

        if not options:
            ctk.CTkLabel(self.main_view, text="No items found. Please add a product first.").pack(pady=40)
            return

        ctk.CTkLabel(self.main_view, text="Select Device:", font=("Arial", 12)).pack(pady=(20, 5))
        combo = ctk.CTkComboBox(self.main_view, values=options, width=450, height=45)
        combo.pack(pady=5)

        ctk.CTkLabel(self.main_view, text="Transaction Quantity:", font=("Arial", 12)).pack(pady=(20, 5))
        amount_ent = ctk.CTkEntry(self.main_view, placeholder_text="Enter quantity...", width=200, height=45,
                                  font=("Arial", 16))
        amount_ent.pack(pady=5)

        def do_update(is_sell):
            try:
                p_id = int(combo.get().split(" | ")[0])
                qty = int(amount_ent.get())
                if is_sell: qty = -abs(qty)

                success, msg = self.logic.update_stock(p_id, qty)
                if success:
                    messagebox.showinfo("Success", msg)
                    self.show_dashboard()
                else:
                    messagebox.showerror("Denied", msg)
            except:
                messagebox.showerror("Error", "Check the quantity format!")

        # Műveleti gombok
        btn_box = ctk.CTkFrame(self.main_view, fg_color="transparent")
        btn_box.pack(pady=40)
        ctk.CTkButton(btn_box, text="📥 RESTOCK (+)", fg_color="#3498db", width=200, height=55,
                      font=("Arial", 14, "bold"),
                      command=lambda: do_update(False)).grid(row=0, column=0, padx=20)
        ctk.CTkButton(btn_box, text="💸 SELL ITEM (-)", fg_color="#e67e22", width=200, height=55,
                      font=("Arial", 14, "bold"),
                      command=lambda: do_update(True)).grid(row=0, column=1, padx=20)


if __name__ == "__main__":
    app = MobiStockV15()
    app.mainloop()