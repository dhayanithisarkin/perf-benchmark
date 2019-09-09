from benchmark.utils import to_epoch_range
from benchmark.output import convert_to_csv
from benchmark.query import Metric, validate_benchmark_run, Category, Process, RuntimeObjects
import argparse
import datetime

current_time = datetime.datetime.now()
yesterdays_time = current_time - datetime.timedelta(days=1)
day_before_yesterdays_time = current_time - datetime.timedelta(days=2)

parser = argparse.ArgumentParser()

parser.add_argument("-did", type=str, help="did for wavefront", default="DPW74PQ")  # "DP10XVX")
parser.add_argument("-se","--symphony-env", type=str, help="Environment for symphony wavefront", default="jazz")  # "DP10XVX")
parser.add_argument("-cs", "--current-start", type=str, help="Start of Current Time Frame(UTC)",
                    default=yesterdays_time.strftime("%Y-%m-%d-%H"))
parser.add_argument("-ce", "--current-end", type=str, help="End of Current Time Frame(UTC)",
                    default=current_time.strftime("%Y-%m-%d-%H"))
parser.add_argument("-bs", "--base-start", type=str, help="Start of Base Time Frame(UTC)",
                    default=day_before_yesterdays_time.strftime("%Y-%m-%d-%H"))
parser.add_argument("-be", "--base-end", type=str, help="End of Base Time Frame(UTC)",
                    default=yesterdays_time.strftime("%Y-%m-%d-%H"))

args = parser.parse_args()
did = args.did
environment = args.symphony_env
info = "For DID = " + did + " and Environment = " + environment + "\n"
info += "Current stats from: " + args.current_start + " to " + args.current_end + "\n"
info += "Base stats from: " + args.base_start + " to " + args.base_end + "\n"

RuntimeObjects.info = info
print(info)
# baseline_time = timerange_daybeforeyesterday()
# run_time = timerange_yesterday()
RuntimeObjects.total_current_time = (
        datetime.datetime.strptime(args.base_end, "%Y-%m-%d-%H") - datetime.datetime.strptime(args.base_start,
                                                                                              "%Y-%m-%d-%H")).total_seconds();
RuntimeObjects.total_base_time = (
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
                      threshold=20, category=Category.GRID)
object_churn = Metric("Object Churn",
                      'mdiff(1h, sum(ts(dd.vRNI.ConfigStore.churn, did="{}"), ot, churn_type))'.format(did),
                      threshold=20, category=Category.GRID)
metric_cache_miss_rate = Metric("Miss rate",
                                'mdiff(1h, avg(ts(dd.vRNI.CachedAlignedMetricStore.miss_300.count, did="{}"))) * 100 / mdiff(1h, avg(ts(dd.vRNI.CachedAlignedMetricStore.gets_300.count, did="{}")))'.format(
                                    did, did), threshold=20, category=Category.GRID)
denorm_latency_by_ot = Metric("Denorm Latency By Object Type",
                              'avg(ts(dd.vRNI.DenormComputationProgram.latency.mean, did="{}"), ot)'.format(did),
                              threshold=20, category=Category.GRID)

grid_metrics = [metric_cache_miss_rate, program_time, denorm_latency_by_ot, object_churn]

# Indexer metrics
index_lag = Metric("Indexer Lag",
                   'time()*1000 - ts(dd.vRNI.ConfigIndexerHelper.bookmark, did="{}")'.format(did), threshold=20,
                   category=Category.INDEXER)
indexed_docs_per_hour = Metric("Indexed docs per hour",
                               'mdiff(1h, ts(dd.vRNI.ConfigIndexerHelper.indexCount, did="{}"))'.format(did),
                               threshold=20, category=Category.INDEXER)
es_heap_usage_avg = Metric("ES Heap usage (Average)",
                           'avg(ts(dd.jvm.mem.heap_used, did="{}"))'.format(did), threshold=20,
                           category=Category.INDEXER)
es_heap_usage_max = Metric("ES Heap usage (Max)",
                           'max(ts(dd.jvm.mem.heap_used, did="{}"))'.format(did), compare_with='max', threshold=20,
                           category=Category.INDEXER)
indexer_metrics = [
    index_lag,
    indexed_docs_per_hour,
    es_heap_usage_avg,
    es_heap_usage_max]

# uptime metrics
uptime_metrics = []
for p in Process:
    m = Metric(p.sku() + '.' + p.process_name(),
               'avg(ts(dd.system.processes.run_time.avg, did="{}" and sku={} and process_name={}), iid)'.format(did,
                                                                                                                p.sku(),
                                                                                                                p.process_name()),
               compare_with='restart', threshold=20, category=Category.UPTIME)
    uptime_metrics.append(m)

# Symphony Metrics
symphony_metrics = []

ui_response_time = Metric("UI Response Time", "ts(scaleperf.vrni.ui.responsetime, environment={})".format(environment),
                          category=Category.SYMPHONY, wavefront="symphony")

symphony_metrics.append(ui_response_time)

metrics = [disk_util, message_age, input_sdm]
metrics.extend(symphony_metrics)
metrics.extend(grid_metrics)
metrics.extend(indexer_metrics)
metrics.extend(uptime_metrics)

validation_results, uptime_results = validate_benchmark_run(metrics, run_time, baseline_time)
convert_to_csv(validation_results, uptime_results)
