from kubernetes import config, client
import sys
import os
import logging


try:
    me = {
            'pod_name': os.environ['POD_NAME'],
            'pod_namespace': os.environ['POD_NAMESPACE']
            }
except KeyError:
    logging.fatal('POD_NAME and POD_NAMESPACE not defined')
    sys.exit(1)


config.load_incluster_config()
corev1 = client.CoreV1Api()


def get_pod():
    """return the current pod"""
    pod = corev1.read_namespaced_pod(me['pod_name'], me['pod_namespace'])
    return pod


def get_container_name(pod):
    with open('/proc/self/cgroup') as f:
        container_id = f.readline().splitlines()[0].split('/')[-1]
    container_name = [c.name for c in pod.status.container_statuses
                      if c.container_id == f'docker://{container_id}'][0]
    return container_name


def get_real_volumes(pod):
    """
    function to return if a volume is a real persistent volume
    pod is a kubernetes pod
    """
    volumes = pod.spec.volumes
    real_volumes = filter(is_real_volume, volumes)
    return [v.name for v in real_volumes]


def get_mounted_volumes(pod, container_name):
    c = [c for c in pod.spec.containers if c.name == container_name][0]
    mounts = c.volume_mounts
    mounted_volumes = [{x.name: x.mount_path for x in mounts}]
    return mounted_volumes


def is_real_volume(volume):
    FAKE_VOLUMES = set([
        'config_map',
        'downward_api',
        'projected',
        'secret'
        ])
    vd = volume.to_dict()
    vtype = set([
        x for x in vd.keys()
        if x is not 'name' and vd[x] is not None
        ])
    return not vtype.issubset(FAKE_VOLUMES)


def get_volumes_information():
    pod = get_pod()
    container_name = get_container_name(pod)
    pod_volumes = get_real_volumes(pod)
    mounted_volumes = get_mounted_volumes(pod, container_name)
    volume_info = {
           'persistent_volumes': pod_volumes,
           'mounted_volumes': mounted_volumes,
           'pod_info': me,
           'labels': pod.metadata.labels
           }
    return volume_info



