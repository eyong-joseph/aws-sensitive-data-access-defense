# AWS Sensitive Data Access Detection & Active Defense
A defender-focused AWS security monitoring and active response project for detecting sensitive access to AWS Secrets Manager and initiating automated defensive controls.
## Overview
This project demonstrates how a cloud security monitoring pipeline can detect access to sensitive data, generate security alerts, and initiate an automated response.

The project follows a defender workflow:

**Visibility → Detection → Alerting → Response → Containment**

The lab uses AWS CloudTrail, Amazon EventBridge, Amazon SNS, AWS Lambda, IAM, and AWS Secrets manager.
## Architecture

The security monitoring architecture follows this flow:

```text
Sensitive Secret Access
        |
        v
   AWS CloudTrail
        |
        +----------------------+
        |                      |
        v                      v
   CloudWatch             EventBridge
   Detection               Detection
        |                      |
        v                      +----------+
       SNS                               |
        |                                v
        v                              SNS
 Security Team                           |
                                         v
                                   Active Defense
                                      Lambda
                                         |
                                         v
                                    IAM Control
                                         |
                                         v
                                  Access Denied
```
## Security Objectives

### Objective 1 — Detection & Alerting

Detect access to the sensitive `Production_Database_Credentials` secret and notify the security team in real time using two AWS-native detection paths:

- CloudWatch Logs → Metric Filter → Alarm → SNS
- CloudTrail → EventBridge → SNS

### Objective 2 — Active Defense & Containment

Automatically respond to a detected sensitive-data access event by invoking Lambda to remove the test user's IAM permission, then validate containment by confirming subsequent access attempts return `AccessDenied`.
## AWS Services Used

| Service | Security Role |
|---|---|
| AWS CloudTrail | Records AWS API activity for visibility and investigation |
| AWS Secrets Manager | Hosts the sensitive test secret |
| Amazon CloudWatch | Detects sensitive API activity and triggers alarms |
| Amazon EventBridge | Detects matching CloudTrail events and invokes response actions |
| Amazon SNS | Delivers security notifications |
| AWS Lambda | Automates the defensive response |
| AWS IAM | Enforces access control and containment |
| Amazon S3 | Stores CloudTrail logs |
## Phase 1 — Security Foundation

The first phase established the logging and sensitive-resource foundation required for security monitoring.

### 1.1 AWS CloudTrail

A multi-Region CloudTrail trail was configured to capture AWS API activity and integrate with CloudWatch Logs for monitoring and investigation.

**Trail:** `BarakaSecurityMonitoringTrail`

Key configuration:

- Multi-Region logging enabled
- Log file validation enabled
- CloudTrail logs delivered to Amazon S3
- CloudWatch Logs integration enabled

### 1.2 Sensitive Resource — AWS Secrets Manager

A controlled honeytoken secret was created in AWS Secrets Manager to represent a sensitive production credential.

**Secret:** `Production_Database_Credentials`

The secret was used only for controlled security testing. The actual secret value is not included in this repository.

### 1.3 Amazon S3

Amazon S3 was configured as part of the logging foundation for storing CloudTrail log files.

No sensitive credentials or secret values are included in the repository.

## Phase 2 — Detection Logic: CloudWatch

The first detection path uses CloudWatch Logs and a metric filter to identify sensitive Secrets Manager API activity and trigger an alarm.

### 2.1 CloudWatch Metric Filter

A CloudWatch Logs metric filter was configured to detect `GetSecretValue` API calls to AWS Secrets Manager.

**Metric namespace:** `SecurityMonitoring`

**Metric name:** `ProductionDatabaseSecretAccess`

Detection pattern:

```text
{ ($.eventSource = "secretsmanager.amazonaws.com") && ($.eventName = "GetSecretValue") }
```
The filter converts matching CloudTrail events into the `ProductionDatabaseSecretAccess` metric.

### 2.2 CloudWatch Alarm 

The metric was connected to a CloudWatch alarm:

**Alarm:** `ProductionDatabaseSecretAccessAlarm`

**Configuration:**

- Statistic: Sum
- Period: 1 minute
- Threshold: Greater than or equal to 1
- Evaluation: 1 datapoint within 1 minute
- Alarm action: Amazon SNS
- Notification topic: `SecurityMonitoringAlerts`

The alarm was tested using a controlled `GetSecretValue` operation against the test secret. The alarm entered the **In Alarm** state and an SNS security notification was received.

## Phase 3 — Detection Logic: EventBridge

The second detection path employed Amazon EventBridge to identify specific CloudTrail API events and trigger security actions.

### 3.1 EventBridge Rule

An EventBridge rule was configured to detect `GetSecretValue` API calls made through AWS Secrets Manager.

**Rule:** `SensitiveDataAccessEventBridgeRule`

**Event pattern:**

```json
{
  "source": ["aws.secretsmanager"],
  "detail-type": ["AWS API Call via CloudTrail"],
  "detail": {
    "eventSource": ["secretsmanager.amazonaws.com"],
    "eventName": ["GetSecretValue"],
    "requestParameters": {
      "secretId": ["Production_Database_Credentials"]
    }
  }
}
```

The rule was enabled on the default EventBridge event bus.

