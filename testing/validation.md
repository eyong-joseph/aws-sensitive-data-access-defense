# Security Validation

## Test 1 — CloudWatch Detection

1. Use the controlled `Victim` IAM identity with the required test permission.
2. Perform a `GetSecretValue` request against `Production_Database_Credentials`.
3. Verify the activity appears in CloudTrail.
4. Verify the CloudWatch metric increments.
5. Verify the CloudWatch alarm enters the **In Alarm** state.
6. Verify the SNS security notification is received.

## Test 2 — EventBridge Detection and Active Defense

1. Ensure `SensitiveDataAccessEventBridgeRule` is enabled.
2. Perform a controlled `GetSecretValue` request.
3. Verify that EventBridge records a matching event.
4. Verify that `ActiveDefenseRevokeUser` is invoked.
5. Verify that the `SecretsManagerRead` policy is detached from the test identity.
6. Attempt another protected-resource access.
7. Verify that the request returns `AccessDenied`.

## Expected Security Outcome

Sensitive-resource access generates security telemetry and notifications. A matching EventBridge event can trigger automated IAM containment, after which unauthorized access attempts are denied.
