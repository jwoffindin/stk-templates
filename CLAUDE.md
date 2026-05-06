# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a CloudFormation template repository for the `stk` tool (CLI: `cfn`). Templates here are the reusable "lego blocks" that get composed with configuration from `../stk-config/` to deploy AWS infrastructure. The deployer source lives at `../cfn-stk/`.

Templates are Jinja2-rendered YAML (`{{ var }}`). Use `##` (not `#`) for Jinja2 block directives (`## if`, `## for`, `## endif`) — `#` is a YAML comment and will break rendering.

## Rendering and Deploying

All `cfn` commands follow the pattern `cfn <command> <stack-name> <environment>`, run from `../stk-config/`:

```bash
cfn show-template vpc dev          # render template with config applied
cfn show-config vpc dev            # inspect resolved vars/refs/params
cfn diff vpc dev                   # diff local vs deployed CloudFormation
cfn validate vpc dev               # validate config + template + AWS API
cfn deploy vpc dev                 # create or update the stack
```

During template development, point the `dev` environment at this local checkout by setting in the config file:

```yaml
environments:
  dev:
    template:
      version:           # empty = local filesystem
      root: /Users/johnw/src/stk-templates
```

The `stk-config` `includes/common.yaml` already does this by default for `dev`.

## Template Structure

Each `.yaml` file is a CloudFormation template with Jinja2. Standard pattern:

```yaml
Metadata:
  stack:
    deployed_at: "{{ deploy.timestamp }}"
    version:
      template_commit: "{{ deploy.template_sha }}"
      template_ref:    "{{ deploy.template_ref }}"
      config_commit:   "{{ deploy.config_sha }}"
      config_ref:      "{{ deploy.config_ref }}"
    vars:
      some_var: Description of what this var does   # documents required vars
```

The `Metadata.stack.vars` block documents which `vars` a template expects — this is the interface contract between template and config.

## Metadata Companion Files

Files prefixed with `_` (e.g. `_vpc.yaml`, `_gitlab-oidc-provider.yaml`) are metadata companions to their matching template. They describe the template's purpose and default config:

```yaml
---
description: |
  Human-readable description of what the template does
config:
  vars:
    some_var: default_value
```

These are not CloudFormation templates — they're consumed by `stk` tooling for documentation and defaults.

## Lambda Functions

Lambda source lives in `functions/<name>/`. The `functions/site-packages/` directory is vendored Python dependencies for the shared lambda layer (`lambda-layers.yaml`).

To update vendored dependencies (requires Docker):

```bash
cd functions
make setup
```

Templates reference lambda code via helpers:
- `{{ lambda_uri('approvals') }}` — uploads `functions/approvals/` as a zip to S3 and returns the URI
- `{{ upload_zip('functions/site-packages', prefix='python') }}` — used by `lambda-layers.yaml` for the shared layer
- `{{ python_lambda_layer_arn }}` — ARN of the deployed lambda layer (passed in as a var from config)

## Testing Lambda Functions

Tests use pytest with moto (AWS mocking) and boddle (bottle.py request mocking):

```bash
# Run all tests
cd functions && python -m pytest

# Run a single test file
cd functions && python -m pytest approvals/tests/test_handler.py

# Run a single test
cd functions && python -m pytest approvals/tests/test_handler.py::TestHandler::testIndex
```

Install test deps: `pip install -r functions/approvals/tests/requirements-dev.txt`

## Stack Naming Convention

Deployed stacks are named `$environment-$template_name` (e.g. `dev-vpc`, `prod-gitlab-oidc-provider`). The `refs:` section in config files uses this convention to look up cross-stack outputs.

## Key Template Relationships

- `lambda-layers.yaml` — deploys the shared Python layer; its `PythonLayerArn` output is passed as `python_lambda_layer_arn` var to any template using lambda functions
- `approval-lambda.yaml` + `approval-load-balancer.yaml` — approval workflow: ALB routes to the lambda in `functions/approvals/`
- `vpc.yaml` — foundational VPC; other stacks reference its outputs (`VpcId`, `PublicSubnets`) via `refs.vpc.*`
