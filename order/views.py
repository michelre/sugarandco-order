from django.shortcuts import render
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .models import Product, Order, OrderProduct
from django.shortcuts import redirect
from django.db import models
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from . import helpers


@method_decorator(login_required, name='dispatch')
class HomeView(View):
    def get(self, request):
        next_order_number = helpers.next_order_number_sqlite()

        return render(request, 'home.html', {'next_order_number': next_order_number})

@method_decorator(login_required, name='dispatch')
class CreateView(View):
    def get(self, request):
        next_order_number = helpers.next_order_number_sqlite()
        products = Product.objects.all()
        print(f"Fetched products: {products}")
        return render(request, 'create.html', {'products': products, 'next_order_number': next_order_number })

    def post(self, request):
        # Handle form submission
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        comments = request.POST.get('comments')
        deposit_amount = request.POST.get('deposit_amount')
        delivery_date = request.POST.get('delivery_date')

        order = Order.objects.create(
            name=name,
            phone=phone,
            comments=comments,
            deposit_amount=deposit_amount,
            delivery_date=delivery_date    
        )

        products = Product.objects.all()
        total_amount = 0
        for product in products:
            quantity = request.POST.get(f'quantity_{product.id}')
            if quantity and int(quantity) > 0:
                OrderProduct.objects.create(
                    order=order,
                    product=product,
                    quantity=int(quantity)
                )
                total_amount += product.price * int(quantity)

        # Process the data (e.g., save to the database)
        order.total_amount = total_amount
        order.save()
        return redirect('order:summary')

@method_decorator(login_required, name='dispatch')
class SummaryView(View):
    def get(self, request):
        orders = Order.objects.all().annotate(
            rest_to_pay=ExpressionWrapper(F('total_amount') - F('deposit_amount'), output_field=DecimalField(max_digits=10, decimal_places=2)),            
        )

        ordered_products = OrderProduct.objects.values('product__name').annotate(
            product_total_quantity=Sum('quantity'),
            product_total_amount=Sum(
                ExpressionWrapper(
                    F('quantity') * F('product__price'),
                    output_field=DecimalField(max_digits=10, decimal_places=2)
                )
            ),
        )

        return render(
            request,
            'summary.html',
            {
                'orders': orders,
                'ordered_products': ordered_products,
                'ordered_total_price': ordered_products.aggregate(Sum('product_total_amount'))['product_total_amount__sum'] or 0,
                'total_rest_to_pay': orders.aggregate(Sum('rest_to_pay'))['rest_to_pay__sum'] or 0,
                'total_amount_orders': orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0,
                'total_products': ordered_products.aggregate(Sum('product_total_quantity'))['product_total_quantity__sum'] or 0
            }
        )
