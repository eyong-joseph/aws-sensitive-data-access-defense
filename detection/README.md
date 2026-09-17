# Detection

This directory contains the detection logic used to identify sensitive AWS API activity.

The project implements two AWS-native detection paths:

- CloudWatch Logs metric filter → CloudWatch Alarm → SNS
- CloudTrail → EventBridge Rule → SNS

The EventBridge detection path also supports automated response through the `ActiveDefenseRevokeUser` Lambda function.
