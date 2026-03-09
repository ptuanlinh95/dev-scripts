import re

def update_sql_in_place(file_path):
    insert_pattern = re.compile(r"INSERT INTO (.*?) \((.*?)\) VALUES \((.*)\);", re.IGNORECASE)
    value_pattern = re.compile(r"'((?:''|[^'])*)'|(null)", re.IGNORECASE)
    placeholder_pattern = re.compile(r"\?([A-Z0-9_]+)")

    updated_content = []

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    for line in lines:
        stripped = line.strip()
        if not stripped or not stripped.upper().startswith("INSERT"):
            updated_content.append(line)
            continue

        match = insert_pattern.search(stripped)
        if not match:
            updated_content.append(line)
            continue

        table_name = match.group(1).strip()
        columns_str = match.group(2).strip()
        values_str = match.group(3).strip()

        extracted_values = []
        for val in value_pattern.findall(values_str):
            if val[1].lower() == 'null':
                extracted_values.append(None)
            else:
                extracted_values.append(val[0])

        if len(extracted_values) > 6:
            message_us = extracted_values[3] or ""
            current_params = extracted_values[6] or ""

            found_placeholders = []
            for p in placeholder_pattern.findall(message_us):
                if p not in found_placeholders:
                    found_placeholders.append(p)

            correct_params_str = ";".join(found_placeholders)

            if current_params != correct_params_str:
                extracted_values[6] = correct_params_str
                formatted_values = []
                for v in extracted_values:
                    if v is None:
                        formatted_values.append("null")
                    else:
                        escaped = v.replace("'", "''")
                        formatted_values.append(f"'{escaped}'")

                new_line = f"INSERT INTO {table_name} ({columns_str}) VALUES ({', '.join(formatted_values)});\n"
                updated_content.append(new_line)
            else:
                updated_content.append(line)
        else:
            updated_content.append(line)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(updated_content)

    print(f"Successfully updated: {file_path}")

if __name__ == "__main__":
    update_sql_in_place('input.sql')