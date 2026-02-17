import matplotlib.pyplot as plt

def compute_feature_importance(case_data: dict):

    scores = {}

    # Rule-based scoring
    if case_data["customer_age_months"] < 6:
        scores["New Account (<6 months)"] = 0.3

    txn = case_data["transactions"][0]

    if txn["amount"] > 1000000:
        scores["Large Transaction"] = 0.8

    if txn["from_accounts"] > 10:
        scores["Multiple Source Accounts"] = 0.7

    if txn["destination_country"] not in ["India"]:
        scores["Offshore Transfer"] = 0.6

    return scores


def generate_shap_plot(scores: dict):

    features = list(scores.keys())
    values = list(scores.values())

    plt.figure()
    plt.barh(features, values)
    plt.xlabel("Risk Contribution Score")
    plt.title("SHAP-Style Risk Explanation")
    plt.tight_layout()
    plt.savefig("shap_explanation.png")

    return "shap_explanation.png"
