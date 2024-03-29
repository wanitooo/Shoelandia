

from ast import Del
from decimal import Decimal
from store.models import Product, ProductImage, SubProduct
from checkout.models import DeliveryOptions
from django.conf import settings


class Basket():
    """
    Initialize a basket class, 
    associate it with the browser session
    """

    def __init__(self, request):
        self.session = request.session
        basket = self.session.get(settings.BASKET_SESSION_ID)
        if settings.BASKET_SESSION_ID not in request.session:
            basket = self.session[settings.BASKET_SESSION_ID] = {}
        self.basket = basket

    def add(self, product, qty, size, variant):
        product_id = str(product.id)
        product_name = str(product.title)
        product_variant = str(variant)
        images = ProductImage.objects.filter(
            sub_product__productcolor__color=product_variant).filter(sub_product__product__title=product_name).values('image')
        image = images[0]

        if product_id in self.basket:
            self.basket[product_id]['qty'] = qty
            self.basket[product_id]['size'] = size
            self.basket[product_id]['variant'] = variant
            self.basket[product_id]['image'] = image['image']
        else:
            self.basket[product_id] = {'price': str(
                product.regular_price), 'qty': qty, 'size': size, 'image': image["image"], 'variant': variant}
        self.save()

    def __iter__(self):
        product_ids = self.basket.keys()
        products = Product.objects.filter(id__in=product_ids)
        basket = self.basket.copy()

        for product in products:
            basket[str(product.id)]['product'] = product

        for item in basket.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['qty']
            yield item

    def __len__(self):
        """
        The oneliner is equivalent to
        sum = 0
        for item in self.basket.values():
            sum += item['qty']
        retun sum

        Returns:
            This returns the number of items in a basket
        """
        return sum(item['qty'] for item in self.basket.values())

    def get_subtotal(self):
        subtotal = sum(Decimal(item['price']) * item['qty']
                       for item in self.basket.values())
        return subtotal

    def get_total_price(self):
        total = self.get_subtotal()
        newprice = 0.00
        if "purchase" in self.session:
            newprice = DeliveryOptions.objects.get(
                id=self.session["purchase"]["delivery_id"]).delivery_price
        total += Decimal(newprice)
        return total

    def get_delivery_price(self):
        price = 0.00
        if "purchase" in self.session:
            price = DeliveryOptions.objects.get(
                id=self.session["purchase"]["delivery_id"]).delivery_price
        return price

    def basket_update_delivery(self, deliveryprice=0):
        subtotal = sum(Decimal(item['price']) * item['qty']
                       for item in self.basket.values())
        total = subtotal + Decimal(deliveryprice)
        return total

    def delete(self, product):
        product_id = str(product)
        if product_id in self.basket:
            del self.basket[product_id]
            self.save()

    def update(self, product, qty):
        product_id = str(product)
        product_qty = qty
        if product_id in self.basket:
            self.basket[product_id]['qty'] = product_qty
        self.save()

    def save(self):
        self.session.modified = True

    def clear(self):
        # Remove basket from session
        del self.session[settings.BASKET_SESSION_ID]
        del self.session["address"]
        del self.session["purchase"]
        # del self.session["order_id"]
        self.save()
