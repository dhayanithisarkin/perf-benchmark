from benchmark.query import Metric, validate_benchmark_run, Category
from benchmark.utils import timerange_yesterday, timerange_daybeforeyesterday
from benchmark.output import convert_to_csv

did = 'DP8SZFH'  # Homedepot

baseline_time = timerange_daybeforeyesterday()
run_time = timerange_yesterday()

disk_util = Metric("disk utilization",
                   'avg(ts(dd.system.io.util, did="{}" and iid="*" and source="*" and role="platform" and device="dm-6"))'.format(did))
message_age = Metric("message age",
                     'avg(ts(dd.vRNI.GenericStreamTask.messageAge.mean, did="{}"))'.format(did))

# Grid metrics
program_time = Metric("Program time",
                      'mdiff(1h, sum(ts(dd.vRNI.GenericStreamTask.processorConsumption, did="{}"), pid))'.format(did))
metric_cache_miss_rate = Metric("Miss rate",
                                'mdiff(1h, avg(ts(dd.vRNI.CachedAlignedMetricStore.miss_300.count, did="{}"))) * 100 / mdiff(1h, avg(ts(dd.vRNI.CachedAlignedMetricStore.gets_300.count, did="{}")))'.format(did, did))
grid_metrics = [metric_cache_miss_rate]
for metric in grid_metrics:
    metric.category = Category.GRID

# Indexer metrics
index_lag = Metric("Indexer Lag",
                   'ts(dd.vRNI.ConfigIndexerHelper.lag, did="{}")'.format(did))
indexed_docs_per_hour = Metric("Indexed docs per hour",
                               'mdiff(1h, ts(dd.vRNI.ConfigIndexerHelper.indexCount, did="{}"))'.format(did))
es_heap_usage = Metric("ES Heap usage",
                       'avg(ts(dd.jvm.mem.heap_used, did="{}"))'.format(did))
indexer_metrics = [
    index_lag,
    indexed_docs_per_hour,
    es_heap_usage]
for metric in indexer_metrics:
    metric.category = Category.INDEXER


metrics = [disk_util, message_age]
metrics.extend(grid_metrics)
metrics.extend(indexer_metrics)

results = validate_benchmark_run(metrics, baseline_time, run_time)
convert_to_csv(results, '/tmp/perf_benchmark.csv')

