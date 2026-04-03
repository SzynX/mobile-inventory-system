import data_manager
from datetime import datetime


class InventoryLogic:
    def __init__(self):
        """Inicializálás és az adatok betöltése/migrálása."""
        self.products = data_manager.load_data()
        self._migrate_data()

    def _migrate_data(self):
        """
        Biztosítja a kompatibilitást a régebbi (1.0, 1.2) verziókkal.
        Ha hiányoznak az 1.5-ös verzió mezői, alapértelmezett értékekkel pótolja őket.
        """
        updated = False
        for p in self.products:
            # 1.5 Új mező: Márka (Brand)
            if 'brand' not in p:
                p['brand'] = "OTHER"
                updated = True

            # 1.5 Új mező: Minimum készlet figyelmeztetéshez
            if 'min_stock' not in p:
                p['min_stock'] = 2
                updated = True

            # 1.5 Új mező: Utolsó módosítás időpontja
            if 'last_update' not in p:
                p['last_update'] = datetime.now().strftime("%Y-%m-%d %H:%M")
                updated = True

            # 1.2-es mezők ellenőrzése (ha 1.0-ról frissít valaki)
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

    def get_all_products(self):
        """Visszaadja a teljes terméklistát."""
        return self.products

    def add_product(self, brand, model, storage, color, purchase_price, sale_price, stock, min_stock):
        """
        Új termék rögzítése minden adattal.
        A márkaneveket automatikusan nagybetűssé alakítja a rendszerezés miatt.
        """
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
            "sold_count": 0,
            "last_update": datetime.now().strftime("%Y-%m-%d %H:%M")
        }

        self.products.append(product)
        data_manager.save_data(self.products)
        return True

    def update_stock(self, product_id, amount):
        """
        Készlet módosítása (beszerzés/eladás).
        Automatikusan frissíti az utolsó módosítás dátumát.
        """
        for p in self.products:
            if p['id'] == product_id:
                if amount < 0:  # ELADÁS
                    sold_qty = abs(amount)
                    if p['stock'] < sold_qty:
                        return False, "Hiba: Nincs elegendő készlet!"
                    p['stock'] -= sold_qty
                    p['sold_count'] += sold_qty
                else:  # BESZERZÉS
                    p['stock'] += amount

                # Időbélyeg frissítése
                p['last_update'] = datetime.now().strftime("%Y-%m-%d %H:%M")

                data_manager.save_data(self.products)
                return True, "Készlet sikeresen frissítve!"

        return False, "Hiba: Termék nem található!"

    def get_financials(self):
        """
        Összetett pénzügyi és készlet statisztikák számítása.
        Visszaadja a bevételt, profitot, készletértéket és a kritikus készletszintet.
        """
        total_revenue = 0
        total_cost = 0
        total_inventory_value = 0
        total_items_in_stock = 0
        low_stock_alerts = 0

        for p in self.products:
            # Pénzügyek
            total_revenue += p['sold_count'] * p['sale_price']
            total_cost += p['sold_count'] * p['purchase_price']

            # Raktár állapot
            total_inventory_value += p['stock'] * p['purchase_price']
            total_items_in_stock += p['stock']

            # Figyelmeztetés, ha a készlet eléri vagy alulmúlja a minimumot
            if p['stock'] <= p['min_stock']:
                low_stock_alerts += 1

        return {
            "revenue": total_revenue,
            "profit": total_revenue - total_cost,
            "inv_value": total_inventory_value,
            "total_items": total_items_in_stock,
            "low_stock_count": low_stock_alerts
        }

    def get_chart_data(self):
        """
        Adat-előkészítés a Dashboard grafikonjához.
        Márkák szerint összesíti a raktárkészletet.
        """
        brand_stats = {}
        for p in self.products:
            brand = p['brand']
            brand_stats[brand] = brand_stats.get(brand, 0) + p['stock']

        # Ha üres a lista, ne legyen hiba
        if not brand_stats:
            return [], []

        return list(brand_stats.keys()), list(brand_stats.values())