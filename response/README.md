# Response

This directory contains the automated defensive response implemented in the project.

The EventBridge rule invokes the `ActiveDefenseRevokeUser` Lambda function when a matching sensitive-data access event is detected.

The Lambda function extracts the IAM username from the CloudTrail event and detaches the designated IAM policy from the affected user.

The response was validated using the controlled `Victim` test identity. After containment, a subsequent protected-resource access attempt returned `AccessDenied`.
