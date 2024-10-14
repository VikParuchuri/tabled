import json
import argparse

import click


@click.command()
@click.argument("file_path", type=str)
def verify_table_scores(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)

    avg = sum([r["score"] for r in data]) / len(data)
    if avg < 0.7:
        raise ValueError("Average score is below the required threshold of 0.7")


if __name__ == "__main__":
    verify_table_scores()
