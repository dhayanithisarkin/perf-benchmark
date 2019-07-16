import csv
from benchmark.query import TaggedValidationResult


def convert_to_csv(results: [TaggedValidationResult], benchmark_result, query_info):
    lines = []
    count = 0
    lst = []
    for result in results:
        metric = result.metric

        for tag, change_result in result.tag_to_change_results.items():
            line = [
                count,
                metric.name + '.' + (tag or ''),
                change_result.baseline_value,
                change_result.current_value,
                'FAILED' if change_result.is_failure else 'PASSED'
            ]
            lst.append([count, metric.query])
            count+=1
            lines.append(line)

    with open(benchmark_result, 'w') as writeFile:
        writer = csv.writer(writeFile,delimiter=':')
        writer.writerows(lines)

    writeFile.close()
    with open(query_info, 'w') as writeFile:
        writer = csv.writer(writeFile,delimiter=':')
        writer.writerows(lst)

    writeFile.close()
