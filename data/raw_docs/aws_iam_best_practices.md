# AWS IAM Best Practices (sample)

This sample document describes common cloud security practices for AWS IAM. It is illustrative and not official AWS documentation.

## Least Privilege

- Use fine-grained IAM policies.
- Grant only the permissions required for a task.
- Avoid broad actions like `*` and wide resource scopes.
- Assign roles to workloads instead of long-lived user credentials.

## Key Rotation

- Rotate keys on a regular schedule.
- Prefer temporary credentials with IAM roles.
- Disable or remove inactive access keys.

## Access Review

- Regularly review IAM role assignments.
- Remove unused permissions and obsolete users.
