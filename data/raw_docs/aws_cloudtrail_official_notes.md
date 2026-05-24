# AWS CloudTrail Logging and Monitoring (official-source notes)

These notes are a concise local summary based on official AWS CloudTrail documentation. They are not a copy of the full AWS documentation.

Source URLs:
- https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-user-guide.html
- https://docs.aws.amazon.com/en_en/awscloudtrail/latest/userguide/logging-insights-events-with-cloudtrail.html

## API Activity

AWS CloudTrail records actions taken by users, roles, and AWS services as events. These events include activity from the AWS Management Console, AWS CLI, AWS SDKs, and AWS APIs.

CloudTrail can support operational auditing, risk auditing, governance, and compliance by showing who made an API call, when it occurred, where it came from, and which resources were affected.

## Event History, Trails, and CloudTrail Lake

CloudTrail Event history provides searchable recent management events for an AWS account. Trails and CloudTrail Lake can be used to collect, store, query, and analyze events for broader auditing and security investigations.

Security teams can use CloudTrail records to investigate suspicious account behavior, privilege changes, policy updates, access to sensitive resources, and other high-risk activity.

## CloudTrail Insights

CloudTrail Insights can help identify unusual API activity by analyzing API call rates and API error rates against a baseline. When activity deviates from normal patterns, Insights events can support detection and response workflows.
