from django.shortcuts import render
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .models import Product, Order, OrderProduct
from django.shortcuts import redirect
from django.db import models
from django.db.models import Sum, F, ExpressionWrapper, DecimalField, Value
from . import helpers


@method_decorator(login_required, name='dispatch')
class HomeView(View):
    def get(self, request):
        next_order_number = helpers.next_order_number_sqlite()

        return render(request, 'home.html', {'next_order_number': next_order_number})

class DetailView(View):
    def get(self, request, order_id):
        order = Order.objects.annotate(
            total_amount=Sum(
            ExpressionWrapper(
                F('orderproduct__quantity') * F('orderproduct__product__price'),
                output_field=DecimalField(max_digits=10, decimal_places=2)
            )
            ),
        ).get(id=order_id)
        ordered_products = OrderProduct.objects.filter(order=order)        

        return render(request, 'detail.html', {'order': order, 'ordered_products': ordered_products })
    
    def post(self, request, order_id):
        action = request.POST.get('action')
        order = Order.objects.get(id=order_id)

        if action == 'mark_completed':
            order.completed = True
        elif action == 'mark_received':
            order.completed = True
            order.delivered = True
        order.save()

        return redirect('order:detail', order_id=order_id)

@method_decorator(login_required, name='dispatch')
class CreateView(View):
    def get(self, request):
        next_order_number = helpers.next_order_number_sqlite()
        categories = Product.objects.values_list('category', flat=True).distinct()
        products_by_category = {}
        for category in categories:
            products_by_category[category] = Product.objects.filter(category=category)

        return render(request, 'create.html', {'products_by_category': products_by_category, 'next_order_number': next_order_number })

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
        for product in products:
            quantity = request.POST.get(f'quantity_{product.id}')
            if  quantity and int(quantity) > 0:
                OrderProduct.objects.create(
                    order=order,
                    product=product,
                    quantity=int(quantity),
                )
        
        order.save()
        return redirect('order:summary')

@method_decorator(login_required, name='dispatch')
class SummaryView(View):
    def get(self, request):
        date = request.GET.get('date')
        remove_delivered = request.GET.get('remove_delivered')
        orders = Order.objects.all().annotate(
            total_amount=Sum(
                ExpressionWrapper(
                    F('orderproduct__quantity') * F('orderproduct__product__price'),
                    output_field=DecimalField(max_digits=10, decimal_places=2)
                )
            ),
            rest_to_pay=ExpressionWrapper(
                
                models.Case(
                    models.When(
                        delivered=True,
                        then=Value(0, output_field=DecimalField(max_digits=10, decimal_places=2))
                    ),
                    default=F('total_amount') - F('deposit_amount'),                     
                ),
                output_field=DecimalField(max_digits=10, decimal_places=2)

            )
        )

        if date:
            orders = orders.filter(delivery_date=date)

        if remove_delivered:
            orders = orders.exclude(delivered=True)

        categories = Product.objects.values_list('category', flat=True).distinct()
        ordered_products = {}

        for category in categories:
            ordered_products[category] = OrderProduct.objects.filter(
                product__category=category
            ).values('product__name').annotate(
                product_total_quantity=Sum('quantity'),
                product_total_amount=Sum(
                    ExpressionWrapper(
                        F('quantity') * F('product__price'),
                        output_field=DecimalField(max_digits=10, decimal_places=2)
                    )
                )
            ).order_by('product__name')

            if date:
                ordered_products[category] = ordered_products[category].filter(
                    order__delivery_date=date
                )
            if remove_delivered:
                ordered_products[category] = ordered_products[category].exclude(
                    order__delivered=True
                )

        totals = {}

        for category, products in ordered_products.items():
            totals[category] = products.aggregate(
                total_quantity=Sum('product_total_quantity'),
                total_amount=Sum('product_total_amount')
            )

        return render(
            request,
            'summary.html',
            {
                'orders': orders,
                'totals': totals,
                'ordered_products': ordered_products,        
                'total_rest_to_pay': orders.aggregate(Sum('rest_to_pay'))['rest_to_pay__sum'] or 0,
                'total_amount_orders': orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0,                
            }
        )
