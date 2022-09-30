import json
import io
from datetime import datetime

test_filesystem_id = 'fs-01234567'

test_stack_name = f'testStackPrefix-ManagedResources-{test_filesystem_id}'

ec2_describe_security_group_rules_response = {
	'SecurityGroupRules': [{
		'SecurityGroupRuleId': 'sgr-0123abc',
		'GroupId': 'sg-4567abcd',
		'GroupOwnerId': '',
		'IsEgress': False,
		'IpProtocol': '-1',
		'FromPort': -1,
		'ToPort': -1,
		'ReferencedGroupInfo': {
			'GroupId': 'sg-4567abcd',
			'UserId': ''
		},
		'Tags': []
	}, {
		'SecurityGroupRuleId': 'sgr-0123abc',
		'GroupId': 'sg-4567abcd',
		'GroupOwnerId': '',
		'IsEgress': False,
		'IpProtocol': 'tcp',
		'FromPort': 2049,
		'ToPort': 2049,
		'ReferencedGroupInfo': {
			'GroupId': 'sg-4567abcd',
			'UserId': ''
		},
		'Tags': []
	}, {
		'SecurityGroupRuleId': 'sgr-0123abc',
		'GroupId': 'sg-4567abcd',
		'GroupOwnerId': '',
		'IsEgress': True,
		'IpProtocol': '-1',
		'FromPort': -1,
		'ToPort': -1,
		'CidrIpv4': '0.0.0.0/0',
		'Tags': []
	},
    {
		'SecurityGroupRuleId': 'sgr-0123abc',
		'GroupId': 'sg-4567abcd',
		'GroupOwnerId': '',
		'IsEgress': False,
		'IpProtocol': '-1',
		'FromPort': -1,
		'ToPort': -1,
		'CidrIpv4': '0.0.0.0/0',
		'Tags': []
	}
    ],
	'ResponseMetadata': {
		'RequestId': '',
		'HTTPStatusCode': 200,
		'HTTPHeaders': {
			'x-amzn-requestid': '',
			'cache-control': 'no-cache, no-store',
			'strict-transport-security': 'max-age=31536000; includeSubDomains',
			'vary': 'accept-encoding',
			'content-type': 'text/xml;charset=UTF-8',
			'transfer-encoding': 'chunked',
			'date': 'Wed, 21 Sep 2022 20:02:50 GMT',
			'server': 'AmazonEC2'
		},
		'RetryAttempts': 0
	}
}

efs_describe_file_systems_no_marker_response = {
    'FileSystems': [
        {
            'CreationTime': datetime.now(),
            'CreationToken': 'tokenstring',
            'FileSystemId': f'{test_filesystem_id}',
            'LifeCycleState': 'available',
            'Name': 'MyFileSystem',
            'NumberOfMountTargets': 1,
            'OwnerId': '012345678912',
            'PerformanceMode': 'generalPurpose',
            'SizeInBytes': {
                'Value': 6144,
            },
            'Tags': [
                {
                    'Key': 'Name',
                    'Value': 'MyFileSystem',
                },
            ],
        },
    ],
    'ResponseMetadata': {
        '...': '...',
    },
}

efs_describe_mount_targets_response = {
    'MountTargets': [
        {
            'FileSystemId': 'fs-01234567',
            'IpAddress': '192.0.0.2',
            'LifeCycleState': 'available',
            'MountTargetId': 'fsmt-12340abc',
            'NetworkInterfaceId': 'eni-cedf6789',
            'OwnerId': '012345678912',
            'SubnetId': 'subnet-1234abcd',
        },
    ],
    'ResponseMetadata': {
        '...': '...',
    },
}

efs_describe_mount_target_security_groups_response = {
    'SecurityGroups': [
        'sg-4567abcd',
    ],
    'ResponseMetadata': {
        '...': '...',
    },
}

