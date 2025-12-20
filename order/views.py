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
        buches = Product.objects.filter(category='buche')
        breads = Product.objects.filter(category='pain')
        others = Product.objects.filter(category='autre')

        return render(request, 'create.html', {'buches': buches, 'breads': breads, 'others': others, 'next_order_number': next_order_number })

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

        ordered_products_buche = OrderProduct.objects.filter(
            product__category='buche'
        ).values('product__name').annotate(
            product_total_quantity=Sum('quantity'),
            product_total_amount=Sum(
            ExpressionWrapper(
                F('quantity') * F('product__price'),
                output_field=DecimalField(max_digits=10, decimal_places=2)
            )
            ),
        ).order_by('product__name')

        if date:
            ordered_products_buche = ordered_products_buche.filter(
                order__delivery_date=date
            )

        ordered_products_bread = OrderProduct.objects.filter(
            product__category='pain'
        ).values('product__name').annotate(
            product_total_quantity=Sum('quantity'),
            product_total_amount=Sum(
            ExpressionWrapper(
                F('quantity') * F('product__price'),
                output_field=DecimalField(max_digits=10, decimal_places=2)
            )
            ),
        ).order_by('product__name')

        if date:
            ordered_products_bread = ordered_products_bread.filter(
                order__delivery_date=date
            )

        ordered_products_other = OrderProduct.objects.filter(
            product__category='autre'
        ).values('product__name').annotate(
            product_total_quantity=Sum('quantity'),
            product_total_amount=Sum(
            ExpressionWrapper(
                F('quantity') * F('product__price'),
                output_field=DecimalField(max_digits=10, decimal_places=2)
            )
            ),
        ).order_by('product__name')

        if date:
            ordered_products_other = ordered_products_other.filter(
                order__delivery_date=date
            )

    
        # Totaux globaux pour la catégorie buche
        buche_totals = ordered_products_buche.aggregate(
            total_quantity=Sum('product_total_quantity'),
            total_amount=Sum('product_total_amount')
        )

        # Totaux globaux pour la catégorie buche
        bread_totals = ordered_products_bread.aggregate(
            total_quantity=Sum('product_total_quantity'),
            total_amount=Sum('product_total_amount')
        )

        # Totaux globaux pour la catégorie autre
        autre_totals = ordered_products_other.aggregate(
            total_quantity=Sum('product_total_quantity'),
            total_amount=Sum('product_total_amount')
        )

        return render(
            request,
            'summary.html',
            {
                'orders': orders,
                'ordered_products_buche': ordered_products_buche,
                'buche_totals': buche_totals,
                'ordered_products_bread': ordered_products_bread,
                'bread_totals': bread_totals,
                'ordered_products_other': ordered_products_other,
                'autre_totals': autre_totals,                
                'total_rest_to_pay': orders.aggregate(Sum('rest_to_pay'))['rest_to_pay__sum'] or 0,
                'total_amount_orders': orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0,                
            }
        )
