import google.generativeai as genai
from django.conf import settings

# Configure the Gemini AI API
genai.configure(api_key=settings.GEMINI_API_KEY)

# Select the model
model = genai.GenerativeModel('gemini-pro')

def get_portfolio_insights(portfolio_data):
    prompt = f"""
    Analyze the following portfolio data and provide insights:
    {portfolio_data}
    
    Please provide:
    1. Overall portfolio health assessment
    2. Suggestions for diversification
    3. Potential risks and mitigation strategies
    4. Performance improvement recommendations
    """
    
    response = model.generate_content(prompt)
    return response.text

def get_risk_assessment(risk_data):
    prompt = f"""
    Assess the following risk data and provide an analysis:
    {risk_data}
    
    Please provide:
    1. Risk severity evaluation
    2. Potential impact on the portfolio
    3. Recommended risk management strategies
    4. Suggestions for risk monitoring
    """
    
    response = model.generate_content(prompt)
    return response.text

def get_market_trends(portfolio_assets):
    prompt = f"""
    Analyze current market trends for the following assets:
    {portfolio_assets}
    
    Please provide:
    1. Short-term market outlook for each asset
    2. Long-term growth potential
    3. Any emerging trends or news that might affect these assets
    4. Recommendations for portfolio adjustments based on market trends
    """
    
    response = model.generate_content(prompt)
    return response.text

def get_ai_investment_advice(user_preferences, portfolio_data):
    prompt = f"""
    Based on the following user preferences and current portfolio data, provide investment advice:
    User Preferences: {user_preferences}
    Portfolio Data: {portfolio_data}
    
    Please provide:
    1. Personalized investment recommendations
    2. Suggestions for rebalancing the portfolio
    3. Potential new investment opportunities aligned with user preferences
    4. Risk-adjusted strategies for portfolio optimization
    """
    
    response = model.generate_content(prompt)
    return response.text


