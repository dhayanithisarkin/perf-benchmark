import csv
from benchmark.query import TaggedValidationResult


def convert_to_csv(results: [TaggedValidationResult], file_name):
    lines = []

    for result in results:
        # get the baseline stats into a dict form
        # so that lookups based on tag values can be performed
        # this will be a dict of tagvalue -> stats(percentiles)
        baseline_tag_to_stats = {}
        if result.baseline_stats is not None:
            for tagged_stats in result.baseline_stats:
                baseline_tag_to_stats[tagged_stats.tag] = tagged_stats.stats

        for tagged_stats in result.run_stats:
            tag = tagged_stats.tag or ''
            line = [
                result.metric.name + '.' + tag,
                result.metric.query,
                tagged_stats.stats['mean'],
                baseline_tag_to_stats[tag]['mean'],
                tagged_stats.stats['90%'],
                baseline_tag_to_stats[tag]['mean'],
            ]
            lines.append(line)

    with open(file_name, 'w') as writeFile:
        writer = csv.writer(writeFile)
        writer.writerows(lines)

    writeFile.close()
