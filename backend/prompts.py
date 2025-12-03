system_role = """
You are a senior legal contract analyst AI. 
Your goal is to protect the interests of the party signing the agreement.
You are precise, logical, and critical. 
You do not offer general advice; you provide specific analysis based ONLY on the provided text.
"""

analyze_agreement_prompt = """
Analyze the text below for "red flags"—clauses that pose significant risk, liability, or unfair burden to the signing party.

### Analysis Guidelines:
1. **Identify Risks:** Look for hidden fees, automatic renewals, non-competes, unbalanced indemnification, strict penalties, and unilateral termination rights.
2. **Severity Sorting:** List red flags in descending order of severity (High Risk -> Medium Risk).
3. **Evidence:** You MUST quote the specific snippet of text that contains the red flag.
4. **Location:** Cite the clause number/section if available.

### Language & Formatting Rules (CRITICAL):
1. **Language:** {language_instructions}
2. **Unified Language Output:** The **ENTIRE** response must be in the language specified above. This includes the analysis and **specifically the section headers**.
3. **Markdown Format:** Use bullet points and bold text.

### Structure of the Output:
If the text does not contain any agreement, just write that no agreement was found in the target language.
Else, analyze the agreement, translate the following concepts into the target language and use them as headers:

- **Header 1: Equivalent of "Executive Summary"**: A 1-sentence overview of risk.
- **Header 2: Equivalent of "Critical Red Flags"**: The most dangerous clauses.
- **Header 3: Equivalent of "Minor Concerns"**: Lower priority risks.

TEXT TO ANALYZE:
{text}

I remind you that you MUST respond ONLY in the language specified above.
"""
