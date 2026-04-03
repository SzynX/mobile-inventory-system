import data_manager
from datetime import datetime


class InventoryLogic:
    def __init__(self):
        """Inicializálja a készletet és a tranzakciós előzményeket."""
        self.products = data_manager.load_data()
        self.history = data_manager.load_history()
        # Automatikus frissítés a 2.0-ás adatmodellre
        self._migrate_2_0()

    def _migrate_2_0(self):
        """Biztosítja, hogy minden termék rendelkezzen a 2.0-ás verzióhoz szükséges mezőkkel."""
        updated = False
        for p in self.products:
            if 'brand' not in p:
                p['brand'] = "OTHER"
                updated = True
            if 'min_stock' not in p:
                p['min_stock'] = 2
                updated = True
            if 'sold_count' not in p:
                p['sold_count'] = 0
                updated = True
            if 'purchase_price' not in p:
                p['purchase_price'] = p.get('price', 0)
                updated = True
            if 'sale_price' not in p:
                p['sale_price'] = p.get('price', 0)
                updated = True

        if updated:
            data_manager.save_data(self.products)

    def _log_transaction(self, p_id, description, quantity, money_flow):
        """
        Belső naplózó rendszer.
        Minden eseményt elment a history.json-ba időbélyeggel.
        money_flow: pozitív ha bevétel (eladás), negatív ha költség (beszerzés).
        """
        log_entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "product_id": p_id,
            "description": description,
            "quantity": quantity,
            "value": int(money_flow)
        }
        # Új bejegyzés az elejére (hogy a legfrissebb legyen legfelül)
        self.history.insert(0, log_entry)

        # Limitáljuk az előzményeket az utolsó 200 műveletre a sebesség miatt
        data_manager.save_history(self.history[:200])

    def add_product(self, brand, model, storage, color, purchase_price, sale_price, stock, min_stock):
        """Új termék rögzítése és a kezdeti készlet naplózása."""
        new_id = max([p['id'] for p in self.products], default=0) + 1

        product = {
            "id": new_id,
            "brand": brand.strip().upper(),
            "model": model.strip(),
            "storage": storage.strip(),
            "color": color.strip(),
            "purchase_price": int(purchase_price),
            "sale_price": int(sale_price),
            "stock": int(stock),
            "min_stock": int(min_stock),
            "sold_count": 0
        }

        self.products.append(product)
        data_manager.save_data(self.products)

        # Kezdeti készlet naplózása (mint egy beszerzés, de 0 költséggel jelölve az indulásnál)
        self._log_transaction(new_id, f"INITIAL STOCK: {brand} {model}", int(stock), 0)
        return True

    def update_stock(self, product_id, amount):
        """
        Készletmódosítás (Beszerzés vagy Eladás).
        Kiszámolja a pénzügyi hatást és naplózza a tranzakciót.
        """
        for p in self.products:
            if p['id'] == product_id:
                if amount < 0:  # ELADÁS
                    sold_qty = abs(amount)
                    if p['stock'] < sold_qty:
                        return False, "Hiba: Nincs elég készleten!"

                    p['stock'] -= sold_qty
                    p['sold_count'] += sold_qty
                    # Bevétel kiszámítása (pozitív érték)
                    money_impact = sold_qty * p['sale_price']
                    desc = f"SALE: {p['brand']} {p['model']} (x{sold_qty})"

                else:  # BESZERZÉS
                    p['stock'] += amount
                    # Költség kiszámítása (negatív érték a naplóban)
                    money_impact = -(amount * p['purchase_price'])
                    desc = f"RESTOCK: {p['brand']} {p['model']} (x{amount})"

                # Mentés és naplózás
                self._log_transaction(p['id'], desc, amount, money_impact)
                data_manager.save_data(self.products)
                return True, "Tranzakció sikeresen rögzítve!"

        return False, "Hiba: A termék nem található!"

    def get_filtered_products(self, query="", low_stock_only=False):
        """Keresés és szűrés a termékek között (márka vagy modell alapján)."""
        results = self.products

        if low_stock_only:
            results = [p for p in results if p['stock'] <= p['min_stock']]

        if query:
            q = query.lower()
            results = [p for p in results if q in p['model'].lower() or q in p['brand'].lower()]

        return results

    def get_financials(self):
        """Vállalati szintű pénzügyi elemzés (Bevétel, Profit, Profitráta, Készletérték)."""
        total_revenue = sum(p['sold_count'] * p['sale_price'] for p in self.products)
        total_cost = sum(p['sold_count'] * p['purchase_price'] for p in self.products)
        inventory_value = sum(p['stock'] * p['purchase_price'] for p in self.products)

        profit = total_revenue - total_cost
        # Profitráta (Margin %) számítása
        margin = (profit / total_revenue * 100) if total_revenue > 0 else 0

        return {
            "revenue": total_revenue,
            "profit": profit,
            "margin": round(margin, 1),
            "inv_value": inventory_value,
            "low_stock_count": sum(1 for p in self.products if p['stock'] <= p['min_stock'])
        }

    def get_chart_data(self):
        """Márkák szerinti készletmegoszlás a grafikonhoz."""
        brand_stats = {}
        for p in self.products:
            brand = p['brand']
            brand_stats[brand] = brand_stats.get(brand, 0) + p['stock']

        return list(brand_stats.keys()), list(brand_stats.values())