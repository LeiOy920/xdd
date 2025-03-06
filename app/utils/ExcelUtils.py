import pandas as pd

def export_to_excel(sheet_name, columns, data):
    """
    Export data to an Excel file.

    :param file_name: The name of the output Excel file.
    :param sheet_name: The name of the sheet in the Excel file.
    :param columns: A list of column names.
    :param data: A list of tuples, where each tuple represents a row of data.
    """
    from io import BytesIO

    df = pd.DataFrame(data, columns=columns)
    output = BytesIO()
    df.to_excel(output, sheet_name=sheet_name, index=False)
    output.seek(0)
    return output

# Example usage
if __name__ == "__main__":
    columns = ['Name', 'Age', 'City']
    data = [
        ('Alice', 25, 'New York'),
        ('Bob', 30, 'Los Angeles'),
        ('Charlie', 35, 'Chicago')
    ]
    export_to_excel('output.xlsx', 'Sheet1', columns, data)