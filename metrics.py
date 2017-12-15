from prometheus_client import Gauge
from prometheus_client.exposition import generate_latest
from lib.kubernetes import get_volumes_information
from lib.filesystem import get_fs_info
from pytz import utc
from apscheduler.schedulers.background import BackgroundScheduler


volume_info = get_volumes_information()
scheduler = BackgroundScheduler(timezone=utc)
metric_labels = {
    'namespace': volume_info['pod_info']['pod_namespace'],
    'pod': volume_info['pod_info']['pod_name'],
    'mount_point': None,
    'volume_name': None,
    'device': None,
    'fstype': None
}
if volume_info['labels']:
    metric_labels.update(volume_info['labels'])

metrics = {
    'mounted': Gauge('kube_vol_mounted', 'volume is mounted', metric_labels),
    'size': Gauge('kube_vol_size', 'volume is mounted', metric_labels),
    'free': Gauge('kube_vol_free', 'volume is mounted', metric_labels)
}


@scheduler.scheduled_job('interval', seconds=5)
def update_metrics():
    fs_details = get_fs_info()
    mounted_volumes = volume_info['mounted_volumes']
    mounted_volumes_names = []
    for vol in mounted_volumes:
        for vname in vol.keys():
            mounted_volumes_names.append(vname)
    for volume in volume_info['persistent_volumes']:
        volume_labels = metric_labels.copy()
        volume_labels['volume_name'] = volume
        if volume not in mounted_volumes_names:
            metrics['mounted'].labels(**volume_labels).set(0)
        else:
            volume_labels['mount_point'] = [m[volume]
                                            for m in mounted_volumes][0]
            fs = [fs for fs in fs_details if fs['mountpoint'] ==
                  volume_labels['mount_point']][0]
            volume_labels['device'] = fs['device']
            volume_labels['fstype'] = fs['fstype']
            metrics['mounted'].labels(**volume_labels).set(1)
            metrics['size'].labels(**volume_labels).set(fs['size'])
            metrics['free'].labels(**volume_labels).set(fs['free'])


def latest_data():
    return generate_latest()