### 3.2 EventBridge Targets

The rule was configured with two targets:

CloudTrail → EventBridge Rule → SNS → Lambda

- Amazon SNS - `SensitiveDataAccessAlerts`
- AWS Lambda - `ActiveDefenseRevokeUser`

The SNS target provides security notification, while the Lambda target supports automated defense response.

### 3.3 Controlled Validation

A controlled `GetSecretValue` request was performed against `Production_Database_Credentials`.

The EventBridge rule successfully matched the CloudTrail event, confirming that the detection logic function as expected.

The event was then available to the configured target for notification and automated respons.

## Phase 4 — Active Defense & Containment

The final phase implemented an automated response to a detected sensitive-data access event.

### 4.1 Lambda Response Function

An AWS Lambda function was configured as an EventBridge target to initiate the defensive response.

**Lambda function:** `ActiveDefenseRevokeUser`

When EventBridge detects the sensitive `GetSecretValue` event, the Lambda function extracts the IAM username from the CloudTrail event and detaches the user's designated IAM policy.

The response is designed to remove the user's ability to continue accessing protected AWS resources.

### 4.2 IAM Response

The controlled test identity was an IAM user named `Victim`.

The Lambda function used the IAM `DetachUserPolicy` API action to remove the user's `SecretsManagerRead` policy.

This provided an automated containment mechanism without requiring manual intervention from the security team.

### 4.3 Containment Validation

The response was validated using a controlled security test.

After the sensitive `GetSecretValue` event triggered the active-defense workflow, the `Victim` user no longer had the required IAM permissions.

A subsequent access attempt returned:

`AccessDenied`

This confirmed that the automated response successfully changed the user's authorization state and prevented continued access.

## Security Testing & Validation

The security controls were validated using a controlled IAM test identity and a dedicated Secrets Manager test secret.

### Test Scenario

The IAM user `Victim` was granted permission to access the test secret:

`Production_Database_Credentials`

A controlled `GetSecretValue` request was then performed.

### Detection Validation

The test generated a CloudTrail event containing:

- `eventSource`: `secretsmanager.amazonaws.com`
- `eventName`: `GetSecretValue`
- `secretId`: `Production_Database_Credentials`

The event successfully triggered the configured detection mechanisms.

### Alert Validation

The CloudWatch detection path entered the **In Alarm** state and generated an SNS security notification.

The EventBridge detection path also successfully matched the CloudTrail event and invoked its configured targets.

### Active Defense Validation

The EventBridge workflow invoked the `ActiveDefenseRevokeUser` Lambda function.

The Lambda function removed the `SecretsManagerRead` policy from the `Victim` IAM user.

After containment, a subsequent attempt to access the protected secret returned:

`AccessDenied`

This confirmed that the detection and automated containment workflow operated successfully during the controlled test.

## Detection Engineering Comparison

Two AWS-native detection paths were implemented and tested.

| Capability | CloudWatch Detection | EventBridge Detection |
|---|---|---|
| Detection source | CloudTrail logs | CloudTrail events |
| Detection mechanism | CloudWatch Logs metric filter | EventBridge event pattern |
| Primary purpose | Metric-based detection and alarm | Event-driven detection and response |
| Notification | SNS | SNS |
| Automated response | No | Lambda |
| Detection condition | `GetSecretValue` API activity | `GetSecretValue` for `Production_Database_Credentials` |
| Observed test result | Alarm entered In Alarm and SNS notification received | Event matched and configured targets were invoked |

The two approaches demonstrate different methods of building AWS-native security detections. CloudWatch provides metric-based monitoring and alarm functionality, while EventBridge provides event-driven detection that can directly initiate automated response actions.

## Security Concepts Demonstrated

This project demonstrates practical experience with:

- Cloud security monitoring
- AWS API activity monitoring
- Security event detection
- Detection engineering
- Event-driven security automation
- Security alerting and notification
- IAM access control
- Automated containment
- CloudTrail investigation
- Incident response concepts
- Defense-in-depth
- Security control validation

## Key Lessons Learned

Building this project provided practical experience in designing and validating cloud security controls.

Key lessons included:

- Security monitoring depends on reliable audit visibility.
- Detection rules must use the correct AWS event structure and field names.
- Different AWS-native detection mechanisms provide different response capabilities.
- Alerts should be validated through controlled security tests rather than configuration alone.
- Automated response requires carefully scoped IAM permissions.
- Containment should be validated by testing what the affected identity can do after the response.

## Project Evidence

The repository includes selected screenshots demonstrating:

1. CloudWatch alarm configuration and detection
2. EventBridge detection rule and targets
3. CloudTrail evidence of sensitive API activity
4. Security notification generated during testing
5. IAM containment and `AccessDenied` validation

Sensitive information such as secret values, credentials, access keys, and account identifiers has been excluded or redacted from the published evidence.

## Security Notice

This project was performed in a controlled AWS environment for educational and portfolio purposes.

The `Production_Database_Credentials` resource was a test honeytoken and did not contain real production credentials.

The IAM containment workflow was tested against a dedicated test identity.

No real credentials, secret values, access keys, or other sensitive authentication material are included in this repository.
