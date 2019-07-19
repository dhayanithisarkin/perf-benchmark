import csv
from benchmark.query import TaggedValidationResult
from benchmark.query import TaggedValidationResultUptime


def convert_to_csv(validation_results: [TaggedValidationResult], uptime_results:[TaggedValidationResultUptime], benchmark_result, query_info, uptimeinfo):
    validation_lines = []
    uptime_lines = []
    count = 0
    lst = []
    for result in validation_results:
        metric = result.metric

        for tag, change_result in result.tag_to_change_results.items():
            line = [
                metric.name + '.' + (tag or ''),
                change_result.baseline_value,
                change_result.current_value,
                'FAILED' if change_result.is_failure else 'PASSED'
            ]
            lst.append([count, metric.query])
            count+=1
            validation_lines.append(line)

    for result in uptime_results:
        metric = result.metric

        for tag, change_result in result.tag_to_change_results.items():
            line = [
                metric.name + '.' + (tag or ''),
                change_result.current_value,
                'FAILED' if change_result.is_failure else 'PASSED'
            ]
            uptime_lines.append(line)


    with open(benchmark_result, 'w') as writeFile:
        writer = csv.writer(writeFile,delimiter=':')
        writer.writerows(validation_lines)

    writeFile.close()
    with open(uptimeinfo, 'w') as writeFile:
        writer = csv.writer(writeFile,delimiter=':')
        writer.writerows(uptime_lines)

    writeFile.close()
    with open(query_info, 'w') as writeFile:
        writer = csv.writer(writeFile,delimiter=':')
        writer.writerows(lst)

    writeFile.close()
