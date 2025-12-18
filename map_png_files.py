from pathlib import Path
import csv


def collect_png_paths(root_dir):
    """
    Walk through root_dir recursively and collect .png files.

    Returns
    -------
    dict
        {filename_without_extension: full_path_as_string}
    """
    png_dict = {}

    try:
        root = Path(root_dir).expanduser().resolve()
    except Exception as e:
        raise ValueError(f"Invalid root directory: {root_dir}") from e

    if not root.exists():
        raise FileNotFoundError(f"Directory does not exist: {root}")
    if not root.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {root}")

    try:
        for path in root.rglob("*.png"):
            try:
                key = path.stem
                value = str(path.resolve())

                if key in png_dict:
                    raise KeyError(f"Duplicate filename detected: {key}")

                png_dict[key] = value

            except Exception as e:
                print(f"Skipping file {path}: {e}")

    except PermissionError as e:
        raise PermissionError(f"Permission denied while accessing {root}") from e

    return png_dict


def append_png_paths_to_csv(
    input_csv,
    output_csv,
    png_dict,
    filename_field="file_name",
    new_field="file_path",
):
    """
    Read an existing CSV and append a new column containing the PNG file path
    when file_name matches a key in png_dict.

    Parameters
    ----------
    input_csv : str or Path
        Path to input CSV.
    output_csv : str or Path
        Path to write updated CSV.
    png_dict : dict
        {filename_without_extension: full_path}
    filename_field : str
        CSV field containing the PNG base filename.
    new_field : str
        Name of the new column to append.
    """
    input_csv = Path(input_csv)
    output_csv = Path(output_csv)

    if not input_csv.exists():
        raise FileNotFoundError(f"CSV not found: {input_csv}")

    with input_csv.open("r", newline="", encoding="utf-8") as f_in:
        reader = csv.DictReader(f_in)

        if filename_field not in reader.fieldnames:
            raise KeyError(f"Missing required column: {filename_field}")

        fieldnames = list(reader.fieldnames)
        if new_field not in fieldnames:
            fieldnames.append(new_field)

        rows = []
        for row in reader:
            key = row.get(filename_field)

            if key in png_dict:
                row[new_field] = png_dict[key]
            else:
                row[new_field] = None

            rows.append(row)

    with output_csv.open("w", newline="", encoding="utf-8") as f_out:
        writer = csv.DictWriter(f_out, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    root_directory = "/path/to/search"
    input_csv = "/path/to/input.csv"
    output_csv = "/path/to/output.csv"

    try:
        png_files = collect_png_paths(root_directory)
        append_png_paths_to_csv(
            input_csv=input_csv,
            output_csv=output_csv,
            png_dict=png_files,
        )
    except Exception as e:
        print(f"Error: {e}")
