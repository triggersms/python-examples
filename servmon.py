#!/usr/bin/env python

# Monitor linux server resources

import os
import triggersms


def get_disk_mounts():
    disk_mounts = []
    # Common non-disk filesystems to exclude
    exclude = {'tmpfs', 'devtmpfs', 'proc', 'sysfs', 'cgroup', 'cgroup2', 'pstore', 'securityfs', 'debugfs', 'mqueue', 'hugetlbfs', 'configfs', 'fusectl', 'fuse.lxcfs', 'overlay', 'ramfs', 'autofs', 'binfmt_misc', 'rpc_pipefs', 'nfsd', 'devpts'}

    with open('/proc/mounts', 'r') as f:
        for line in f:
            parts = line.split()
            if len(parts) < 3:
                continue
            device, mountpoint, fstype = parts[:3]
            if fstype not in exclude and device.startswith('/dev/'):
                disk_mounts.append(mountpoint)
    return disk_mounts

def get_ram_used_pct():
    os_free = os.popen('free -m').readlines()
    os_free_header = os_free[0].split()
    if os_free_header[-1] == 'available':
        # new version of free
        os_free_1 = os_free[1].split()
        ram_total = os_free_1[1]
        ram_avail = os_free_1[-1]
        return 1.0 - float(ram_avail)/float(ram_total)
    else:
        # old version of free
        # probably 3.2.8 but anything less than 3.3.10
        # will probably work
        os_free_1 = os_free[1].split()
        os_free_2 = os_free[2].split()
        ram_total = os_free_1[1]
        ram_used = os_free_2[2]
        return float(ram_used)/float(ram_total)

def get_disk_used_pct(path='/'):
    statvfs = os.statvfs(path)
    fs_size = statvfs.f_frsize * statvfs.f_blocks
    fs_avail = statvfs.f_frsize * statvfs.f_bavail
    return 1.0 - float(fs_avail)/float(fs_size)


samples = [{'rule': '001', 'name': 'ram', 'value': get_ram_used_pct()}] + \
          [{'rule': '001', 'name': mount, 'value': get_disk_used_pct(mount)} for mount in get_disk_mounts()]

triggersms.post(
    trigger_id = triggersms.get_trigger_id(),
    trigger_name = triggersms.get_trigger_name(),
    samples = samples
)
