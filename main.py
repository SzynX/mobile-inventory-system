import customtkinter as ctk
from tkinter import messagebox
from logic import InventoryLogic

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class PhoneApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.logic = InventoryLogic()
        self.title("Telefon Készletkezelő v1.0")
        self.geometry("900x600")

        # Grid elrendezés (Sidebar + Tartalom)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- SIDEBAR ---
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        self.logo_label = ctk.CTkLabel(self.sidebar, text="MOBIL-KÉSZLET", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.pack(pady=20, padx=10)

        self.btn_dash = ctk.CTkButton(self.sidebar, text="Irányítópult", command=self.show_dashboard)
        self.btn_dash.pack(pady=10, padx=20)

        self.btn_list = ctk.CTkButton(self.sidebar, text="Készlet Lista", command=self.show_inventory)
        self.btn_list.pack(pady=10, padx=20)

        self.btn_add = ctk.CTkButton(self.sidebar, text="Új Termék", command=self.show_add_product)
        self.btn_add.pack(pady=10, padx=20)

        self.btn_stock = ctk.CTkButton(self.sidebar, text="Beszerzés/Eladás", command=self.show_stock_update)
        self.btn_stock.pack(pady=10, padx=20)

        # --- MAIN CONTENT AREA ---
        self.main_view = ctk.CTkFrame(self, corner_radius=15, fg_color="transparent")
        self.main_view.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        self.show_dashboard()

    def clear_view(self):
        for widget in self.main_view.winfo_children():
            widget.destroy()

    # --- VIEWS ---
    def show_dashboard(self):
        self.clear_view()
        types, items = self.logic.get_stats()

        title = ctk.CTkLabel(self.main_view, text="Irányítópult", font=("Arial", 24, "bold"))
        title.pack(pady=20)

        stat_frame = ctk.CTkFrame(self.main_view)
        stat_frame.pack(pady=10, padx=20, fill="x")

        ctk.CTkLabel(stat_frame, text=f"Különböző modellek: {types}", font=("Arial", 18)).pack(pady=10)
        ctk.CTkLabel(stat_frame, text=f"Összes készlet: {items} db", font=("Arial", 18)).pack(pady=10)

    def show_inventory(self):
        self.clear_view()
        ctk.CTkLabel(self.main_view, text="Aktuális Készlet", font=("Arial", 24, "bold")).pack(pady=10)

        scroll_frame = ctk.CTkScrollableFrame(self.main_view, width=600, height=400)
        scroll_frame.pack(pady=10, padx=10, fill="both", expand=True)

        # Fejléc
        header = ["ID", "Modell", "Tárhely", "Szín", "Ár", "Készlet"]
        for i, h in enumerate(header):
            lbl = ctk.CTkLabel(scroll_frame, text=h, font=("Arial", 12, "bold"))
            lbl.grid(row=0, column=i, padx=10, pady=5, sticky="w")

        # Termékek listázása
        for row_idx, p in enumerate(self.logic.get_all_products(), start=1):
            ctk.CTkLabel(scroll_frame, text=p['id']).grid(row=row_idx, column=0, padx=10, pady=2)
            ctk.CTkLabel(scroll_frame, text=p['model']).grid(row=row_idx, column=1, padx=10, pady=2)
            ctk.CTkLabel(scroll_frame, text=p['storage']).grid(row=row_idx, column=2, padx=10, pady=2)
            ctk.CTkLabel(scroll_frame, text=p['color']).grid(row=row_idx, column=3, padx=10, pady=2)
            ctk.CTkLabel(scroll_frame, text=f"{p['price']} Ft").grid(row=row_idx, column=4, padx=10, pady=2)
            ctk.CTkLabel(scroll_frame, text=f"{p['stock']} db", text_color="#1fbbff").grid(row=row_idx, column=5,
                                                                                           padx=10, pady=2)

    def show_add_product(self):
        self.clear_view()
        ctk.CTkLabel(self.main_view, text="Új Termék Hozzáadása", font=("Arial", 24, "bold")).pack(pady=20)

        model_ent = ctk.CTkEntry(self.main_view, placeholder_text="Modell (pl. iPhone 14)")
        model_ent.pack(pady=5)
        storage_ent = ctk.CTkEntry(self.main_view, placeholder_text="Tárhely (pl. 256GB)")
        storage_ent.pack(pady=5)
        color_ent = ctk.CTkEntry(self.main_view, placeholder_text="Szín")
        color_ent.pack(pady=5)
        price_ent = ctk.CTkEntry(self.main_view, placeholder_text="Ár (Ft)")
        price_ent.pack(pady=5)
        stock_ent = ctk.CTkEntry(self.main_view, placeholder_text="Kezdő készlet")
        stock_ent.pack(pady=5)

        def save():
            try:
                self.logic.add_product(model_ent.get(), storage_ent.get(), color_ent.get(), price_ent.get(),
                                       stock_ent.get())
                messagebox.showinfo("Siker", "Termék mentve!")
                self.show_inventory()
            except ValueError:
                messagebox.showerror("Hiba", "Kérlek érvényes számokat adj meg az árnál és készletnél!")

        ctk.CTkButton(self.main_view, text="Mentés", fg_color="green", hover_color="#006400", command=save).pack(
            pady=20)

    def show_stock_update(self):
        self.clear_view()
        ctk.CTkLabel(self.main_view, text="Készlet Módosítása", font=("Arial", 24, "bold")).pack(pady=20)

        # Termék választó (ID alapján egyszerűség kedvéért)
        products = self.logic.get_all_products()
        options = [f"{p['id']} - {p['model']} ({p['storage']})" for p in products]

        if not options:
            ctk.CTkLabel(self.main_view, text="Nincs rögzített termék!").pack()
            return

        combo = ctk.CTkComboBox(self.main_view, values=options, width=300)
        combo.pack(pady=10)

        amount_ent = ctk.CTkEntry(self.main_view, placeholder_text="Mennyiség (eladáshoz negatív szám)")
        amount_ent.pack(pady=10)

        def update(mode):
            try:
                p_id = int(combo.get().split(" - ")[0])
                val = int(amount_ent.get())
                if mode == "sell":
                    val = -abs(val)
                else:
                    val = abs(val)

                success, msg = self.logic.update_stock(p_id, val)
                if success:
                    messagebox.showinfo("Info", msg)
                    self.show_inventory()
                else:
                    messagebox.showerror("Hiba", msg)
            except:
                messagebox.showerror("Hiba", "Hibás adatbevitel!")

        btn_frame = ctk.CTkFrame(self.main_view, fg_color="transparent")
        btn_frame.pack(pady=10)

        ctk.CTkButton(btn_frame, text="📥 Beszerzés (+)", command=lambda: update("buy"), fg_color="blue").grid(row=0,
                                                                                                              column=0,
                                                                                                              padx=10)
        ctk.CTkButton(btn_frame, text="💸 Eladás (-)", command=lambda: update("sell"), fg_color="red").grid(row=0,
                                                                                                           column=1,
                                                                                                           padx=10)


if __name__ == "__main__":
    app = PhoneApp()
    app.mainloop()