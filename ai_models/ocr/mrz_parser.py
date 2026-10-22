import re


def mrz_check_digit(value):
    """
    Calculate MRZ check digit using ICAO rules.

    0-9 = numeric value
    A-Z = 10-35
    <   = 0
    """

    weights = [7, 3, 1]
    total = 0

    for i, char in enumerate(value):

        if char.isdigit():
            number = int(char)

        elif "A" <= char <= "Z":
            number = ord(char) - ord("A") + 10

        elif char == "<":
            number = 0

        else:
            return None

        total += number * weights[i % 3]

    return total % 10


def parse_mrz(mrz_text):

    # -------------------------
    # Clean OCR lines
    # -------------------------

    lines = [
        re.sub(r"[^A-Z0-9<]", "", line.upper())
        for line in mrz_text.splitlines()
        if line.strip()
    ]

    # TD3 passport MRZ:
    # 2 lines
    # 44 characters per line

    mrz_lines = [
        line
        for line in lines
        if len(line) == 44
    ]

    if len(mrz_lines) < 2:

        return {
            "valid": False,
            "validation_status": "INVALID",
            "message": "Valid 44-character passport MRZ not found",
            "lines": []
        }

    line1 = mrz_lines[0]
    line2 = mrz_lines[1]

    # -------------------------
    # Document type validation
    # -------------------------

    if line1[0] != "P":

        return {
            "valid": False,
            "validation_status": "INVALID",
            "message": "Invalid passport MRZ document type",
            "lines": mrz_lines[:2]
        }

    # -------------------------
    # Line 1 fields
    # -------------------------

    document_type = line1[0]

    country = line1[2:5]

    name_part = line1[5:]

    name_parts = name_part.split("<<")

    surname = name_parts[0].replace("<", " ").strip()

    given_names = ""

    if len(name_parts) > 1:
        given_names = (
            name_parts[1]
            .replace("<", " ")
            .strip()
        )

    # -------------------------
    # Line 2 fields
    # -------------------------

    document_number = line2[0:9]

    document_number_check = line2[9]

    nationality = line2[10:13]

    date_of_birth = line2[13:19]

    date_of_birth_check = line2[19]

    sex = line2[20]

    expiry_date = line2[21:27]

    expiry_date_check = line2[27]

    optional_data = line2[28:43]

    composite_check = line2[43]

    # -------------------------
    # Individual check digits
    # -------------------------

    document_check_valid = (
        document_number_check.isdigit()
        and
        mrz_check_digit(document_number)
        == int(document_number_check)
    )

    dob_check_valid = (
        date_of_birth_check.isdigit()
        and
        mrz_check_digit(date_of_birth)
        == int(date_of_birth_check)
    )

    expiry_check_valid = (
        expiry_date_check.isdigit()
        and
        mrz_check_digit(expiry_date)
        == int(expiry_date_check)
    )

    # -------------------------
    # Composite check
    # -------------------------

    composite_data = (
        line2[0:10]
        + line2[13:20]
        + line2[21:43]
    )

    composite_check_valid = (
        composite_check.isdigit()
        and
        mrz_check_digit(composite_data)
        == int(composite_check)
    )

    # -------------------------
    # Overall validation
    # -------------------------

    all_checks_valid = (
        document_check_valid
        and
        dob_check_valid
        and
        expiry_check_valid
        and
        composite_check_valid
    )

    # -------------------------
    # Validation status
    # -------------------------

    if all_checks_valid:

        validation_status = "VALID"

    elif (
        document_check_valid
        and
        dob_check_valid
        and
        expiry_check_valid
    ):

        validation_status = "OCR_UNCERTAIN"

    else:

        validation_status = "INVALID"

    # -------------------------
    # Final result
    # -------------------------

    return {

        "valid": all_checks_valid,

        "validation_status": validation_status,

        "document_type": document_type,

        "country": country,

        "surname": surname,

        "given_names": given_names,

        "document_number": (
            document_number.replace("<", "")
        ),

        "nationality": nationality,

        "date_of_birth": date_of_birth,

        "sex": sex,

        "expiry_date": expiry_date,

        "check_digits": {

            "document_number":
                document_check_valid,

            "date_of_birth":
                dob_check_valid,

            "expiry_date":
                expiry_check_valid,

            "composite":
                composite_check_valid
        },

        "lines": mrz_lines[:2]
    }