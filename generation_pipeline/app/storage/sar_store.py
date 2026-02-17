sar_database = {}

def save_sar(case_id: str, sar_content: dict):
    if case_id not in sar_database:
        sar_database[case_id] = []

    sar_database[case_id].append(sar_content)
    return len(sar_database[case_id])


def get_previous_versions(case_id: str):
    return sar_database.get(case_id, [])
