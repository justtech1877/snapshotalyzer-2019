import boto3
import botocore
import click

session = boto3.Session(profile_name='boto3user')
ec2 = session.resource('ec2')

#Function helper to filter EC2 instances
def filter_instances(project):
    instances = []

    if project:
        filters = [{'Name':'tag:Project', 'Values':[project]}]
        instances = ec2.instances.filter(Filters=filters)
    else:
        instances = ec2.instances.all()

    return instances

#Function helper to list volume snapshots in pending state
def has_pending_snapshots(volume):
    snapshots = list(volume.snapshots.all())
    return snapshots and snapshots[0].state == 'pending'

@click.group()
def cli():
    """Shotty manages EC2 volume snapshots"""

@cli.group('snapshots')
def snapshots():
    """Commands for EC2 volume snapshots"""

@snapshots.command('list')
@click.option('--project', default=None,
    help="Only snapshots for project (tag Project:<name>)")
@click.option('--all', 'list_all', default=False, is_flag=True,
    help="List all snapshots for each volume, not just the most recent")
def list_snapshots(project, list_all):
    "List EC2 volume snapshots"

    instances = filter_instances(project)

    for i in instances:
        for v in i.volumes.all():
            for s in v.snapshots.all():
                print(", ".join((
                    s.id,
                    v.id,
                    i.id,
                    s.state,
                    s.progress,
                    s.start_time.strftime("%c")
                    )))

                if s.state == 'completed' and not list_all:
                    break

    return

@cli.group('volumes')
def volumes():
    """Commands for EC2 volumes"""

@volumes.command('list')
@click.option('--project', default=None,
    help="Only volumes for project (tag Project:<name>)")
def list_volumes(project):
    "List EC2 volumes"

    instances = filter_instances(project)

    for i in instances:
        for v in i.volumes.all():
            print(", ".join((
                v.id,
                i.id,
                v.state,
                str(v.size) + "GiB",
                v.encrypted and "Encrypted" or "Not Encrypted"
                )))

    return

@cli.group('instances')
def instances():
    """Commands for EC2 instances"""

@instances.command('snapshot',
    help="Create snapshots of available volumes")
@click.option('--project', default=None,
    help="Only instances for project (tag Project:<name>)")
def create_snapshots(project):
    "Create snapshots for EC2 instances"

    instances = filter_instances(project)

    for i in instances:
        print("Stopping {0}...".format(i.id))

        i.stop()
        i.wait_until_stopped()

        for v in i.volumes.all():
            if has_pending_snapshots(v):
                print(" Skipping {0}, snapshot already in progress".format(v.id))
                continue

            print("Creating snapshot of {0}...".format(v.id))
            v.create_snapshot(Description="Created by SnapshotAlyzer-2019")

        print("Starting {0}...".format(i.id))

        i.start()
        i.wait_until_running()

    print("Job's completed!")

    return


@instances.command('list')
@click.option('--project', default=None,
    help="Only instances for project (tag Project:<name>)")
def list_instances(project):
    "List EC2 instances"

    instances = filter_instances(project)

    for i in instances:
        tags = { t['Key']: t['Value'] for t in i.tags or [] }
        print(", ".join((
            i.id,
            i.instance_type,
            i.placement['AvailabilityZone'],
            i.state['Name'],
            i.public_dns_name,
            tags.get('Project', '<no project>')
            )))

    return

@instances.command('stop')
@click.option('--project', default=None,
    help='Only instances for project')
@click.option('--force', default=False, is_flag=True,
    help='Forces instance stop')
def stop_instances(project, force):
    "Stop EC2 instances"

    instances = filter_instances(project)

    for i in instances:
        print("Stopping {0}...".format(i.id))

        if project:
            try:
                i.stop()
            except botocore.exceptions.ClientError as e:
                print("Could not stop {0}. ".format(i.id) + str(e))
                #continue
        elif force:
             try:
                i.stop(--force)
             except botocore.exceptions.ClientError as e:
                print("Could not stop {0}. ".format(i.id) + str(e))

        else: print("Error: the --project or --force flags must be set")

        continue

    return

@instances.command('start')
@click.option('--project', default=None,
    help='Only instances for project')
@click.option('--force', default=False, is_flag=True,
    help='Forces instance start')
def start_instances(project, force):
    "Start EC2 instances"

    instances = filter_instances(project)

    for i in instances:
        print("Starting {0}...".format(i.id))

        if project:
            try:
                i.start()
            except botocore.exceptions.ClientError as e:
                print("Could not start {0}. ".format(i.id) + str(e))
                #continue

        elif force:
          try:
             i.start(--force)
          except botocore.exceptions.ClientError as e:
             print("Could not start {0}. ".format(i.id) + str(e))

        else: print("Error: the --project or --force flags must be set")

        continue

    return

@instances.command('reboot')
@click.option('--project', default=None,
    help='Only instances for project')
@click.option('--force', default=False, is_flag=True,
    help='Forces instance start')
def reboot_instances(project, force):
    "Reboot EC2 instances"

    instances = filter_instances(project)

    for i in instances:
        print("Rebooting {0}...".format(i.id))
        if project:
            try:
                i.reboot()
            except botocore.exceptions.ClientError as e:
                print("Could not start {0}. ".format(i.id) + str(e))
                #continue

        elif force:
            try:
                i.reboot(--force)
            except botocore.exceptions.ClientError as e:
                print("Could not reboot {0}. ".format(i.id) + str(e))

        else: print("Error: the --project or --force flags must be set")

        continue

    return

if __name__ == '__main__':
    cli()
