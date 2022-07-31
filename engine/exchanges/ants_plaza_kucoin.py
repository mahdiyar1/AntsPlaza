from ccxt import kucoin


class AntsPlazakucoin(kucoin):

    def fetch_margin_balance(self):
        return self.private_get_margin_account()

    def fetch_borrow_order(self, order_id):
        return self.private_get_margin_borrow({'orderId': order_id})
