from benchmark.utils import to_epoch_range
from benchmark.output import convert_to_csv
from benchmark.query import Metric, validate_benchmark_run, Category, Process, run_time_stats
import argparse
import datetime

current_time = datetime.datetime.now()
yesterdays_time = current_time - datetime.timedelta(days=1)
day_before_yesterdays_time = current_time - datetime.timedelta(days=2)

parser = argparse.ArgumentParser()

parser.add_argument("-did", type=str, help="did for wavefront", default="DPW74PQ")  # "DP10XVX")
# parser.add_argument("-w", "--window", type=int, help="Window of wavefront in days", default=1)
# parser.add_argument("-cw", "--current_window", type=int,
#                     help="Current time of wavefront in days [0 for today, 1 for yesterday ans so on] [0 default]",
#                     default=0)
# parser.add_argument("-bw", "--base_window", type=int,
#                     help="Baseline time of wavefront in days [0 for today, 1 for yesterday ans so on] [1 default]",
#                     default=1) .strftime("%Y-%m-%d-%H")
parser.add_argument("-cs", "--current-start", type=str, help="Start of Current Time Frame",
                    default=yesterdays_time.strftime("%Y-%m-%d-%H"))
parser.add_argument("-ce", "--current-end", type=str, help="End of Current Time Frame",
                    default=current_time.strftime("%Y-%m-%d-%H"))
parser.add_argument("-bs", "--base-start", type=str, help="Start of Base Time Frame",
                    default=day_before_yesterdays_time.strftime("%Y-%m-%d-%H"))
parser.add_argument("-be", "--base-end", type=str, help="End of Base Time Frame",
                    default=yesterdays_time.strftime("%Y-%m-%d-%H"))

args = parser.parse_args()
did = args.did
print("Current stats from:", args.current_start, "to", args.current_end)
print("Base stats from:", args.base_start, "to", args.base_end)
# baseline_time = timerange_daybeforeyesterday()
# run_time = timerange_yesterday()
run_time_stats.totol_current_time = (
            datetime.datetime.strptime(args.base_end, "%Y-%m-%d-%H") - datetime.datetime.strptime(args.base_start,
                                                                                                  "%Y-%m-%d-%H")).total_seconds();
run_time_stats.total_base_time = (
            datetime.datetime.strptime(args.current_end, "%Y-%m-%d-%H") - datetime.datetime.strptime(args.current_start,
                                                                                                     "%Y-%m-%d-%H")).total_seconds();

baseline_time = to_epoch_range(datetime.datetime.strptime(args.base_start, "%Y-%m-%d-%H"),
                               datetime.datetime.strptime(args.base_end, "%Y-%m-%d-%H"))
run_time = to_epoch_range(datetime.datetime.strptime(args.current_start, "%Y-%m-%d-%H"),
                          datetime.datetime.strptime(args.current_end, "%Y-%m-%d-%H"))

disk_util = Metric("disk utilization",
                   'avg(ts(dd.system.io.util, did="{}" and iid="*" and source="*" and role="platform" and device="dm-6"))'.format(
                       did), threshold=20)
message_age = Metric("message age",
                     'avg(ts(dd.vRNI.GenericStreamTask.messageAge.mean, did="{}"))'.format(did), threshold=20)
input_sdm = Metric("Input SDM", 'mdiff(1h, avg(ts(dd.vRNI.UploadHandler.sdm, did="{}"), sdm))'.format(did),
                   threshold=20)
# Grid metrics
program_time = Metric("Program time",
                      'mdiff(1h, avg(ts(dd.vRNI.GenericStreamTask.processorConsumption, did="{}"), pid))'.format(did),
                      threshold=20)
object_churn = Metric("Object Churn",
                      'mdiff(1h, sum(ts(dd.vRNI.ConfigStore.churn, did="{}"), ot, churn_type))'.format(did),
                      threshold=20)
metric_cache_miss_rate = Metric("Miss rate",
                                'mdiff(1h, avg(ts(dd.vRNI.CachedAlignedMetricStore.miss_300.count, did="{}"))) * 100 / mdiff(1h, avg(ts(dd.vRNI.CachedAlignedMetricStore.gets_300.count, did="{}")))'.format(
                                    did, did), threshold=20)
denorm_latency_by_ot = Metric("Denorm Latency By Object Type",
                              'avg(ts(dd.vRNI.DenormComputationProgram.latency.mean, did="{}"), ot)'.format(did),
                              threshold=20)

grid_metrics = [metric_cache_miss_rate, program_time, denorm_latency_by_ot, object_churn]
for metric in grid_metrics:
    metric.category = Category.GRID

# Indexer metrics
index_lag = Metric("Indexer Lag",
                   'ts(dd.vRNI.ConfigIndexerHelper.lag, did="{}")'.format(did), threshold=20)
indexed_docs_per_hour = Metric("Indexed docs per hour",
                               'mdiff(1h, ts(dd.vRNI.ConfigIndexerHelper.indexCount, did="{}"))'.format(did),
                               threshold=20)
es_heap_usage = Metric("ES Heap usage",
                       'avg(ts(dd.jvm.mem.heap_used, did="{}"))'.format(did), threshold=20)
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
               'avg(ts(dd.system.processes.run_time.avg, did="{}" and sku={} and process_name={}), iid)'.format(did,
                                                                                                                p.sku(),
                                                                                                                p.process_name()),
               compare_with='restart', threshold=20)
    m.category = Category.UPTIME
    uptime_metrics.append(m)

metrics = [disk_util, message_age, input_sdm]
metrics.extend(grid_metrics)
metrics.extend(indexer_metrics)
metrics.extend(uptime_metrics)

validation_results, uptime_results = validate_benchmark_run(metrics, baseline_time, run_time)
convert_to_csv(validation_results, uptime_results, './tmp/benchmark_result', './tmp/query_info.csv',
               './tmp/uptime_result.csv')
