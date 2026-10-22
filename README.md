# agent-deployment-cloud

Terraform for the infrastructure that will run AI agents on Google Kubernetes Engine, with three environments:
`dev`, `stage` and `prod`. Each environment gets its **own VPC**, its own GKE cluster and its own image registry.
Nothing here has been applied; applying creates billable resources.

## Layout

```
modules/
  vpc/        dedicated VPC + subnet (pod and service ranges) + optional Cloud NAT
  gke/        GKE cluster (one managed control plane) + worker node pool + node service account
  registry/   Artifact Registry Docker repo for the agent images
  github-actions/  deployer identity + keyless GitHub login (Workload Identity Federation), one per environment
  platform/   composes the modules above and enables the needed Google APIs
apps/         the two hello-world apps (app1, app2): code, tests, Dockerfile, per-app Helm values
agents/       the AI agent: agent-core (library) + agent-starter (the agent) and the Dockerfile that builds them
charts/ai-agent/  Helm chart for the agent (deploy/agents/<env>.yaml holds per-environment values)
charts/hello-app/  one Helm chart shared by every app
deploy/env/   per-environment Helm settings (dev.yaml, stage.yaml, prod.yaml)
.github/workflows/  CI checks and the deploy pipelines
envs/
  dev/        thin root module: main.tf, variables.tf, terraform.tfvars, outputs.tf
  stage/
  prod/
```

Every environment calls `modules/platform` with different inputs, so they stay structurally identical and only the
values in each `envs/<env>/main.tf` differ. Each environment folder has its own Terraform state.

## Cluster shape: "1 master + 2 workers"

On GKE the master is the Google-managed control plane; you pay no node charges for it and you do not run it.
The two workers are normal VMs.

| | dev | stage | prod |
|---|---|---|---|
| Control plane | zonal (1) | zonal (1) | regional (HA) |
| Workers | 2 x e2-medium, `asia-south1-a` | 2 x e2-standard-2, `asia-south1-a` | 1 each in `a` and `b` = 2 x e2-standard-4 |
| Worker IPs | public | private + Cloud NAT | private + Cloud NAT |
| Kubernetes API | open (restrict if you can) | `authorized_networks` recommended | `authorized_networks` **required** |
| Deletion protection | off | on | on |
| Release channel | REGULAR | REGULAR | STABLE |
| Image tags | mutable | immutable | immutable |
| VPC | `agents-dev-vpc` 10.50.0.0/20 | `agents-stage-vpc` 10.51.0.0/20 | `agents-prod-vpc` 10.52.0.0/20 |

Region is Mumbai (`asia-south1`). Pod and service ranges differ per environment so the VPCs can be peered later.
All resource names carry the environment, e.g. `agents-dev-cluster`, so environments can share one project.

## Deploy an environment

```
gcloud auth application-default login
cd envs/dev                    # or stage / prod
terraform init
terraform plan
terraform apply
```

For `prod`, first list your office/VPN CIDRs in `envs/prod/terraform.tfvars`; `terraform plan` refuses to run without them.

Plan sizes: dev 17 resources, stage and prod 19 (they add Cloud Router and NAT). Setting `github_repository` adds 9 more per environment.

## Deploying apps with GitHub Actions

Each environment can get its own CI/CD identity. Set `github_repository = "owner/repo"` in
`envs/<env>/terraform.tfvars` and apply; this creates, per environment:

- a deployer service account (`agents-<env>-gha`) that may push to **that environment's registry only** and deploy to
  **that environment's cluster**;
- a Workload Identity pool and provider that accept a GitHub token **only if** the repository matches **and** the job
  runs in the GitHub environment named `<env>`. No keys are stored anywhere, and a dev workflow cannot reach prod;
- the cluster registered with the fleet, so `kubectl` works through the **Connect gateway** even when the Kubernetes API
  is locked to private CIDRs (stage and prod). GitHub-hosted runners have changing IPs, so without this they could not
  deploy to a locked-down cluster.

Then, in GitHub (Settings > Environments), create environments `dev`, `stage`, `prod` (add required reviewers on `prod`)
and set these on each environment, using `terraform output` from the matching `envs/<env>` folder:

| GitHub environment setting | Value from |
|---|---|
| secret `GCP_WIF_PROVIDER` | `github_wif_provider` |
| secret `GCP_SERVICE_ACCOUNT` | `github_service_account` |
| variable `GCP_PROJECT_ID` | your project ID (`project_id` in tfvars) |
| variable `IMAGE_PATH` | `image_path` |
| variable `CLUSTER_NAME` | `cluster_name` |
| variable `CLUSTER_LOCATION` | zone for dev/stage (`asia-south1-a`), region for prod (`asia-south1`) |

A workflow job must declare `environment: <env>` and `permissions: id-token: write`, authenticate with
`google-github-actions/auth`, push to `IMAGE_PATH`, then reach the cluster with
`gcloud container fleet memberships get-credentials <CLUSTER_NAME>` and deploy (for example with Helm).
Check the fleet membership name and location with `gcloud container fleet memberships list` the first time.
The identity is created by Terraform; the workflows are described in the next section.

## The apps and their pipelines

`apps/app1` (plain-text) and `apps/app2` (JSON) are tiny Python web services with a unit test and a Dockerfile.
Both answer `GET /` with "Hello, World!" and `GET /healthz` with a health result. One Helm chart (`charts/hello-app`)
deploys either of them; `deploy/env/<env>.yaml` sets the environment (replicas, disruption budget, resources) and
`apps/<app>/values.yaml` sets the app name.

