---
study: "{{study_id}}"
artifact: "deployment-spec"
phase: "deploy"
status: "draft"
owner: "{{owner}}"
approved_by: ""
approved_on: ""
---

# {{title}}: Deployment spec

The deployment spec defines how the approved model goes into use, and how to undo it.

## Serving pattern

| Item | Entry |
|---|---|
| Pattern | [[FILL: batch, online, or embedded]] |
| Reason | [[FILL: link to latency and freshness needs from the charter]] |
| Trigger or schedule | [[FILL: for example daily at 02:00 UTC, or on each request]] |
| Consumers | [[FILL: systems and people that use the output]] |

## Interface contract

### Input schema

| Field | Type | Unit | Allowed values | Required |
|---|---|---|---|---|
| [[FILL: field]] | [[FILL: type]] | [[FILL: unit]] | [[FILL: range]] | [[FILL: yes or no]] |

### Output schema

| Field | Type | Meaning |
|---|---|---|
| [[FILL: field, for example score]] | [[FILL: type]] | [[FILL: meaning]] |

### Service levels

| Item | Target |
|---|---|
| Latency (p95) | [[FILL: value with unit]] |
| Throughput | [[FILL: value with unit]] |
| Availability | [[FILL: percentage over a period]] |
| Behaviour on invalid input | [[FILL: reject, default or fallback]] |

## Packaging and versioning

| Item | Entry |
|---|---|
| Artifact | [[FILL: for example MLflow model, container image, SageMaker model package]] |
| Model version | [[FILL: version and registry location]] |
| Model record | [[FILL: path model-records/<model-id>.toml. Create it with dsflow model new]] |
| Promotion | [[FILL: name of the human who runs dsflow model promote after approval of this spec]] |
| Code version | [[FILL: git tag or commit]] |
| Dependency lock | [[FILL: lock file and base image]] |
| Version rule | [[FILL: how you number new versions]] |

## Infrastructure

| Item | Entry |
|---|---|
| Runtime environment | [[FILL: platform and region]] |
| Compute and memory | [[FILL: size]] |
| Storage and data stores | [[FILL: stores and retention]] |
| Estimated run cost | [[FILL: cost per period]] |

## Security and access

| Item | Entry |
|---|---|
| Authentication and authorisation | [[FILL: method and roles]] |
| Secrets handling | [[FILL: where secrets are stored]] |
| Personal data in requests and logs | [[FILL: handling and masking]] |
| Audit logging | [[FILL: what you log and for how long]] |

## Rollout strategy

| Stage | Method | Traffic share | Duration | Exit criteria |
|---|---|---|---|---|
| 1 | [[FILL: shadow]] | [[FILL: share]] | [[FILL: duration]] | [[FILL: criteria]] |
| 2 | [[FILL: canary]] | [[FILL: share]] | [[FILL: duration]] | [[FILL: criteria]] |
| 3 | [[FILL: full release or A/B test]] | [[FILL: share]] | [[FILL: duration]] | [[FILL: criteria]] |

## Rollback plan

| Item | Entry |
|---|---|
| Rollback trigger | [[FILL: conditions that start a rollback]] |
| Fallback behaviour | [[FILL: previous model, rule or manual process]] |
| Rollback steps | [[FILL: numbered steps, one action each]] |
| Time to roll back | [[FILL: duration with unit]] |
| Decision owner | [[FILL: name]] |

## Runbook links

| Topic | Link |
|---|---|
| Deploy procedure | [[FILL: link or path]] |
| Incident response | [[FILL: link or path]] |
| Contacts and escalation | [[FILL: link or path]] |

## Release checklist

- [ ] [[FILL: add a release step, for example register the model with the evaluated run ID]]
- [ ] A contract test checks the input and output schemas.
- [ ] A load test meets the service levels.
- [ ] A test run proves the rollback procedure.

## Gate checklist

- [ ] The spec chooses the serving pattern and gives a reason.
- [ ] The spec defines the interface contract and the service levels.
- [ ] The artifact has a version and links to the evaluated run.
- [ ] You complete the security review.
- [ ] Each rollout stage has exit criteria.
- [ ] You test the rollback plan.
- [ ] Runbook links exist.
- [ ] You complete the release checklist.
- [ ] The operations owner approves the spec.

## Open items

Record open questions, assumptions, risks and deviations in `log.md`. Do not keep them here.

[[FILL: list the log IDs that relate to this artifact, or write N/A]]
