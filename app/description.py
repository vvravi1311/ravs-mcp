from app.rag_tools import retrieve_context

uw_tool_description = """Evaluate a Medicare Supplement (Medigap) application and generate a complete underwriting decision.

    This tool analyzes eligibility for Medicare Supplement insurance based on federal regulations,
    state-specific rules, and applicant circumstances. It determines whether the applicant qualifies
    for guaranteed issue rights, open enrollment protections, or requires medical underwriting.

    Input Structure (EvaluateRequest):
    ---------------------------------
    {
        "application": {
            "applicationId": "string (required) - Unique application identifier",
            "receivedDate": "string (required) - Date received in YYYY-MM-DD format",
            "requestedEffectiveDate": "string (required) - Requested policy start date YYYY-MM-DD",
            "channel": "string (optional) - AGENT|BROKER|DIRECT|MGA",
            "carrierCode": "string (optional) - Carrier identifier"
        },
        "applicant": {
            "firstName": "string (optional)",
            "lastName": "string (optional)",
            "dateOfBirth": "string (required) - YYYY-MM-DD format",
            "state": "string (required) - 2-letter state code",
            "zip": "string (optional)",
            "tobaccoUse": "boolean (optional) - Default: false",
            "heightInches": "integer (optional) - Height in inches for BMI calculation",
            "weightPounds": "integer (optional) - Weight in pounds for BMI calculation",
            "partAEffectiveDate": "string (required) - Medicare Part A effective date YYYY-MM-DD",
            "partBEffectiveDate": "string (required) - Medicare Part B effective date YYYY-MM-DD",
            "currentlyOnMA": "boolean (optional) - Currently on Medicare Advantage, Default: false",
            "currentCoverageType": "string (optional) - NONE|MEDIGAP|MA|EMPLOYER_GROUP|UNION|SELECT|OTHER",
            "medicareEligibilityDate": "string (optional) - First Medicare eligibility date YYYY-MM-DD"
        },
        "coverage": {
            "requestedPlanLetter": "string (required) - A|B|C|D|F|G|K|L|M|N|HDG|HDF",
            "replacingCoverage": "boolean (optional) - Replacing existing coverage, Default: false",
            "replacingCoverageType": "string (optional) - NONE|MEDIGAP|MA|SELECT|EMPLOYER_GROUP|UNION|OTHER",
            "priorCreditableCoverageMonths": "integer (optional) - Months of prior creditable coverage",
            "gapSinceCreditableCoverageEndDays": "integer (optional) - Days without coverage since creditable coverage ended"
        },
        "giEvents": [
            {
                "type": "string (required) - MA_PLAN_TERMINATION|MA_MOVE_OUT_OF_SERVICE_AREA|MA_TRIAL_RIGHT_WITHIN_12M|EMPLOYER_GROUP_ENDING|MEDIGAP_INSOLVENCY|SELECT_MOVE_OUT_OF_AREA|CARRIER_RULE_VIOLATION_OR_MISLEADING",
                "triggeringDate": "string (required) - Date the GI event occurred YYYY-MM-DD"
            }
        ],
        "health": {
            "conditions": "array of strings (optional) - List of medical conditions",
            "medications": "array of strings (optional) - List of current medications",
            "oxygenUse": "boolean (optional) - Uses supplemental oxygen, Default: false",
            "adlAssistance": "boolean (optional) - Needs help with Activities of Daily Living, Default: false",
            "recentHospitalization": {
                "occurred": "boolean (optional) - Recent hospitalization occurred, Default: false",
                "dischargeDate": "string (optional) - Hospital discharge date YYYY-MM-DD"
            }
        },
        "context": "object (optional) - Additional contextual data"
    }

    Output Structure (EvaluateResponse):
    ------------------------------------
    {
        "decisionId": "string - Unique identifier for this evaluation",
        "status": "string - ACCEPT_NO_UW|ACCEPT_WITH_UW|DECLINE|PENDED",
        "underwritingRequired": "boolean - Whether manual underwriting is needed",
        "reasons": [
            {
                "code": "string - Machine-readable reason code (e.g., R-100, R-200)",
                "message": "string - Human-readable explanation"
            }
        ],
        "planRestrictions": {
            "allowedPlanLetters": "array of strings - Plans applicant is eligible for",
            "disallowedPlanLetters": "array of strings - Plans applicant cannot access",
            "notes": "array of strings - Additional eligibility notes"
        },
        "waitingPeriod": {
            "applies": "boolean - Whether a waiting period applies",
            "months": "integer - Length of waiting period in months",
            "reason": "string - Explanation for the waiting period"
        },
        "ratingGuidance": {
            "class": "string - PREFERRED|STANDARD|RATED",
            "suggestedFactor": "float - Rating factor (e.g., 1.15 for 15% rate-up)"
        },
        "requestsForInformation": "array of strings - Additional information needed from applicant",
        "audit": "object - Full rule audit trail showing which rules fired and why"
    }

    Key Decision Rules:
    ------------------
    - R-100: Open Enrollment (6-month window after Part B at age 65+)
    - R-200: Guaranteed Issue rights (MA termination, loss of coverage, etc.)
    - R-300: Medicare Advantage conflict check
    - R-400: Medical underwriting requirements
    - R-600: State-specific continuous GI protections
    - R-700: MACRA restrictions (Plans C/F unavailable for Medicare-eligible after 2020)
    """


rag_tool_description="""Retrieve relevant Medicare Supplement insurance documentation using semantic search.

Use this tool to answer questions about Medicare Supplement plans, benefits, coverage, and policy details.

Input Structure:
----------------
{
    "user_query": "string (required) - Natural language question from insurance agent"
}

Example Request:
---------------
{
    "user_query": "What does Plan N cover?"
}

Other Example Queries:
- "What are the differences between Plan G and Plan N?"
- "Does Plan F cover Part B deductible?"

Example Response:
-----------------
Returns tuple: (serialized_text: str, documents: List[Document])

serializedtext:
"Source: medicare-plan-n-benefits.pdf

Content: Plan N covers Medicare Part A coinsurance and hospital costs up to an additional 365 days after Medicare benefits are used up. It also covers Medicare Part B coinsurance or copayment, with the exception of up to $20 copayment for office visits and up to $50 copayment for emergency room visits.

Source: medicare-plans-comparison.pdf

Content: Plan N provides comprehensive coverage similar to Plan G but requires small copayments for office visits ($20) and emergency room visits ($50 if not admitted)."

documents:
[
    Document(page_content="Plan N covers...", metadata={"source": "medicare-plan-n-benefits.pdf"}),
    Document(page_content="Plan N provides...", metadata={"source": "medicare-plans-comparison.pdf"})
]

Technical Details:
- Retrieves top 3 most relevant documents
- Uses semantic similarity search
- Results are cached for performance
"""