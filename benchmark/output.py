import csv
from benchmark.query import TaggedValidationResult


def convert_to_csv(results: [TaggedValidationResult], file_name):
    lines = []

    for result in results:
        metric = result.metric

        for tag, change_result in result.tag_to_change_results.items():
            line = [
                metric.name + '.' + (tag or ''),
                metric.query,
                change_result.baseline_value,
                change_result.current_value,
                'FAILED' if change_result.is_failure else 'PASSED'
            ]
            lines.append(line)

    with open(file_name, 'w') as writeFile:
        writer = csv.writer(writeFile)
        writer.writerows(lines)

    writeFile.close()
