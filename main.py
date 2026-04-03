import customtkinter as ctk
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from logic import InventoryLogic

# Megjelenési beállítások (Modern Sötét Téma)
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class MobiStockV2(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Logikai példányosítás
        self.logic = InventoryLogic()

        # Ablak konfiguráció
        self.title("MobiStock v2.0 - Enterprise Edition")
        self.geometry("1280x850")

        # Színpaletta definíció (Enterprise Design)
        self.color_bg = "#121212"
        self.color_sidebar = "#1e1e1e"
        self.color_primary = "#3b8ed0"
        self.color_success = "#2fa572"
        self.color_danger = "#d3514d"
        self.color_warning = "#f39c12"

        # Rács elrendezés
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- OLDALSÁV (SIDEBAR) ---
        self.sidebar = ctk.CTkFrame(self, width=280, corner_radius=0, fg_color=self.color_sidebar)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        # Logo
        ctk.CTkLabel(self.sidebar, text="MOBI", font=("Impact", 40), text_color=self.color_primary).pack(pady=(40, 0))
        ctk.CTkLabel(self.sidebar, text="STOCK v2.0", font=("Arial", 12, "bold"), text_color="white").pack(pady=(0, 40))

        # Menüpontok
        menu_items = [
            ("📊 Dashboard", self.show_dashboard),
            ("📦 Inventory", self.show_inventory),
            ("📜 History Log", self.show_history),
            ("➕ New Product", self.show_add_product),
            ("🔄 Transactions", self.show_stock_update)
        ]

        for text, command in menu_items:
            btn = ctk.CTkButton(self.sidebar, text=text, command=command,
                                height=50, corner_radius=12,
                                font=("Arial", 14, "bold"),
                                fg_color="transparent", hover_color="#333333",
                                anchor="w")
            btn.pack(pady=5, padx=20, fill="x")

        # --- FŐ NÉZET (MAIN VIEW) ---
        self.main_view = ctk.CTkFrame(self, corner_radius=25, fg_color=self.color_bg)
        self.main_view.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        # Alapértelmezett oldal: Dashboard
        self.show_dashboard()

    def clear_view(self):
        """Minden widget törlése a fő nézetből."""
        for widget in self.main_view.winfo_children():
            widget.destroy()

    # --- 1. DASHBOARD (ÜZLETI INTELLIGENCIA) ---
    def show_dashboard(self):
        self.clear_view()
        data = self.logic.get_financials()

        ctk.CTkLabel(self.main_view, text="Business Intelligence", font=("Arial", 32, "bold")).pack(pady=30, padx=40,
                                                                                                    anchor="w")

        # Kártyák konténere
        cards_frame = ctk.CTkFrame(self.main_view, fg_color="transparent")
        cards_frame.pack(fill="x", padx=40)

        self.create_card(cards_frame, 0, "TOTAL REVENUE", f"{data['revenue']:,} Ft", self.color_primary)
        self.create_card(cards_frame, 1, "NET PROFIT", f"{data['profit']:,} Ft", self.color_success)
        self.create_card(cards_frame, 2, "AVG MARGIN", f"{data['margin']}%", self.color_warning)
        self.create_card(cards_frame, 3, "LOW STOCK", str(data['low_stock_count']), self.color_danger)

        self.render_chart()

    def create_card(self, master, col, title, value, color):
        card = ctk.CTkFrame(master, width=240, height=130, corner_radius=20, border_width=1, border_color="#333")
        card.grid(row=0, column=col, padx=10)
        card.grid_propagate(False)

        ctk.CTkLabel(card, text=title, font=("Arial", 12), text_color="gray").pack(pady=(25, 5))
        ctk.CTkLabel(card, text=value, font=("Arial", 26, "bold"), text_color=color).pack()

    def render_chart(self):
        brands, counts = self.logic.get_chart_data()
        if not brands:
            ctk.CTkLabel(self.main_view, text="No data for charts.", font=("Arial", 14, "italic")).pack(pady=50)
            return

        fig, ax = plt.subplots(figsize=(9, 4), dpi=100)
        fig.patch.set_facecolor(self.color_bg)
        ax.set_facecolor(self.color_bg)

        ax.bar(brands, counts, color=self.color_primary, alpha=0.8)
        ax.set_title("Inventory Distribution by Brand", color="white", fontsize=14, pad=20)
        ax.tick_params(colors='white', labelsize=9)

        for spine in ax.spines.values():
            spine.set_visible(False)
        ax.grid(axis='y', linestyle='--', alpha=0.1)

        plt.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=self.main_view)
        canvas.draw()
        canvas.get_tk_widget().pack(pady=40, fill="both", expand=True, padx=40)

    # --- 2. INVENTORY (KERESÉS ÉS SZŰRÉS) ---
    def show_inventory(self, query="", low_only=False):
        self.clear_view()
        ctk.CTkLabel(self.main_view, text="Inventory Analytics", font=("Arial", 28, "bold")).pack(pady=(20, 10),
                                                                                                  padx=40, anchor="w")

        # Kereső sáv
        search_frame = ctk.CTkFrame(self.main_view, fg_color="transparent")
        search_frame.pack(fill="x", padx=40, pady=10)

        search_entry = ctk.CTkEntry(search_frame, placeholder_text="Search model or brand...", width=400, height=40)
        search_entry.pack(side="left", padx=(0, 10))
        if query: search_entry.insert(0, query)

        low_stock_var = ctk.BooleanVar(value=low_only)

        def refresh():
            self.show_inventory(search_entry.get(), low_stock_var.get())

        ctk.CTkButton(search_frame, text="Search", width=100, command=refresh).pack(side="left")
        ctk.CTkCheckBox(search_frame, text="Critical Stock Only", variable=low_stock_var, command=refresh).pack(
            side="left", padx=20)

        # Táblázat
        scroll = ctk.CTkScrollableFrame(self.main_view, fg_color="#181818", corner_radius=20)
        scroll.pack(fill="both", expand=True, padx=40, pady=20)

        headers = ["BRAND", "MODEL", "STOCK", "STATUS", "PURCHASE", "SALE", "MARGIN"]
        for i, h in enumerate(headers):
            ctk.CTkLabel(scroll, text=h, font=("Arial", 11, "bold"), text_color=self.color_primary).grid(row=0,
                                                                                                         column=i,
                                                                                                         padx=20,
                                                                                                         pady=15)

        products = self.logic.get_filtered_products(query, low_only)
        for idx, p in enumerate(products, start=1):
            margin = round(((p['sale_price'] - p['purchase_price']) / p['sale_price'] * 100), 1) if p[
                                                                                                        'sale_price'] > 0 else 0
            status = "OK" if p['stock'] > p['min_stock'] else "LOW"
            status_color = self.color_success if status == "OK" else self.color_danger

            ctk.CTkLabel(scroll, text=p['brand'], font=("Arial", 12, "bold")).grid(row=idx, column=0, padx=20, pady=10)
            ctk.CTkLabel(scroll, text=p['model']).grid(row=idx, column=1, padx=20)
            ctk.CTkLabel(scroll, text=str(p['stock']), font=("Arial", 13, "bold")).grid(row=idx, column=2, padx=20)
            ctk.CTkLabel(scroll, text=status, text_color=status_color, font=("Arial", 11, "bold")).grid(row=idx,
                                                                                                        column=3,
                                                                                                        padx=20)
            ctk.CTkLabel(scroll, text=f"{p['purchase_price']:,}").grid(row=idx, column=4, padx=20)
            ctk.CTkLabel(scroll, text=f"{p['sale_price']:,}").grid(row=idx, column=5, padx=20)
            ctk.CTkLabel(scroll, text=f"{margin}%", text_color=self.color_warning).grid(row=idx, column=6, padx=20)

    # --- 3. HISTORY LOG (ESEMÉNYNAPLÓ) ---
    def show_history(self):
        self.clear_view()
        ctk.CTkLabel(self.main_view, text="Transaction History Log", font=("Arial", 28, "bold")).pack(pady=20, padx=40,
                                                                                                      anchor="w")

        scroll = ctk.CTkScrollableFrame(self.main_view, fg_color="#181818", corner_radius=20)
        scroll.pack(fill="both", expand=True, padx=40, pady=20)

        for h in self.logic.history:
            color = self.color_success if h['value'] >= 0 else self.color_danger
            line = ctk.CTkFrame(scroll, fg_color="transparent")
            line.pack(fill="x", pady=8, padx=15)

            ctk.CTkLabel(line, text=h['timestamp'], font=("Consolas", 12), text_color="gray").pack(side="left", padx=10)
            ctk.CTkLabel(line, text=h['description'], font=("Arial", 13, "bold"), width=450, anchor="w").pack(
                side="left", padx=10)

            # Pénzáramlás kijelzése
            prefix = "+" if h['value'] > 0 else ""
            ctk.CTkLabel(line, text=f"{prefix}{h['value']:,} Ft", font=("Arial", 13, "bold"),
                         text_color=color, width=150, anchor="e").pack(side="right", padx=20)

    # --- 4. NEW PRODUCT (MODERN FORM) ---
    def show_add_product(self):
        self.clear_view()
        ctk.CTkLabel(self.main_view, text="Enterprise Asset Integration", font=("Arial", 28, "bold")).pack(pady=30,
                                                                                                           padx=40,
                                                                                                           anchor="w")

        form_frame = ctk.CTkFrame(self.main_view, fg_color="#181818", corner_radius=25)
        form_frame.pack(pady=10, padx=40, fill="both", expand=True)

        fields = [
            ("Brand (e.g. APPLE)", "brand"), ("Model Name", "model"),
            ("Storage Capacity", "storage"), ("Color Variant", "color"),
            ("Purchase Price (Ft)", "p_price"), ("Sale Price (Ft)", "s_price"),
            ("Initial Stock", "stock"), ("Min. Stock Limit", "min_stock")
        ]

        self.inputs = {}
        # Belső rács a formhoz
        inner_form = ctk.CTkFrame(form_frame, fg_color="transparent")
        inner_form.pack(pady=40)

        for i, (label, key) in enumerate(fields):
            row, col = divmod(i, 2)
            ctk.CTkLabel(inner_form, text=label, font=("Arial", 12, "bold")).grid(row=row * 2, column=col, padx=30,
                                                                                  pady=(15, 0), sticky="w")
            entry = ctk.CTkEntry(inner_form, width=320, height=40, corner_radius=10)
            entry.grid(row=row * 2 + 1, column=col, padx=30, pady=(5, 10))
            self.inputs[key] = entry

        def save():
            try:
                self.logic.add_product(
                    self.inputs['brand'].get(), self.inputs['model'].get(),
                    self.inputs['storage'].get(), self.inputs['color'].get(),
                    self.inputs['p_price'].get(), self.inputs['s_price'].get(),
                    self.inputs['stock'].get(), self.inputs['min_stock'].get()
                )
                messagebox.showinfo("Success", "Asset integrated and logged in history.")
                self.show_inventory()
            except:
                messagebox.showerror("Error", "Numerical validation failed. Check prices/stock.")

        ctk.CTkButton(self.main_view, text="ADD PRODUCT TO DATABASE", fg_color=self.color_success,
                      hover_color="#27ae60", height=55, width=400, font=("Arial", 16, "bold"),
                      command=save).pack(pady=40)

    # --- 5. TRANSACTIONS (TERMINÁL) ---
    def show_stock_update(self):
        self.clear_view()
        ctk.CTkLabel(self.main_view, text="Transaction Terminal", font=("Arial", 28, "bold")).pack(pady=30, padx=40,
                                                                                                   anchor="w")

        prods = self.logic.products
        options = [f"{p['id']} | {p['brand']} {p['model']}" for p in prods]

        if not options:
            ctk.CTkLabel(self.main_view, text="Empty database. Add products first.").pack(pady=50)
            return

        terminal = ctk.CTkFrame(self.main_view, fg_color="#181818", corner_radius=25, width=600, height=400)
        terminal.pack(pady=20)
        terminal.pack_propagate(False)

        ctk.CTkLabel(terminal, text="Select Target Asset:", font=("Arial", 13)).pack(pady=(40, 5))
        combo = ctk.CTkComboBox(terminal, values=options, width=450, height=45, corner_radius=10)
        combo.pack(pady=10)

        ctk.CTkLabel(terminal, text="Transaction Quantity:", font=("Arial", 13)).pack(pady=(20, 5))
        amt_entry = ctk.CTkEntry(terminal, placeholder_text="Enter qty...", width=200, height=45, font=("Arial", 16),
                                 justify="center")
        amt_entry.pack(pady=10)

        def execute(is_sell):
            try:
                p_id = int(combo.get().split(" | ")[0])
                qty = int(amt_entry.get())
                if is_sell: qty = -abs(qty)

                success, msg = self.logic.update_stock(p_id, qty)
                if success:
                    self.show_history()
                else:
                    messagebox.showerror("Transaction Denied", msg)
            except:
                messagebox.showerror("Error", "Invalid quantity format.")

        btn_f = ctk.CTkFrame(terminal, fg_color="transparent")
        btn_f.pack(pady=40)

        ctk.CTkButton(btn_f, text="RESTOCK (+)", fg_color=self.color_primary, width=180, height=50,
                      font=("Arial", 14, "bold"), command=lambda: execute(False)).grid(row=0, column=0, padx=15)

        ctk.CTkButton(btn_f, text="EXECUTE SALE (-)", fg_color=self.color_danger, width=180, height=50,
                      font=("Arial", 14, "bold"), command=lambda: execute(True)).grid(row=0, column=1, padx=15)


if __name__ == "__main__":
    app = MobiStockV2()
    app.mainloop()