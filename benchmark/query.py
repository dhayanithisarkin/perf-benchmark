from __future__ import print_function
import wavefront_api_client
from wavefront_api_client.rest import ApiException
from benchmark.utils import response_tostats
from enum import Enum


prod_config = wavefront_api_client.Configuration()
prod_config.host = "https://varca.wavefront.com"
prod_config.api_key['X-AUTH-TOKEN'] = '10a79735-3ed2-4cbd-bb3b-5ddecf2a06f7'

test_config = wavefront_api_client.Configuration()
test_config.host = "https://xyz.wavefront.com"
test_config.api_key['X-AUTH-TOKEN'] = 'TODO-FILL-THIS'

# create an instance of the API class
did = 'DP8SZFH'  # Homedepot
prod_api_instance = wavefront_api_client.QueryApi(wavefront_api_client.ApiClient(prod_config))


# Priority of metrics. High priority metric breaches will
# be highlighted first
class Priority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3


# Various metric categories present in the system
class Category(Enum):
    UNKNOWN = 1
    SYSTEM = 2
    GRID = 3
    INDEXER = 4
    REST_API = 5


# Class to define a metric object
class Metric:
    def __init__(self, name, query):
        """
        :param name: The name of the metric (e.g: Average message age)
        :param query: The wavefront query used to get the metric time series.
        """
        self.name = name
        self.query = query
        self.priority = Priority.LOW
        self.category = Category.UNKNOWN

    def set_priority(self, priority):
        self.priority = priority

    def set_category(self, category):
        self.category = category


class TaggedStats:
    def __init__(self, tag, percentile_stats):
        self.tag = tag
        self.stats = percentile_stats


class TaggedValidationResult:
    def __init__(self, metric, tagged_stats):
        self.metric = metric
        self.run_stats = tagged_stats
        self.baseline_stats = None

    def set_baseline_stats(self, baseline_stats):
        self.baseline_stats = baseline_stats


def validate_benchmark_run(
        metrics,
        run_timerange,
        baseline_timerange=None,
):
    """
    :param metrics: List of Metric objects
    :param run_timerange: (start, end) timestamps for the current run
    :param baseline_timerange: (start, end) timestamps for the baseline run.
    :return: list of ValidationResult objects
    """
    validation_results = []
    for metric in metrics:
        current_run_response = query_wf(metric.query, run_timerange)
        current_run_stats = response_tostats(current_run_response, stats)
        result = TaggedValidationResult(metric, current_run_stats)

        if baseline_timerange:
            baseline_response = query_wf(metric.query, baseline_timerange)
            baseline_stats = response_tostats(baseline_response, stats)
            result.set_baseline_stats(baseline_stats)

        validation_results.append(result)
    return validation_results


def query_wf(
        query_str,
        time_range,
):
    """
    Query wavefront and return query results
    :param query_str: The wavefront query string
    :param time_range: Tuple of (start, end) timestamps
    :return: Query results
    """
    start_time = time_range[0]
    end_time = time_range[1]

    granularity = 'h'  # minutely granularity
    try:
        # Perform a charting query against Wavefront servers that
        # returns the appropriate points in the specified time window and granularity
        api_response = prod_api_instance.query_api(
            q=query_str, s=start_time, g=granularity, e=end_time,
            i=True, auto_events=False, summarization='MEAN',
            list_mode=True, strict=True, include_obsolete_metrics=False,
            sorted=False, cached=True)
        return api_response
    except ApiException as e:
        print("Exception when calling QueryApi->query_api: %s\n" % e)


# Returns stats as a pandas series
# The keys of the series are count,
# mean, std, min, 10%, 25%, 50%, 75%, 90% 95%, max
def stats(df, tag=None):
    """
    :param tag: The tag value of the timeseries or None if there is no tag
    :param df: dataframe containing the timeseries(time, values)
    :return: percentiles and min and max
    """
    percentiles = df['value'].describe(
        percentiles=[0.10, 0.25, 0.5, 0.75, 0.9, 0.95])
    return TaggedStats(tag, percentiles)