| Workflow | Runs when | What it does |
|---|---|---|
| `ci.yml` | pull request | unit tests, Docker build (not pushed), `helm lint`/`template` for every app and environment, `terraform fmt` and `validate` |
| `app1.yml`, `app2.yml` | push to `main` touching that app, the chart or `deploy/env`; or manually | deploys to **dev** on push; **Run workflow** lets you pick dev, stage or prod |
| `_deploy.yml` | called by the two above | tests, builds and pushes the image (skips if the tag exists), connects to the cluster, `helm upgrade --install --atomic`, prints the app address in the run summary |

Images are tagged with the short git SHA. A promotion to stage or prod rebuilds nothing if that SHA is already in the
registry. Each deployed app is its own Helm release in the `apps` namespace and gets its own Google load balancer
(`service.type: LoadBalancer`); switch to `ClusterIP` plus an Ingress to share one.

Order of work for a first deployment: apply `envs/<env>` with `github_repository` set, add the GitHub environment
secrets and variables above, push this repository to GitHub, then run the **app1** and **app2** workflows.
## The AI agent

`agents/` holds the two attached projects, unchanged:

- `agents/agent-core` is the framework library (FastAPI service, Claude tool-use loop). It is not deployed on its own.
- `agents/agent-starter` is the agent that runs: a prompt, a markdown skill and one `echo` tool. Edit its `src/agent/prompts`,
  `skills` and `tools` to give it a real job.

`agents/Dockerfile` builds **one image** from both and installs `agent-core` from the local copy, so the build never
downloads code from another GitHub repository. `charts/ai-agent` deploys it; `deploy/agents/<env>.yaml` holds the
per-environment settings; the workflow is `agent-starter.yml` (calls `_deploy-agent.yml`). A push to `main` that touches
`agents/`, the chart or `deploy/agents` deploys to **dev**; run the workflow manually to promote to stage or prod.

The agent lands in the `agents` namespace as Helm release `agent-starter`, behind a `ClusterIP` Service. It is **not
public on purpose**: `/run` has no authentication and every call can spend LLM money. Reach it with:

```
kubectl -n agents port-forward svc/agent-starter 8080:80
# then http://localhost:8080/ (test console), /docs (Swagger), /healthz, /metrics
```

**Reaching it from your laptop (optional, locked to your IP).** By default the agent is private. To get a browser URL, set the
GitHub environment **variable** `AGENT_ALLOWED_CIDRS` to the public IP address(es) allowed to connect, comma-separated, for
example `203.0.113.7/32`. The next deploy then creates a Google load balancer that accepts connections **only** from those
addresses, and the run summary prints the URL (`http://<ip>/`, API docs at `/docs`). The list lives in GitHub, not in the code,
because this repository may be public. Entries must be IPv4 addresses or CIDRs, and `0.0.0.0/0` is refused. Check the address your
browser really uses at https://ifconfig.me, since company proxies can differ from your laptop's own address. The URL is plain
HTTP, and anyone on an allowed address can use the agent, so keep the list short. Clear the variable to make the agent private again.
**Giving it a brain.** The agent supports two providers, chosen by the model name or `AGENT_LLM_PROVIDER`:

| Provider | GitHub environment secret | `AGENT_MODEL` example |
|---|---|---|
| OpenRouter (default here) | `OPENROUTER_API_KEY` | `openai/gpt-4o-mini` |
| Anthropic | `ANTHROPIC_API_KEY` | `claude-sonnet-5-5` |

Add the secret to the GitHub environment (`dev`, `stage`, `prod`) and, optionally, the environment **variable** `AGENT_MODEL`.
The pipeline stores the key as the Kubernetes secret `agent-secrets`, passes it to the pod under the right variable name, and
sets the provider and model. If both secrets exist, OpenRouter wins. With neither, the agent deploys with the no-op brain,
which is a free way to confirm the pipeline works. The run summary shows the active provider and model. Keys live only in
GitHub and in the cluster, never in Terraform or git, and `.env.example` must only ever hold placeholders.

OpenRouter support is code in `agents/agent-core/src/agent_core/llm/openrouter.py` (tests in `tests/test_openrouter.py`);
the rest of the agent is unchanged.
It uses the same GitHub environment secrets and variables as the apps, so no new infrastructure is needed.
## Next steps once a cluster exists

```
terraform output get_credentials_command     # connect kubectl
terraform output docker_auth_command         # allow docker push to the registry
terraform output image_path                  # where to push agent images
```

Then build the agent image, push it to `image_path`, create the `ANTHROPIC_API_KEY` secret with `kubectl`
(never in Terraform), and deploy the agent's Helm chart.

## Remote state (recommended before a team uses this)

State is local by default. For shared, locked, versioned state create a GCS bucket and uncomment the `backend "gcs"`
block in each environment's `main.tf` (prefixes `agents/dev`, `agents/stage`, `agents/prod`), then
`terraform init -migrate-state`.

## Cost notes

Dev is the cheapest: one control plane plus two small VMs. Stage and prod add Cloud NAT and larger VMs, and prod runs
a regional control plane. Destroy an environment with `terraform destroy` (stage and prod need
`deletion_protection = false` applied first).

## Not included yet

Encryption keys (CMEK), audit-log buckets, alerting and budgets. Add them per environment when
needed; the module split makes each a self-contained addition.