cfn_describe_stacks_response = {
    'Stacks': [
        {
            'StackId': 'string',
            'StackName': test_stack_name,
            'ChangeSetId': 'string',
            'Description': 'string',
            'Parameters': [
                {
                    'ParameterKey': 'string',
                    'ParameterValue': 'string',
                    'UsePreviousValue': True,
                    'ResolvedValue': 'string'
                },
            ],
            'CreationTime': datetime.now(),
            'DeletionTime': datetime.now(),
            'LastUpdatedTime': datetime.now(),
            'RollbackConfiguration': {
                'RollbackTriggers': [
                    {
                        'Arn': 'string',
                        'Type': 'string'
                    },
                ],
                'MonitoringTimeInMinutes': 123
            },
            'StackStatus': 'CREATE_COMPLETE',
            'StackStatusReason': 'string',
            'DisableRollback': True,
            'NotificationARNs': [
                'string',
            ],
            'TimeoutInMinutes': 123,
            'Capabilities': [
                'CAPABILITY_IAM'
            ],
            'Outputs': [
                {
                    'OutputKey': 'string',
                    'OutputValue': 'string',
                    'Description': 'string',
                    'ExportName': 'string'
                },
            ],
            'RoleARN': 'arn:aws:iam::xxxxxxx:role/xxxxx',
            'Tags': [
                {
                    'Key': 'string',
                    'Value': 'string'
                },
            ],
            'EnableTerminationProtection': False,
            'ParentId': 'string',
            'RootId': 'string',
            'DriftInformation': {
                'StackDriftStatus': 'IN_SYNC',
                'LastCheckTimestamp': datetime.now()
            }
        },
    ],
    'NextToken': 'string'
}

cfn_create_stack_response = {
    'StackId': test_stack_name
}

lambda_invoke_upload_response = {
    'StatusCode': 200,
    'FunctionError': 'string',
    'LogResult': 'string',
    'Payload': io.BytesIO(bytes(json.dumps({"message": "Chunk upload successful", "statusCode": 200}), 'utf-8')),
    'ExecutedVersion': 'string'
}

lambda_invoke_delete_response = {
    'StatusCode': 200,
    'FunctionError': 'string',
    'LogResult': 'string',
    'Payload': io.BytesIO(bytes(json.dumps({"message": "file deletion successful", "statusCode": 200}), 'utf-8')),
    'ExecutedVersion': 'string'
}

lambda_invoke_list_response = {
    'StatusCode': 200,
    'FunctionError': 'string',
    'LogResult': 'string',
    'Payload': io.BytesIO(bytes(json.dumps({'path': '/mnt/efs/', 'directories': [], 'files': [], 'statusCode': 200}), 'utf-8')),
    'ExecutedVersion': 'string'
}

lambda_invoke_make_dir_response = {
    'StatusCode': 200,
    'FunctionError': 'string',
    'LogResult': 'string',
    'Payload': io.BytesIO(bytes(json.dumps({"message": "directory creation successful", "statusCode": 200}), 'utf-8')),
    'ExecutedVersion': 'string'
}

lambda_invoke_download_response = {
    'StatusCode': 200,
    'FunctionError': 'string',
    'LogResult': 'string',
    'Payload': io.BytesIO(bytes(json.dumps({"dzchunkindex": 0, "dztotalchunkcount": 1, "dzchunkbyteoffset": 0,
                        "chunk_data": "test", "dztotalfilesize": 4}), 'utf-8')),
    'ExecutedVersion': 'string'
}



EFS = {'describe_file_systems_no_marker': efs_describe_file_systems_no_marker_response, 'describe_mount_targets': efs_describe_mount_targets_response, 'describe_mount_target_security_groups': efs_describe_mount_target_security_groups_response}
CFN = {'describe_stacks': cfn_describe_stacks_response, 'create_stack': cfn_create_stack_response}
LAMBDA = {'upload': lambda_invoke_upload_response, 'delete': lambda_invoke_delete_response, 'list': lambda_invoke_list_response, 'make_dir': lambda_invoke_make_dir_response, 'download': lambda_invoke_download_response}
EC2 = {'describe_sec_rules': ec2_describe_security_group_rules_response}