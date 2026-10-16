# Codex Internal Test Cloud Deployment V0.1

Status: `PURCHASE_CANDIDATE_NOT_EXECUTED`

Date: 2026-08-31

Scope: Diary One real-media internal Web testing and the shared test-backend boundary for a later App test client.

Explicitly out of scope: Firmware/SDK, hardware transfer, the formal App UI, production SLA, final privacy policy, and claiming that the current X01 bridge is the S00-S13 Production engine.

## 1. Outcome

Use a split deployment:

```text
Internal tester
  -> codex-diary.canpu18.com
  -> OpenAI Sites: ChatGPT sign-in + server-side tester allowlist + Web UI
  -> short-lived backend session
  -> codex-diary-api.canpu18.com
  -> Alibaba Cloud mainland Staging
       -> API + bounded job worker
       -> PostgreSQL test ledger
       -> private OSS Evidence objects
       -> Alibaba Model Studio
```

This preserves the agreed product boundary:

- Web and the later App use different identity/input adapters.
- Both clients use one shared Diary One test core, run ledger, audit trace, evaluation store, and model gateway.
- Raw phone media remains in the browser in this Web test. Only normalized Evidence is uploaded.
- X01 remains an explicit real-media compatibility bridge. Deployment does not rename it Production.

## 2. Why this shape fits the measured workload

The first recorded 24-asset real-media run provides a usable Staging baseline:

| Metric | Measured value |
| --- | ---: |
| Raw phone media read locally | 330,804,848 bytes |
| Normalized Evidence uploaded | 7,354,426 bytes |
| Assets / normalized frames | 24 / 72 |
| Frames sent to the model | 36 |
| Browser Evidence preparation | 36.24 seconds |
| Upload + service round trip | 88.90 seconds |
| Model bridge | 88.76 seconds |
| Server multipart materialization | 0.08 seconds |
| Input / output tokens | 37,813 / 8,634 |
| Recorded model cost | CNY 0.01862295 |

The wait is dominated by the remote model, not local CPU. The server only materializes normalized JPEG Evidence, validates contracts, writes audit records, and calls the model. It does not decode the original phone videos. Therefore a GPU or a large compute instance would not improve the current bottleneck.

## 3. Identity and access

### 3.1 Web tester identity

The existing Sites project remains the Web host because it already supports ChatGPT sign-in. Before shared publication:

1. make the browser route sign-in-gated;
2. check the tester email against a server-side allowlist;
3. exchange the signed-in Sites identity for a short-lived Diary One backend session;
4. never expose the Alibaba Model Studio key or a permanent backend bearer token to the browser.

The Site platform access may be public so external ChatGPT accounts can reach the sign-in flow, but the product route and all write actions remain allowlist-protected. "Public Site shell" must not mean public access to test data.

### 3.2 Later App identity

The App must not impersonate Sites or reuse Sites headers. It will use a separate `/v1/app-test/session` adapter and receive the same internal tester/run identity shape. This keeps the shared core stable while allowing App authentication to change later.

### 3.3 Roles for V0.1

- `ADMIN`: manage tester allowlist and see all test runs/evaluations.
- `TESTER`: create runs, see own runs, and evaluate own results.
- No anonymous read or write access.

## 4. Alibaba Cloud minimum resource list

Resource group and tag prefix: `codex-diary-one-staging`

Recommended region: `cn-shanghai`.

### 4.1 Purchase now

| Resource | Initial configuration | Reason |
| --- | --- | --- |
| ECS | 2 vCPU / 4 GiB RAM, Linux, 40 GiB system disk | Enough for API, one or two bounded model jobs, PostgreSQL, and reverse proxy at internal-test scale |
| Public network | Fixed public IPv4, pay by traffic, 10 Mbps safety cap | Upload is inbound; outbound is small and bursty, so fixed monthly bandwidth is unnecessary at first |
| OSS | Private Standard LRS bucket, pay as used | Store normalized Evidence/selected thumbnails, never public objects |
| DNS | `codex-diary` and `codex-diary-api` records | Web custom domain and mainland API domain |
| TLS | Managed Sites TLS for Web; free DV/ACME certificate for API | HTTPS on both ingress paths |
| Model Studio | Dedicated Staging API key with spend/rate limits | Separate company test spend from personal/local credentials |

### 4.2 Run on the ECS initially

- HTTPS reverse proxy.
- Diary One API service.
- One bounded job worker; start with concurrency `1`, raise to `2` only after observation.
- PostgreSQL for users, test days, run status, output metadata, stage metrics, token/cost records, evaluation targets, evaluation revisions, and audit events.
- Daily encrypted database backup uploaded to the private OSS bucket.

### 4.3 Do not purchase yet

- GPU.
- RDS.
- Redis.
- SLB/ALB.
- Kubernetes/ACK.
- CDN.
- WAF paid tier.
- Long-term raw-video storage.

RDS becomes justified when the App test begins, tester count grows materially, or database availability/restore objectives exceed what a single Staging ECS can provide. Redis or a managed queue becomes justified only when database-backed jobs and one/two workers cannot meet observed concurrency.

## 5. Persistence contract

### 5.1 PostgreSQL records

Persist structured records centrally:

- tester identity and role;
- imported test-day metadata;
- asset metadata without raw media bytes;
- Evidence object keys and hashes;
- run state and immutable run revision;
- Chapter/Aha/editorial output and decision trace;
- per-stage time, model calls, tokens, and estimated cost;
- granular evaluation target: day, Chapter, Aha, asset, Evidence frame, boundary, title, story, tag, or independence relation;
- issue code, suggestion text, and evaluation revision history.

### 5.2 OSS objects

