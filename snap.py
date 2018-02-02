import boto3
import collections
import datetime
ec2 = boto3.client('ec2',region_name='us-east-1')

def lambda_handler(event, context):
        reservations = ec2.describe_volumes( Filters=[ {'Name': 'tag-key', 'Values': ['backup', 'True']} ] )
      
        for volume in reservations['Volumes']:
                print "Backing up %s in %s" % (volume['VolumeId'], volume['AvailabilityZone'])

                # Create snapshot
                reservations = ec2.create_snapshot(VolumeId=volume['VolumeId'],Description="Lambda backup for ebs" + volume['VolumeId'])

                result = reservations['SnapshotId']
                print(result)

                ec2.create_tags(
                Resources=[result],Tags=[
                {'Key': 'Name', 'Value': 'snapshot' },
                ]
                )

        reservations = ec2.describe_snapshots(Filters=[ {'Name': 'tag-key', 'Values': ['Name', 'snapshot']}], OwnerIds=['self'] )
        #print(reservations)
        # get the time
        now = datetime.datetime.today().strftime('%Y%m%d')
        #print now
        current = int(now)
        retention = 1
        for snapshot in reservations['Snapshots']:
                print "Checking snapshot %s which was created on %s" % (snapshot['SnapshotId'],snapshot['StartTime'])

                # Remove timezone info from snapshot in order for comparison
                x = snapshot['StartTime'].strftime('%Y%m%d')
                #print(x)
                snaptime = int(x)
                #print snaptime
                z = current - snaptime
                #print z
                if z > retention:
                        print "The snapshot older than One day. Deleting Now"
                        ec2.delete_snapshot(SnapshotId= snapshot['SnapshotId'])

                else:
                        print "Snapshot is newer than configured retention of %d days so we keep it" % (retention)
