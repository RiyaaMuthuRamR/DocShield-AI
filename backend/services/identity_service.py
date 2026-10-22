from rapidfuzz import fuzz

def compare_identity(doc1: dict, doc2: dict) -> dict:
    name1 = (doc1.get("name") or "").strip().casefold()
    name2 = (doc2.get("name") or "").strip().casefold()
    dob1 = (doc1.get("dob") or "").strip()
    dob2 = (doc2.get("dob") or "").strip()
    type1 = (doc1.get("document_type") or "").strip().casefold()
    type2 = (doc2.get("document_type") or "").strip().casefold()

    name_similarity = round(float(fuzz.ratio(name1, name2)), 2) if name1 and name2 else 0.0
    checks = {
        "name_similarity": name_similarity,
        "name_match": bool(name1 and name2 and name_similarity >= 90),
        "dob_match": bool(dob1 and dob2 and dob1 == dob2),
    }
    score = (40 if checks["name_match"] else 0) + (40 if checks["dob_match"] else 0)

    # Document numbers normally differ across different document types. Compare only
    # when the user explicitly identifies both documents as the same type.
    if type1 and type2 and type1 == type2:
        number1 = (doc1.get("document_number") or "").replace(" ", "").upper()
        number2 = (doc2.get("document_number") or "").replace(" ", "").upper()
        checks["document_number_comparable"] = True
        checks["document_number_match"] = bool(number1 and number2 and number1 == number2)
        score += 20 if checks["document_number_match"] else 0
    else:
        checks["document_number_comparable"] = False
        checks["document_number_match"] = None

    if not name1 or not name2 or not dob1 or not dob2:
        status = "INSUFFICIENT DATA"
    elif score >= 80:
        status = "MATCHED"
    elif score >= 40:
        status = "PARTIAL MATCH"
    else:
        status = "MISMATCH"
    return {"identity_score": score, "status": status, "checks": checks}
