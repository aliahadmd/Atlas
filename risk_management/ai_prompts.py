# ai_prompts.py

def get_risk_analysis_prompt(risk_assessment, associated_assets):
    return f"""
    Analyze the following risk assessment:
    Risk: {risk_assessment.risk.name}
    Type: {risk_assessment.risk.risk_type}
    Probability: {risk_assessment.risk.probability}
    Impact: {risk_assessment.risk.impact}
    Mitigation Strategy: {risk_assessment.mitigation_strategy}
    Associated Assets: {associated_assets}

    Provide a comprehensive risk analysis including:
    1. A risk score between 0 and 1 (0 being lowest risk, 1 being highest risk)
    2. Detailed analysis of the risk and its potential impact
    3. Recommendations for managing and mitigating the risk
    4. Potential scenarios and their impacts
    5. Key performance indicators (KPIs) to monitor this risk

    Consider the following in your analysis:
    - The specific risk type and its implications
    - The probability and impact scores provided
    - The existing mitigation strategy and its effectiveness
    - The associated assets and their vulnerabilities

    Format your response with clear section headers for each part of the analysis.
    Use markdown formatting for better readability.
    """