- Private bucket only.
- Normalized Evidence and selected thumbnails only.
- Access through short-lived signed URLs.
- Initial lifecycle candidate: delete Evidence bytes after 30 days while retaining structured run/audit/evaluation records.
- Do not upload phone originals in V0.1.

The 30-day Evidence lifecycle is an operational test default, not a frozen product privacy contract. It can be revised after real evaluation cadence is known.

## 6. Capacity and the current 24-item boundary

Cloud deployment does not solve the X01 24-item limit. It remains a single-request research guardrail:

- up to 24 assets;
- up to 72 normalized frames in the current Web contract;
- currently at most 48 model frames by default;
- one long-running model call with no partial retry.

V0.1 can be shared with a small pilot only if the UI continues to state this limit explicitly. It must not be presented as full-day product capacity.

Before broader internal testing or App testing, implement the real expansion path:

1. accept the complete test day;
2. upload Evidence directly to private OSS;
3. understand bounded batches and cache Observation outputs;
4. retry only failed batches;
5. aggregate structured observations across the complete day;
6. run Chapter/Aha editorial selection over the complete-day structure;
7. keep run- and stage-level time/token/cost attribution.

For the 186-asset high-intensity reference day, eight 24-item-sized understanding batches are a planning approximation, not a frozen batching contract. At the measured X01 price, eight equivalent calls would be about CNY 0.15 before the complete-day aggregation call. Actual Production-shaped cost must be measured after the batch/aggregation prompts exist.

## 7. Cost envelope

The following is a planning range, not an Alibaba Cloud quote. Promotions, region, billing duration, and account eligibility change the purchase-page price.

| Cost area | Planning envelope |
| --- | ---: |
| ECS + 40 GiB disk | CNY 50-200 / month |
| Public traffic | CNY 0-30 / month at small internal-test volume |
| OSS storage and requests | Usually below CNY 5 / month at Evidence-only scale |
| Model API | About CNY 1.86 per 100 measured 24-asset-equivalent runs; CNY 9.31 per 500, before new batching/aggregation work |
| DNS / existing domain | No new domain purchase |
| RDS / Redis / GPU | CNY 0 in V0.1 |

Expected V0.1 total: approximately `CNY 60-245/month`, plus any Sites plan cost already associated with the existing project. The Alibaba purchase page is the final price source.

## 8. Deployment order

### Gate A - code readiness, no cloud purchase needed

1. Protect the Web route with ChatGPT sign-in and a server-side email allowlist.
2. Replace the editable local endpoint/token fields with environment-owned configuration.
3. Add a Sites-to-backend short-lived session exchange.
4. Add backend run ownership and authorization checks.
5. Replace local JSON-only persistence with the central run/evaluation repository while preserving audit exports.
6. Add a bounded job state so a model call does not depend on one fragile browser connection.

### Gate B - purchase and infrastructure

1. Create resource group `codex-diary-one-staging`.
2. Purchase the ECS and enable traffic-billed public IPv4.
3. Create a private OSS bucket with lifecycle and CORS limited to the Web origins.
4. Install the API, worker, PostgreSQL, backup, reverse proxy, monitoring, and log rotation.
5. Configure the dedicated Model Studio Staging key as a server secret.

### Gate C - domains and publication

1. Attach `codex-diary.canpu18.com` to the existing Sites project and apply the returned DNS validation/CNAME records.
2. Point `codex-diary-api.canpu18.com` to the ECS.
3. Issue TLS for both domains.
4. Display `Canpu 旗下 Diary One 内部测试` and `沪ICP备18018191号-2` in the Web footer.

### Gate D - pilot

1. Owner-only end-to-end smoke run.
2. One photo-only and one mixed photo/video run.
3. Verify audit, Evidence object access, granular evaluation, time/token/cost, retry, and deletion lifecycle.
4. Add 3-5 tester emails.
5. Observe at least ten successful runs before raising worker concurrency or adding managed infrastructure.

## 9. Purchase decision to request once

Only the following purchase decision is required for V0.1:

> Approve one Alibaba Cloud Shanghai ECS at 2 vCPU / 4 GiB / 40 GiB, traffic-billed public IPv4 with a 10 Mbps cap, plus pay-as-you-go private OSS. Do not purchase RDS, Redis, GPU, load balancing, CDN, or paid WAF yet.

All exact prices must be copied from the Alibaba purchase confirmation screen before payment.

## 10. Exit criteria

V0.1 is ready for internal testers only when:

- a non-allowlisted ChatGPT account cannot access the product route or API;
- the browser never receives the Model Studio key or a permanent backend secret;
- raw originals are not uploaded;
- every run is bound to one tester and one immutable run revision;
- every Chapter/Aha/asset/frame evaluation can be stored and retrieved centrally;
- stage time, tokens, and model cost are visible and auditable;
- one failed job cannot corrupt the latest successful run;
- the UI still labels X01 and the 24-item limit honestly;
- the Canpu/ICP footer is present on the deployed Web surface.

## 11. Evidence and current price references

- Measured run evidence: local `var/x01_runs/92af24f9-1baf-4cc4-80a0-bae3554b3414/run_audit.json` and its matching `client_trace.json`.
- Alibaba Cloud ECS public price table: <https://ecs-buy.aliyun.com/price>
- Alibaba Cloud public-bandwidth billing: <https://help.aliyun.com/zh/ecs/public-bandwidth/>
- Alibaba Cloud OSS storage billing: <https://help.aliyun.com/zh/oss/storage-fees>
- Alibaba Cloud same-provider server-change filing guidance: <https://help.aliyun.com/zh/icp-filing/basic-icp-service/support/changes-for-the-record-the-faq>

Public cloud prices are time-sensitive. The purchase-page total, not this document, is authoritative at checkout.
