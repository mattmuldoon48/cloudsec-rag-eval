# AWS IAM Security Best Practices (official-source notes)

These notes are a concise local summary based on official AWS IAM documentation. They are not a copy of the full AWS documentation.

Source URLs:
- https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html
- https://docs.aws.amazon.com/IAM/latest/UserGuide/securing_access-keys.html

## Least Privilege

AWS IAM guidance emphasizes granting only the permissions needed for a role, workload, or human user to perform required tasks. A practical least-privilege process starts with managed policies or scoped permissions, then narrows access based on observed activity and review.

IAM Access Analyzer can help generate and validate policies, identify public or cross-account access, and move permissions toward least privilege. Conditions, permissions boundaries, and organization-level guardrails can further limit how permissions are used.

## Temporary Credentials

AWS recommends using IAM roles and temporary credentials for human users and workloads where possible. Temporary credentials expire after a limited period, which reduces risk if credentials are exposed.

Long-term access keys should be avoided unless a specific use case requires them. When long-term access keys are necessary, they should be assigned least privilege, protected carefully, rotated or updated when needed, and removed when inactive or no longer required.

## Access Reviews

Regular review is part of maintaining least privilege. Unused users, roles, permissions, policies, and credentials should be identified and removed so access does not accumulate over time.
