import os


def get_mounted_fs():
    with open('/proc/mounts') as f:
        content = f.read().splitlines()
    return [tuple(fs.split()) for fs in content]


def fs_is_valid(fs):
    """
    fs - tuple containing mounted filesystem information
    """
    invalid_fs_type = [
        'autofs', 'cgroup', 'cgroup2', 'configfs', 'debugfs', 'devpts',
        'devtmpfs', 'efivarfs', 'fusectl', 'fuse.gvfsd-fuse', 'hugetlbfs',
        'mqueue', 'overlay', 'proc', 'pstore', 'securityfs', 'sysfs', 'tmpfs'
    ]
    if fs[2] not in invalid_fs_type and os.path.isdir(fs[1]):
        return True
    else:
        return False


def get_valid_mountpoints():
    valid_fs = filter(fs_is_valid, get_mounted_fs())
    return [fs for fs in valid_fs]


def get_fsdetails(fs):
    fs = {
            'mountpoint': fs[1],
            'device': fs[0],
            'fstype': fs[2]
            }
    fs_stat = os.statvfs(fs['mountpoint'])
    fs['size'] = fs_stat.f_bsize * fs_stat.f_blocks
    fs['free'] = fs_stat.f_bsize * fs_stat.f_bfree
    return fs

