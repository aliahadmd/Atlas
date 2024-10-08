# portfolio_management/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, F, Count
from .models import Portfolio, PortfolioAsset, Transaction, PortfolioPerformance
from .forms import PortfolioForm, PortfolioAssetForm, TransactionForm
from datetime import date
import logging
from django.db import transaction
from django.core.exceptions import ValidationError
from decimal import Decimal
from risk_management.models import Risk
from .gemini_ai import get_portfolio_insights, get_risk_assessment, get_market_trends, get_ai_investment_advice
from django.http import JsonResponse
from markdown2 import markdown
from django.utils.safestring import mark_safe

logger = logging.getLogger(__name__)

@login_required
def portfolio_list(request):
    portfolios = Portfolio.objects.filter(owner=request.user).prefetch_related(
        "portfolio_assets__asset", "performances"
    )

    performance_dates = PortfolioPerformance.objects.filter(
        portfolio__owner=request.user
    ).dates("date", "day")

    total_values = []
    for date in performance_dates:
        total_value = (
            PortfolioPerformance.objects.filter(
                portfolio__owner=request.user, date=date
            ).aggregate(total=Sum("total_value"))["total"]
            or 0
        )
        total_values.append(str(total_value))

    for portfolio in portfolios:
        portfolio.asset_values = []
        portfolio.asset_names = []
        for asset in portfolio.portfolio_assets.all():
            value = asset.quantity * asset.asset.value
            portfolio.asset_values.append(str(value))
            portfolio.asset_names.append(asset.asset.name)

    risk_overview = Risk.objects.filter(portfolios__owner=request.user).values('risk_type').annotate(count=Count('id'))

    context = {
        "portfolios": portfolios,
        "performance_dates": [date.strftime("%Y-%m-%d") for date in performance_dates],
        "total_values": total_values,
        "risk_overview": risk_overview,
    }
    return render(request, "portfolio_management/portfolio_list.html", context)

@login_required
def portfolio_detail(request, portfolio_id):
    portfolio = get_object_or_404(Portfolio, id=portfolio_id, owner=request.user)
    assets = portfolio.portfolio_assets.all()
    transactions = portfolio.transactions.order_by("-transaction_date")[:10]
    performance = portfolio.performances.order_by("-date").first()
    risks = Risk.objects.filter(portfolios=portfolio)

    context = {
        "portfolio": portfolio,
        "assets": assets,
        "transactions": transactions,
        "performance": performance,
        "risks": risks,
    }
    return render(request, "portfolio_management/portfolio_detail.html", context)

@login_required
def portfolio_create(request):
    if request.method == "POST":
        form = PortfolioForm(request.POST)
        if form.is_valid():
            portfolio = form.save(commit=False)
            portfolio.owner = request.user
            portfolio.save()
            messages.success(request, "Portfolio created successfully.")
            return redirect("portfolio_management:portfolio_detail", portfolio_id=portfolio.id)
    else:
        form = PortfolioForm()
    return render(request, "portfolio_management/portfolio_form.html", {"form": form})

@login_required
def portfolio_update(request, portfolio_id):
    portfolio = get_object_or_404(Portfolio, id=portfolio_id, owner=request.user)
    if request.method == "POST":
        form = PortfolioForm(request.POST, instance=portfolio)
        if form.is_valid():
            form.save()
            messages.success(request, "Portfolio updated successfully.")
            return redirect("portfolio_management:portfolio_detail", portfolio_id=portfolio.id)
    else:
        form = PortfolioForm(instance=portfolio)
    return render(request, "portfolio_management/portfolio_form.html", {"form": form})

@login_required
def portfolio_delete(request, portfolio_id):
    portfolio = get_object_or_404(Portfolio, id=portfolio_id, owner=request.user)
    if request.method == "POST":
        portfolio.delete()
        messages.success(request, "Portfolio deleted successfully.")
        return redirect("portfolio_management:portfolio_list")
    return render(request, "portfolio_management/portfolio_confirm_delete.html", {"portfolio": portfolio})

@login_required
def portfolio_asset_add(request, portfolio_id):
    portfolio = get_object_or_404(Portfolio, id=portfolio_id, owner=request.user)
    if request.method == "POST":
        form = PortfolioAssetForm(request.POST)
        if form.is_valid():
            asset = form.cleaned_data["asset"]
            quantity = form.cleaned_data["quantity"]
            purchase_price = form.cleaned_data["purchase_price"]
            purchase_date = form.cleaned_data["purchase_date"]

            portfolio_asset, created = PortfolioAsset.objects.get_or_create(
                portfolio=portfolio,
                asset=asset,
                defaults={
                    "quantity": quantity,
                    "purchase_price": purchase_price,
                    "purchase_date": purchase_date,
                },
            )

            if not created:
                total_value = (portfolio_asset.quantity * portfolio_asset.purchase_price) + (quantity * purchase_price)
                new_quantity = portfolio_asset.quantity + quantity
                new_avg_price = total_value / new_quantity

                portfolio_asset.quantity = new_quantity
                portfolio_asset.purchase_price = new_avg_price
                portfolio_asset.purchase_date = purchase_date
                portfolio_asset.save()

            messages.success(request, "Asset added to portfolio successfully.")
            return redirect("portfolio_management:portfolio_detail", portfolio_id=portfolio.id)
    else:
        form = PortfolioAssetForm()
    return render(request, "portfolio_management/portfolio_asset_form.html", {"form": form, "portfolio": portfolio})

