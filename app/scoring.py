def best_score(item):
    """
    Skyscanner-like balanced score.
    Lower price/dist/tat is better; higher rating is better.
    We don't have rating/dist yet for chains -> focus on price + tat.
    """
    price = item.get("price") or 10**9
    tat = item.get("tat_hours") or 72

    price_score = 1.0 / max(price, 1.0)
    tat_score = 1.0 / max(tat, 1.0)

    return 0.75 * price_score + 0.25 * tat_score