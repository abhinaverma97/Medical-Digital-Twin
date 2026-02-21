import csv

def export_csv(matrix, path):
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=matrix[0].keys())
        writer.writeheader()
        writer.writerows(matrix)