@login_required
def portfolio_asset_update(request, portfolio_id, asset_id):
    portfolio = get_object_or_404(Portfolio, id=portfolio_id, owner=request.user)
    asset = get_object_or_404(PortfolioAsset, id=asset_id, portfolio=portfolio)
    if request.method == "POST":
        form = PortfolioAssetForm(request.POST, instance=asset)
        if form.is_valid():
            form.save()
            messages.success(request, "Asset updated successfully.")
            return redirect("portfolio_management:portfolio_detail", portfolio_id=portfolio.id)
    else:
        form = PortfolioAssetForm(instance=asset)
    return render(request, "portfolio_management/portfolio_asset_form.html", {"form": form, "portfolio": portfolio, "asset": asset})

@login_required
def portfolio_asset_delete(request, portfolio_id, asset_id):
    portfolio = get_object_or_404(Portfolio, id=portfolio_id, owner=request.user)
    asset = get_object_or_404(PortfolioAsset, id=asset_id, portfolio=portfolio)
    if request.method == "POST":
        asset.delete()
        messages.success(request, "Asset removed from portfolio successfully.")
        return redirect("portfolio_management:portfolio_detail", portfolio_id=portfolio.id)
    return render(request, "portfolio_management/portfolio_asset_confirm_delete.html", {"portfolio": portfolio, "asset": asset})

@login_required
def transaction_add(request, portfolio_id):
    portfolio = get_object_or_404(Portfolio, id=portfolio_id, owner=request.user)
    if request.method == "POST":
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.portfolio = portfolio
            transaction.save()
            update_portfolio_after_transaction(portfolio, transaction)
            messages.success(request, "Transaction added successfully.")
            return redirect("portfolio_management:portfolio_detail", portfolio_id=portfolio.id)
    else:
        form = TransactionForm()
    return render(request, "portfolio_management/transaction_form.html", {"form": form, "portfolio": portfolio})

@login_required
def transaction_update(request, portfolio_id, transaction_id):
    portfolio = get_object_or_404(Portfolio, id=portfolio_id, owner=request.user)
    transaction = get_object_or_404(Transaction, id=transaction_id, portfolio=portfolio)
    if request.method == "POST":
        form = TransactionForm(request.POST, instance=transaction)
        if form.is_valid():
            form.save()
            update_portfolio_after_transaction(portfolio, transaction)
            messages.success(request, "Transaction updated successfully.")
            return redirect("portfolio_management:portfolio_detail", portfolio_id=portfolio.id)
    else:
        form = TransactionForm(instance=transaction)
    return render(request, "portfolio_management/transaction_form.html", {"form": form, "portfolio": portfolio, "transaction": transaction})

@login_required
def transaction_delete(request, portfolio_id, transaction_id):
    portfolio = get_object_or_404(Portfolio, id=portfolio_id, owner=request.user)
    transaction = get_object_or_404(Transaction, id=transaction_id, portfolio=portfolio)
    if request.method == "POST":
        transaction.delete()
        update_portfolio_after_transaction(portfolio, transaction, delete=True)
        messages.success(request, "Transaction deleted successfully.")
        return redirect("portfolio_management:portfolio_detail", portfolio_id=portfolio.id)
    return render(request, "portfolio_management/transaction_confirm_delete.html", {"portfolio": portfolio, "transaction": transaction})

@login_required
def portfolio_performance(request, portfolio_id):
    portfolio = get_object_or_404(Portfolio, id=portfolio_id, owner=request.user)
    performances = portfolio.performances.order_by("-date")
    return render(request, "portfolio_management/portfolio_performance.html", {"portfolio": portfolio, "performances": performances})

@login_required
def associate_risk_with_portfolio(request, portfolio_id):
    portfolio = get_object_or_404(Portfolio, id=portfolio_id, owner=request.user)
    
    if request.method == 'POST':
        risk_id = request.POST.get('risk_id')
        risk = get_object_or_404(Risk, id=risk_id)
        
        portfolio.risks.add(risk)
        messages.success(request, f"Risk '{risk.name}' associated with portfolio '{portfolio.name}'.")
        
        return redirect('portfolio_management:portfolio_detail', portfolio_id=portfolio.id)
    
    available_risks = Risk.objects.exclude(portfolios=portfolio)
    
    context = {
        'portfolio': portfolio,
        'available_risks': available_risks,
    }
    return render(request, 'portfolio_management/associate_risk.html', context)

