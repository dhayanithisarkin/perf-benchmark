from benchmark.utils import timerange_yesterday, timerange_daybeforeyesterday, get_timerange
from benchmark.output import convert_to_csv
from benchmark.query import Metric, validate_benchmark_run, Category, Process
import argparse
parser = argparse.ArgumentParser()

parser.add_argument("-did", type=str, help="did for wavefront", default="DP10XVX")
parser.add_argument("-w", "--window", type=int, help="Window of wavefront in days",default=1)
parser.add_argument("-cw", "--current_window", type=int, help="Current time of wavefront in days [0 for today, 1 for yesterday ans so on] [0 default]",default=0)
parser.add_argument("-bw", "--base_window", type=int, help="Baseline time of wavefront in days [0 for today, 1 for yesterday ans so on] [1 default]",default=1)

args = parser.parse_args()
did = args.did

print("Current stats from: (today-",args.current_window+args.window,") to (today-", args.current_window, ")")
print("Baseline stats from: (today-",args.base_window+args.window,") to (today-", args.base_window, ")")

# baseline_time = timerange_daybeforeyesterday()
# run_time = timerange_yesterday()
baseline_time = get_timerange(args.base_window+args.window,args.base_window)
run_time = get_timerange(args.current_window+args.window,args.current_window)

disk_util = Metric("disk utilization",
                   'avg(ts(dd.system.io.util, did="{}" and iid="*" and source="*" and role="platform" and device="dm-6"))'.format(did))
message_age = Metric("message age",
                     'avg(ts(dd.vRNI.GenericStreamTask.messageAge.mean, did="{}"))'.format(did))

# Grid metrics
program_time = Metric("Program time",
                      'mdiff(1h, sum(ts(dd.vRNI.GenericStreamTask.processorConsumption, did="{}"), pid))'.format(did))
metric_cache_miss_rate = Metric("Miss rate",
                                'mdiff(1h, avg(ts(dd.vRNI.CachedAlignedMetricStore.miss_300.count, did="{}"))) * 100 / mdiff(1h, avg(ts(dd.vRNI.CachedAlignedMetricStore.gets_300.count, did="{}")))'.format(did, did))
denorm_latency_by_ot = Metric("Denorm Latency By Object Type",
                              'avg(ts(dd.vRNI.DenormComputationProgram.latency.mean, did="{}"), ot)'.format(did))

# TODO: Add program_time to grid_metrics, denorm_latency_by_ot
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


# uptime metrics
uptime_metrics = []
for p in Process:
    m = Metric(p.sku() + '.' + p.process_name(),
               'avg(ts(dd.system.processes.run_time.avg, did="{}" and sku={} and process_name={}), iid)'.format(did, p.sku(), p.process_name()), compare_with='restart')
    m.category = Category.UPTIME
    uptime_metrics.append(m)


metrics = [disk_util, message_age]
metrics.extend(grid_metrics)
metrics.extend(indexer_metrics)
metrics.extend(uptime_metrics)

validation_results, uptime_results = validate_benchmark_run(metrics, baseline_time, run_time)
convert_to_csv(validation_results, uptime_results, './tmp/benchmark_result', './tmp/query_info.csv', './tmp/uptime_result.csv')
