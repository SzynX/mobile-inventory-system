import data_manager


class InventoryLogic:
    def __init__(self):
        """Inicializálás: adatok betöltése a JSON fájlból."""
        self.products = data_manager.load_data()

    def get_all_products(self):
        """Visszaadja az összes terméket."""
        return self.products

    def add_product(self, model, storage, color, purchase_price, sale_price, stock):
        """
        Új termék rögzítése a rendszerbe.
        purchase_price: Beszerzési ár (mennyiért vettük)
        sale_price: Eladási ár (mennyiért adjuk)
        sold_count: Kezdetben 0, ez tárolja az eladott darabszámot a profit számításhoz.
        """
        new_id = max([p['id'] for p in self.products], default=0) + 1

        product = {
            "id": new_id,
            "model": model,
            "storage": storage,
            "color": color,
            "purchase_price": int(purchase_price),
            "sale_price": int(sale_price),
            "stock": int(stock),
            "sold_count": 0  # Statisztikához: eddig eladott mennyiség
        }

        self.products.append(product)
        data_manager.save_data(self.products)
        return True

    def update_stock(self, product_id, amount):
        """
        Készlet módosítása.
        Ha amount > 0: Beszerzés (készlet nő)
        Ha amount < 0: Eladás (készlet csökken, sold_count nő)
        """
        for p in self.products:
            if p['id'] == product_id:
                if amount < 0:  # ELADÁS LOGIKA
                    sold_qty = abs(amount)
                    if p['stock'] < sold_qty:
                        return False, "Hiba: Nincs elég készlet az eladáshoz!"

                    p['stock'] -= sold_qty
                    # Az eladott mennyiséget hozzáadjuk a statisztikához
                    p['sold_count'] += sold_qty
                else:  # BESZERZÉS LOGIKA
                    p['stock'] += amount

                data_manager.save_data(self.products)
                return True, "Készlet sikeresen frissítve!"

        return False, "Hiba: A termék nem található!"

    def get_financials(self):
        """
        Pénzügyi mutatók kiszámítása.
        Revenue (Bevétel): Eladott darab * Eladási ár
        Cost (Költség): Eladott darab * Beszerzési ár
        Profit: Bevétel - Költség
        Inventory Value: Raktáron lévő termékek értéke (beszerzési áron)
        """
        total_revenue = 0
        total_cost_of_sold_items = 0
        total_inventory_value = 0
        total_items_in_stock = 0

        for p in self.products:
            # Bevétel és profit számítás az eladások alapján
            total_revenue += p['sold_count'] * p['sale_price']
            total_cost_of_sold_items += p['sold_count'] * p['purchase_price']

            # Jelenlegi raktárkészlet értéke
            total_inventory_value += p['stock'] * p['purchase_price']
            total_items_in_stock += p['stock']

        total_profit = total_revenue - total_cost_of_sold_items

        return {
            "revenue": total_revenue,
            "profit": total_profit,
            "inventory_value": total_inventory_value,
            "total_items": total_items_in_stock
        }

    def get_model_stats(self):
        """Adatok a grafikonhoz: Modellek nevei, készletei és profitjai."""
        models = []
        stocks = []
        profits = []

        for p in self.products:
            models.append(p['model'])
            stocks.append(p['stock'])
            # Egy adott modell profitja: eladott db * (eladási ár - beszerzési ár)
            model_profit = p['sold_count'] * (p['sale_price'] - p['purchase_price'])
            profits.append(model_profit)

        return models, stocks, profits