@login_required
def get_ai_investment_advice_view(request, portfolio_id):
    try:
        portfolio = get_object_or_404(Portfolio, id=portfolio_id, owner=request.user)
        
        user_preferences = request.session.get('user_preferences', {})
        portfolio_data = {
            'assets': [{'name': asset.asset.name, 'quantity': asset.quantity, 'value': asset.quantity * asset.asset.value} for asset in portfolio.portfolio_assets.all()],
            'total_value': sum(asset.quantity * asset.asset.value for asset in portfolio.portfolio_assets.all()),
        }
        
        ai_advice = get_ai_investment_advice(user_preferences, portfolio_data)
        ai_advice = markdown(ai_advice)
        ai_advice = mark_safe(ai_advice)
        
        return JsonResponse({'ai_advice': ai_advice})
    except Exception as e:
        logger.error(f"Error generating AI investment advice: {str(e)}")
        return JsonResponse({'error': 'Failed to generate AI investment advice'}, status=500)

@login_required
def ai_investment_advice(request, portfolio_id):
    portfolio = get_object_or_404(Portfolio, id=portfolio_id, owner=request.user)
    
    if request.method == 'POST':
        user_preferences = {
            'risk_tolerance': request.POST.get('risk_tolerance'),
            'investment_horizon': request.POST.get('investment_horizon'),
            'investment_goals': request.POST.get('investment_goals'),
            'preferred_sectors': request.POST.getlist('sectors'),
            'monthly_investment': request.POST.get('monthly_investment'),
            'esg_preference': request.POST.get('esg_preference') == 'on'
        }
        request.session['user_preferences'] = user_preferences
        
        context = {
            'portfolio': portfolio,
            'user_preferences': user_preferences
        }
        return render(request, 'portfolio_management/ai_investment_advice_result.html', context)
    
    return render(request, 'portfolio_management/ai_investment_advice_form.html', {'portfolio': portfolio})

@login_required
def get_ai_insights(request, portfolio_id):
    portfolio = get_object_or_404(Portfolio, id=portfolio_id, owner=request.user)
    assets = portfolio.portfolio_assets.all()
    risks = Risk.objects.filter(portfolios=portfolio)

    portfolio_data = {
        'assets': [{'name': asset.asset.name, 'quantity': asset.quantity, 'value': asset.quantity * asset.asset.value} for asset in assets],
        'total_value': sum(asset.quantity * asset.asset.value for asset in assets),
    }
    
    ai_insights = get_portfolio_insights(portfolio_data)
    
    risk_data = [{'name': risk.name, 'risk_type': risk.risk_type, 'description': risk.description} for risk in risks]
    ai_risk_assessment = get_risk_assessment(risk_data)

    asset_names = [asset.asset.name for asset in assets]
    ai_market_trends = get_market_trends(asset_names)

    ai_insights = markdown(ai_insights)
    ai_risk_assessment = markdown(ai_risk_assessment)
    ai_market_trends = markdown(ai_market_trends)
    return JsonResponse({
        'ai_insights': ai_insights,
        'ai_risk_assessment': ai_risk_assessment,
        'ai_market_trends': ai_market_trends,
    })

def update_portfolio_after_transaction(portfolio, transaction_obj, delete=False):
    try:
        with transaction.atomic():
            asset, created = PortfolioAsset.objects.get_or_create(
                portfolio=portfolio,
                asset=transaction_obj.asset,
                defaults={
                    "quantity": Decimal("0"),
                    "purchase_price": Decimal("0"),
                    "purchase_date": transaction_obj.transaction_date,
                },
            )

            quantity_change = transaction_obj.quantity if transaction_obj.transaction_type == "BUY" else -transaction_obj.quantity
            if delete:
                quantity_change = -quantity_change

            new_quantity = asset.quantity + quantity_change
            if new_quantity < 0:
                raise ValidationError("Transaction would result in negative asset quantity.")

            asset.quantity = new_quantity
            if not delete and transaction_obj.transaction_type == "BUY":
                # Update average purchase price
                total_value = (asset.quantity * asset.purchase_price) + (transaction_obj.quantity * transaction_obj.price)
                asset.purchase_price = total_value / asset.quantity
                asset.purchase_date = transaction_obj.transaction_date

            asset.save()

            # Update portfolio performance
            total_value = PortfolioAsset.objects.filter(portfolio=portfolio).aggregate(
                total=Sum(F('quantity') * F('asset__value'))
            )['total'] or Decimal('0')

            performance, created = PortfolioPerformance.objects.get_or_create(
                portfolio=portfolio,
                date=date.today(),
                defaults={
                    "total_value": total_value,
                    "daily_return": Decimal("0"),
                    "cumulative_return": Decimal("0"),
                },
            )

            if not created:
                performance.total_value = total_value
                performance.save()

            # Calculate returns
            previous_performance = PortfolioPerformance.objects.filter(
                portfolio=portfolio, date__lt=date.today()
            ).order_by('-date').first()

            if previous_performance and previous_performance.total_value > 0:
                daily_return = (total_value - previous_performance.total_value) / previous_performance.total_value
                cumulative_return = (total_value - previous_performance.total_value) / previous_performance.total_value
                performance.daily_return = daily_return
                performance.cumulative_return = cumulative_return
                performance.save()

    except ValidationError as e:
        logger.error(f"Validation error in update_portfolio_after_transaction: {str(e)}")
        raise

    except Exception as e:
        logger.error(f"Unexpected error in update_portfolio_after_transaction: {str(e)}")
        raise