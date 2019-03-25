from django.shortcuts import redirect

from restaurant_admin.models import *
from django.views.generic import ListView, DetailView, TemplateView
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
from django.views.generic.edit import FormMixin
from .forms import FormOrder


class IndexView(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        if 'food_orders_list' not in self.request.session:
            fo_list = []
            self.request.session['food_orders_list'] = fo_list
        fo_list = self.request.session['food_orders_list']
        ordered_foods = FoodOrder.objects.filter(pk__in=fo_list)

        if 'order_list_pk' not in self.request.session:
            ol = OrderList.objects.create()
            self.request.session['order_list_pk'] = ol.pk
        ol_pk = self.request.session['order_list_pk']
        order_list = OrderList.objects.get(pk=ol_pk)

        context['food_order'] = ordered_foods.values()
        context['order_status'] = order_list.status

        return context


class FoodCategoryListView(ListView):
    model = FoodCategory
    context_object_name = 'categories'
    template_name = 'customer/category_list.html'

    def get_context_data(self, **kwargs):
        context = super(FoodCategoryListView, self).get_context_data(**kwargs)
        if 'food_orders_list' not in self.request.session:
            fo_list = []
            self.request.session['food_orders_list'] = fo_list
        fo_list = self.request.session['food_orders_list']
        ordered_foods = FoodOrder.objects.filter(pk__in=fo_list)

        if 'order_list_pk' not in self.request.session:
            ol = OrderList.objects.create()
            self.request.session['order_list_pk'] = ol.pk
        ol_pk = self.request.session['order_list_pk']
        order_list = OrderList.objects.get(pk=ol_pk)

        context['food_order'] = ordered_foods.values()
        context['order_status'] = order_list.status

        return context


# TODO : clear session and database after pay

# TODO : dont refresh the page after adding or removing food

# TODO : order more food after first order_list status is preparing


class FoodCategoryDetailView(DetailView):
    model = FoodCategory
    context_object_name = 'category'
    template_name = 'customer/category_detail.html'

    def get_context_data(self, **kwargs):
        context = super(FoodCategoryDetailView, self).get_context_data(**kwargs)
        # del self.request.session['order_list_pk']
        if 'food_orders_list' not in self.request.session:
            fo_list = []
            self.request.session['food_orders_list'] = fo_list
        fo_list = self.request.session['food_orders_list']
        ordered_foods = FoodOrder.objects.filter(pk__in=fo_list)

        if 'order_list_pk' not in self.request.session:
            ol = OrderList.objects.create()
            self.request.session['order_list_pk'] = ol.pk
        ol_pk = self.request.session['order_list_pk']
        order_list = OrderList.objects.get(pk=ol_pk)

        context['food_order'] = ordered_foods.values()
        context['ordered'] = ordered_foods.values_list('food', flat=True).distinct()
        context['order_status'] = order_list.status

        return context

    def post(self, request, *args, **kwargs):
        if request.POST.get('addFood'):
            food_pk = request.POST.get('food_pk')
            food = Food.objects.get(pk=food_pk)

            if 'food_orders_list' not in self.request.session:
                fo_list = []
                self.request.session['food_orders_list'] = fo_list
            fo_list = self.request.session['food_orders_list']
            ordered_foods = FoodOrder.objects.filter(pk__in=fo_list)

            try:
                ordered_foods = ordered_foods.get(food=food)
                ordered_foods.number = ordered_foods.number + 1
                ordered_foods.cost = ordered_foods.cost + food.cost
                ordered_foods.save()
            except ObjectDoesNotExist:
                food_order = FoodOrder(food=food, number=1, cost=food.cost)
                food_order.save()
                fo_list.append(food_order.pk)
                self.request.session['food_orders_list'] = fo_list

            return HttpResponseRedirect(self.request.path_info)

        if request.POST.get('removeFood'):
            food_pk = request.POST.get('food_pk')
            food = Food.objects.get(pk=food_pk)

            if 'food_orders_list' not in self.request.session:
                fo_list = []
                self.request.session['food_orders_list'] = fo_list
            fo_list = self.request.session['food_orders_list']
            ordered_foods = FoodOrder.objects.filter(pk__in=fo_list)

            try:
                ordered_foods = ordered_foods.get(food=food)
                if ordered_foods.number == 1:
                    fo_list.remove(ordered_foods.pk)
                    self.request.session['food_orders_list'] = fo_list
                    ordered_foods.delete()
                else:
                    ordered_foods.number = ordered_foods.number - 1
                    ordered_foods.cost = ordered_foods.cost - food.cost
                    ordered_foods.save()
            except ObjectDoesNotExist:
                pass

            return HttpResponseRedirect('')

        return HttpResponseRedirect('')


class OrderListView(FormMixin, ListView):
    model = OrderList
    template_name = 'customer/order_list.html'
    form_class = FormOrder

    def get_context_data(self, **kwargs):
        context = super(OrderListView, self).get_context_data(**kwargs)
        if 'food_orders_list' not in self.request.session:
            fo_list = []
            self.request.session['food_orders_list'] = fo_list
        fo_list = self.request.session['food_orders_list']
        ordered_foods = FoodOrder.objects.filter(pk__in=fo_list)

        if 'order_list_pk' not in self.request.session:
            ol = OrderList.objects.create()
            self.request.session['order_list_pk'] = ol.pk
        ol_pk = self.request.session['order_list_pk']
        order_list = OrderList.objects.get(pk=ol_pk)

        context['food_order'] = ordered_foods.values()
        context['ordered_foods'] = ordered_foods
        context['ordered'] = ordered_foods.values_list('food', flat=True).distinct()
        context['order_status'] = order_list.status

        cost_vals = Cost.objects.get(pk=1)
        food_costs = ordered_foods.values_list('cost', flat=True).distinct()
        food_numbers = ordered_foods.values_list('number', 'food').distinct()

        total_food_costs = 0
        for cost in food_costs:
            total_food_costs += cost

        n = 0
        for item in food_numbers:
            if Food.objects.get(pk=item[1]).takeaway_price:
                n += item[0]

        packaging_charge = cost_vals.packaging_cost * n
        tax = cost_vals.tax * total_food_costs / 100
        service_charge = cost_vals.service_charge * total_food_costs / 100

        context['packaging_charge'] = packaging_charge
        context['tax'] = tax
        context['service_charge'] = service_charge
        context['total_food_cost'] = total_food_costs
        context['total_cost_wt'] = total_food_costs + service_charge + tax + packaging_charge
        context['total_cost_nt'] = total_food_costs + service_charge + tax

        self.request.session['total_cost_wt'] = total_food_costs + service_charge + tax + packaging_charge
        self.request.session['total_cost_nt'] = total_food_costs + service_charge + tax
        return context

    def post(self, request, *args, **kwargs):
        if request.POST.get('addFood'):
            food_pk = request.POST.get('food_pk')
            food = Food.objects.get(pk=food_pk)

            if 'food_orders_list' not in self.request.session:
                fo_list = []
                self.request.session['food_orders_list'] = fo_list
            fo_list = self.request.session['food_orders_list']
            ordered_foods = FoodOrder.objects.filter(pk__in=fo_list)

            try:
                ordered_foods = ordered_foods.get(food=food)
                ordered_foods.number = ordered_foods.number + 1
                ordered_foods.cost = ordered_foods.cost + food.cost
                ordered_foods.save()
            except ObjectDoesNotExist:
                food_order = FoodOrder(food=food, number=1, cost=food.cost)
                food_order.save()
                fo_list.append(food_order.pk)
                self.request.session['food_orders_list'] = fo_list

            return HttpResponseRedirect('')

        if request.POST.get('removeFood'):
            food_pk = request.POST.get('food_pk')
            food = Food.objects.get(pk=food_pk)

            if 'food_orders_list' not in self.request.session:
                fo_list = []
                self.request.session['food_orders_list'] = fo_list
            fo_list = self.request.session['food_orders_list']
            ordered_foods = FoodOrder.objects.filter(pk__in=fo_list)

            try:
                ordered_foods = ordered_foods.get(food=food)
                if ordered_foods.number == 1:
                    fo_list.remove(ordered_foods.pk)
                    self.request.session['food_orders_list'] = fo_list
                    ordered_foods.delete()
                else:
                    ordered_foods.number = ordered_foods.number - 1
                    ordered_foods.cost = ordered_foods.cost - food.cost
                    ordered_foods.save()
            except ObjectDoesNotExist:
                pass

            return HttpResponseRedirect('')

        if request.POST.get('order'):
            form = FormOrder(request.POST)

            if 'order_list_pk' not in self.request.session:
                ol = OrderList.objects.create()
                self.request.session['order_list_pk'] = ol.pk
            ol_pk = self.request.session['order_list_pk']
            order_list = OrderList.objects.get(pk=ol_pk)
            table = Table.objects.get(pk=form['table'].value())

            if 'food_orders_list' not in self.request.session:
                fo_list = []
                self.request.session['food_orders_list'] = fo_list
            fo_list = self.request.session['food_orders_list']
            ordered_foods = FoodOrder.objects.filter(pk__in=fo_list)

            order_list_food_orders = order_list.FoodOrder_list.all()

            for order in order_list_food_orders :
                if order not in ordered_foods:
                    order.delete()

            for order in ordered_foods:
                try:
                    of = order_list_food_orders.get(food=order.food)
                    of.delete()
                except ObjectDoesNotExist:
                    pass
                tmp = FoodOrder(food=order.food, number=order.number, cost=order.cost)
                tmp.order_list = order_list
                tmp.save()

            order_list.details = form['details'].value()
            order_list.takeaway = form['takeaway'].value()
            if order_list.takeaway:
                order_list.cost = self.request.session['total_cost_wt']
            else:
                order_list.cost = self.request.session['total_cost_nt']

            if order_list.status == 'NO':
                order_list.status = 'OR'
            elif order_list.status == 'OR' or order_list.status == 'CH':
                order_list.status = 'CH'
                old_table = Table.objects.get(pk=order_list.table.pk)
                old_table.table_availability = True
                old_table.save()

            order_list.table = table

            table.table_availability = False
            table.save()
            order_list.save()
            return redirect('index')

        return HttpResponseRedirect("")
