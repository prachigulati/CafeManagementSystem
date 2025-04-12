from main.models import Product

class Cart():
    def __init__(self, request):
        self.session = request.session
        # get the current session key if it exists
        cart = self.session.get('cart')
        #if the user is new, no session key so create one
        if 'cart' not in request.session:
            cart = self.session['cart'] = {}

            #make sure cart is available on all pages of site
        self.cart = cart


    def add(self, product, quantity):
        product_id = str(product.id)
        product_qty = str(quantity)
        #logic
        if product_id in self.cart:
            pass
        else:
            # self.cart[product_id] = {'price': str(product.price)}
            self.cart[product_id] = int(product_qty)
        self.session.modified = True

    def cart_total(self):
        #get product ids
        product_ids = self.cart.keys()
        #lookup those keys in our products databse model
        products = Product.objects.filter(id__in = product_ids)
        #get quantities
        quantities = self.cart
        #start counting at 0
        total=0
        for key, value in quantities.items():
            #convert key string into int so we can do math
            key = int(key)
            for product in products : 
                if product.id == key:
                    if product.is_sale:
                        total = total + (product.sale_price * value)
                    else:
                        total = total + (product.price * value)
        return total         


    def __len__(self):
        return len(self.cart)
    
    def get_prods(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        # return those looked up products
        return products
    
    def get_quants(self):
        quantities = self.cart
        return quantities
    
    def update(self, product, quantity):
        product_id = str(product)
        product_qty = int(quantity)
        #get the cart
        ourcart = self.cart
        ourcart[product_id]=product_qty
        self.session.modified = True
        thing = self.cart
        return thing 
    
    def delete(self, product):
        product_id = str(product)
        #delete from dictionary/cart
        if product_id in self.cart:
            del self.cart[product_id]
        self.session.modified =True

