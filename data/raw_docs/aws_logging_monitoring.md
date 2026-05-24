# AWS Logging and Monitoring (sample)

This sample document describes cloud logging signals and monitoring guidance. It is illustrative and not official AWS documentation.

## Logging Sources

- Capture AWS CloudTrail for API activity.
- Collect VPC Flow Logs for network traffic.
- Capture application logs from ECS, Lambda, or EC2.

## Suspicious Activity

- Watch for failed login attempts and unusual API calls.
- Monitor privilege escalation events and policy changes.
- Detect unexpected data access from sensitive resources.

## Centralized Logging

- Send logs to a centralized storage account or SIEM.
- Keep logs immutable and searchable.
- Use alerts for high-risk events.
