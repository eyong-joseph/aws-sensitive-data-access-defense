import os
import boto3

iam = boto3.client("iam")

VICTIM_POLICY_ARN = os.environ["VICTIM_POLICY_ARN"]


def lambda_handler(event, context):
    detail = event.get("detail", {})
    identity = detail.get("userIdentity", {})

    user_name = identity.get("userName")

    if not user_name:
        return {
            "statusCode": 400,
            "message": "No IAM username found in the CloudTrail event."
        }

    iam.detach_user_policy(
        UserName=user_name,
        PolicyArn=VICTIM_POLICY_ARN
    )

    return {
        "statusCode": 200,
        "message": f"Policy detached from user: {user_name}"
    }
