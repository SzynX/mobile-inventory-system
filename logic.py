import data_manager

class InventoryLogic:
    def __init__(self):
        self.products = data_manager.load_data()

    def get_all_products(self):
        return self.products

    def add_product(self, model, storage, color, price, stock):
        new_id = max([p['id'] for p in self.products], default=0) + 1
        product = {
            "id": new_id,
            "model": model,
            "storage": storage,
            "color": color,
            "price": int(price),
            "stock": int(stock)
        }
        self.products.append(product)
        data_manager.save_data(self.products)
        return True

    def update_stock(self, product_id, amount):
        for p in self.products:
            if p['id'] == product_id:
                new_stock = p['stock'] + amount
                if new_stock < 0:
                    return False, "Nincs elég készleten!"
                p['stock'] = new_stock
                data_manager.save_data(self.products)
                return True, "Sikeres frissítés!"
        return False, "Termék nem található!"

    def get_stats(self):
        total_types = len(self.products)
        total_items = sum(p['stock'] for p in self.products)
        return total_types, total_items