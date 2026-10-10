"""
For comparing the OCR outputs given different runs of the system.
Mostly written by Github Copilot, with edits by Sally.
"""
import os
import tkinter as tk
from tkinter import filedialog


def choose_four_text_files():
    root = tk.Tk()
    root.withdraw()
    paths = filedialog.askopenfilenames(
        title="Select 4 text files to compare",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
    )
    root.destroy()

    selected = list(paths)
    if len(selected) != 4:
        raise ValueError("Please select exactly 4 text files.")
    return selected


def read_file_lines(path):
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read().splitlines()

def compare_letter_by_letter(str1, str2):
    max_length = max(len(str1), len(str2))
    differences1 = 0
    differences2 = 0
    for i in range(max_length):
        char1 = str1[i] if i < len(str1) else "<missing>"
        char2 = str2[i] if i < len(str2) else "<missing>"
        if char1 != char2:
            differences1 += 1
    if len(str1) == len(str2):
        return f"{differences1}/{max_length} differences"
    return f"maybe {abs(len(str1)-len(str2))} differences"
    
"""     for i in range(1, max_length):
        char1 = str1[(i*-1)] if i <= len(str1) else "<missing>"
        char2 = str2[(i*-1)] if i <= len(str2) else "<missing>"
        if char1 != char2:
            differences2 += 1
    if max_length -(differences1+differences2) == abs(len(str1)-len(str2)):
        return f"{(max_length-(differences1+differences2))}/{max_length} differences"
    return f"Complicated number of differences ({differences1} vs {differences2}) in strings of length {len(str1)} and {len(str2)}"
 """
def compare_line_by_line(file_paths):
    file_lines = [read_file_lines(path) for path in file_paths]
    max_lines = max(len(lines) for lines in file_lines)
    print("Total number of lines:", max_lines)
    differences = []
    for index in range(max_lines):
        values = []
        for lines in file_lines:
            values.append(lines[index] if index < len(lines) else "<missing>")

        if len(set(values)) > 1:
            #do as I say, not as I do (don't name variables like this)
            whoozum1 = compare_letter_by_letter(values[0], values[1])
            whoozum2 = compare_letter_by_letter(values[1], values[2])
            whoozum3 = compare_letter_by_letter(values[2], values[3])
            whoozum4 = compare_letter_by_letter(values[3], values[0])
            whoozum5 = compare_letter_by_letter(values[0], values[2])
            whoozum6 = compare_letter_by_letter(values[1], values[3])
            values.append(f"1 and 2: {whoozum1}, 1 and 3: {whoozum5}, 1 and 4: {whoozum4}, 2 and 3: {whoozum2}, 2 and 4: {whoozum6}, 3 and 4: {whoozum3}")
            differences.append((index + 1, values))

    return differences


def main():
    try:
        file_paths = choose_four_text_files()
    except ValueError as e:
        print(e)
        return

    print("Selected files:")
    for path in file_paths:
        print(f"- {os.path.basename(path)}: {path}")

    diffs = compare_line_by_line(file_paths)

    if not diffs:
        print("\nAll 4 files match line by line.")
        return
    print(len(diffs), "differences found.")
    print("\nDifferences found:")
    for line_number, values in diffs:
        print(f"\nLine {line_number}:")
        for i, value in enumerate(values):
            if i < 4:
                label = os.path.basename(file_paths[i])
            else:
                label = "Differences"
            print(f"  {label}: {value}")


if __name__ == "__main__":
    main()
