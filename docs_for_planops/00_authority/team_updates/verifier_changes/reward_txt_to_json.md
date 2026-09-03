Based on recent feedback from the client: 
Verifier Standard Update: reward.json Schema (Required for All Tasks) @here 
Going forward, every task's tests/verify.py must write /logs/verifier/reward.json in the following format:
{
  "reward": 0.667,
  "total_static_check_score": 0.875,
  "total_reward_hacking_check_score": 0.4825,
  "total_partial_oracle_check_score": 0.875
}reward.txt is no longer accepted. Any task that only generates reward.txt will fail the quality gate.Required Fields

total_static_check_score – Mean of all static_checks_* scores.
total_reward_hacking_check_score – Mean of all reward_hacking_checks_* scores.
total_partial_oracle_check_score – Mean of all partial_oracle_checks_* scores.
• Group checks into:
STATIC_CHECKS
REWARD_HACKING_CHECKS
PARTIAL_ORACLE_CHECKS
• Compute the mean score for each group.
• Blend them using the weighted formula above.
• Write the final reward.json.
Reference Implementation attached below

This verifier already implements the standard by:

Grouping checks into the three buckets.
Averaging each bucket.
Computing the weighted final reward.
Writing the required reward.json.


Additionally, tests/test.sh has been updated so that if verify.py it crashes, it writes an all-zero reward.json with the same schema. This prevents missing or malformed reward files.
Quality Gate Enforcement
A task will be rejected if:

:x: reward.json is missing.
:x: Only reward.txt is present.
:x: reward.json is missing any of the four required numeric fields.
:x: The reported reward does not match the weighted formula (within a tolerance of 0.001).
Please update all new and existing verifiers to follow this standard going forward.

If you're currently in the middle of a task or have already completed a task that still generates only reward.txt, please manually create the required reward.json before submitting.
When doing so:

Calculate all four fields correctly.
Double-check that the values are accurate and consistent, as even small mistakes can cause the task to fail the quality gate.
If you're not confident about the manual calculation, please update the verifier to generate reward.json and re-run the verifier instead. That's completely fine and is the preferred approach over submitting an incorrect file.
QA Leads: Please verify these submissions carefully and ensure the reward.json values are correct before approving the task. We should leave no room for calculation or formatting errors.