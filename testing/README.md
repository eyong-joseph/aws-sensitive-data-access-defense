# Testing

This directory contains documentation related to security-control validation.

Testing was performed using a controlled IAM test identity and the dedicated `Production_Database_Credentials` honeytoken.

The validation process included:

- Generating a controlled `GetSecretValue` request.
- Verifying the resulting CloudTrail activity.
- Verifying CloudWatch detection and SNS alerting.
- Verifying EventBridge event matching.
- Verifying Lambda invocation.
- Confirming that subsequent unauthorized access attempts returned `AccessDenied`.
