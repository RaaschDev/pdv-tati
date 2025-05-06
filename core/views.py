from django.shortcuts import render, redirect
from products.models import Tables, Product, Order, Category, OrderItem
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q
from datetime import datetime
from django.utils import timezone
from collections import defaultdict 
import json
from .models import FinishedOrder, FinishedOrderItem
from django.db.models import Sum
from .decorators import login_required

def login_view(request):
    # Se o usuário já estiver logado, redireciona para a home
    if request.user.is_authenticated:
        return redirect('home')
        
    error_message = None
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.is_superuser:
                return redirect('home')
            else:
                return redirect('tables')
        else:
            error_message = 'Usuário ou senha inválidos'
    return render(request, 'pages/login.html', {'error_message': error_message})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def home(request):
    # Get today's date
    today = timezone.now().date()
    
    # Get today's finished orders
    today_orders = FinishedOrder.objects.filter(
        created_at__date=today
    )
    
    # Calculate total orders and value for today
    total_orders_today = today_orders.count()
    total_value_today = today_orders.aggregate(
        total=Sum('total_price')
    )['total'] or 0
    
    # Get most sold products
    most_sold_products = FinishedOrderItem.objects.filter(
        finishedorder__created_at__date=today
    ).values(
        'product__name'
    ).annotate(
        total_quantity=Sum('quantity')
    ).order_by('-total_quantity')[:5]
    
    context = {
        'user': request.user,
        'total_orders_today': total_orders_today,
        'total_value_today': total_value_today,
        'most_sold_products': most_sold_products,
    }
    return render(request, 'pages/home.html', context)

def mesas(request):
    tables = Tables.objects.all()
    return render(request, 'pages/tables.html', {'tables': tables})

def table_detail(request, table_id):
    table = Tables.objects.get(id=table_id)
    # Get products by category
    food_products = Product.objects.filter(category__name='Comida')
    drink_products = Product.objects.filter(category__name='Bebida')
    orders = Order.objects.filter(table=table)
    order_items = OrderItem.objects.filter(order__in=orders)
    total = sum(item.total_value for item in order_items)

    context = {
        'table': table,
        'food_products': food_products,
        'drink_products': drink_products,
        'orders': orders,
        'order_items': order_items,
        'total': total
    }

    return render(request, 'pages/table_detail.html', context)

def products(request):
    products = Product.objects.all()
    categories = Category.objects.all()
    user = request.user
    context = {
        'products': products,
        'categories': categories,
        'user': user
    }
    return render(request, 'pages/products.html', context)

def create_product(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        price = request.POST.get('price')
        category_id = request.POST.get('category')
        
        product = Product(name=name, price=price, category_id=category_id)
        product.save()
        return redirect('products')
    return render(request, 'pages/create_product.html')

def close_order(request, table_id):
    table = Tables.objects.get(id=table_id)
    order = Order.objects.filter(table=table, status='aberto').latest('created_at')
    itens = OrderItem.objects.filter(order=order)
    
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        if not payment_method:
            context = {
                'table': table,
                'itens': itens,
                'order': order,
                'error': 'Selecione uma forma de pagamento'
            }
            return render(request, 'pages/finish_order.html', context)
            
        # Create finished order
        finished_order = FinishedOrder.objects.create(
            table=table,
            total_price=order.total_price,
            payment_method=payment_method
        )
        
        # Create finished order items
        for item in itens:
            finished_item = FinishedOrderItem.objects.create(
                product=item.product,
                quantity=item.quantity,
                price=item.product.price,
                total_value=item.total_value
            )
            finished_order.items.add(finished_item)
        
        # Update order status and payment method
        order.status = 'fechado'
        order.payment_method = payment_method
        order.save()
        
        # Delete all items from the current order
        itens.delete()
        
        # Create new empty order for the table
        new_order = Order.objects.create(
            table=table,
            status='aberto',
            total_price=0
        )
        
        # Update table status
        table.status = 'disponivel'
        table.save()
        return redirect('tables')
    
    context = {
        'table': table,
        'itens': itens,
        'order': order
    }
    return render(request, 'pages/finish_order.html', context)

def add_order_item(request, table_id):
    table = Tables.objects.get(id=table_id)
    product_id = request.POST.get('product_id')
    quantity = int(request.POST.get('quantity', 1))
    product = Product.objects.get(id=product_id)
    
    # Get or create order for the table
    order, created = Order.objects.get_or_create(
        table=table,
        status='aberto',
        defaults={'total_price': 0}
    )
    
    order_item = OrderItem(
        order=order,
        product=product,
        quantity=quantity
    )
    order_item.save()
    
    return redirect('table_detail', table_id)

def orders(request):
    # Get all finished orders
    finished_orders = FinishedOrder.objects.all().order_by('-created_at')
    
    # Group orders by date
    orders_by_date = defaultdict(list)
    for order in finished_orders:
        date = order.created_at.date()
        orders_by_date[date].append(order)
    
    # Convert to list of tuples for template
    orders_by_date = sorted(orders_by_date.items(), reverse=True)
    
    context = {
        'orders_by_date': orders_by_date,
    }
    return render(request, 'pages/orders.html', context)

def dashboard(request):
    # Get today's date
    today = timezone.now().date()
    
    # Get today's finished orders
    today_orders = FinishedOrder.objects.filter(
        created_at__date=today
    )
    
    # Calculate total orders and value for today
    total_orders_today = today_orders.count()
    total_value_today = today_orders.aggregate(
        total=Sum('total_price')
    )['total'] or 0
    
    # Get all products
    products = Product.objects.all()
    
    # Get all categories
    categories = Category.objects.all()
    
    context = {
        'products': products,
        'categories': categories,
        'total_orders_today': total_orders_today,
        'total_value_today': total_value_today,
    }
    return render(request, 'pages/dashboard.html', context)