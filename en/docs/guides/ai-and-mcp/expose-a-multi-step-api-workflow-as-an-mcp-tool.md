---
title: "Expose a multi-step API workflow as an MCP tool"
description: "Combine several API calls into one Arazzo workflow, generate an MCP server from it, and expose that server as a governed MCP server in the agent control plane."
canonical_url: https://wso2.com/api-platform/docs/guides/ai-and-mcp/expose-a-multi-step-api-workflow-as-an-mcp-tool/
md_url: https://wso2.com/api-platform/docs/guides/ai-and-mcp/expose-a-multi-step-api-workflow-as-an-mcp-tool.md
tags:
  - guides
  - ai-and-mcp
  - mcp
  - arazzo
author: Choreo API Platform Documentation Team
last_updated: 2026-11-26
content_type: "tutorial"
---

# Expose a multi-step API workflow as an MCP tool

## Overview

A REST API can be given to an AI agent as one MCP tool per endpoint. That's
manageable for a small API. It gets harder to rely on as the API grows, and it
falls short whenever the calls have to happen in a particular order.

- **The order of the calls has nowhere to live.** It survives only in the prompt
  you wrote for the agent, so you can't version it, test it, or review it.
- **The tool list fills up.** Every tool's schema is sent to the model on every
  request, and similar tools compete, so the model picks the wrong one or calls
  them out of order.
- **A half-finished sequence becomes the agent's problem.** The reservation
  succeeds, the order fails, and stock is held for an order that was never created.

The alternative: describe the sequence once as a workflow, and give the agent a
single tool that runs it.

In this guide, you build one tool called `place_an_order` that runs three calls
in order:

| Step | Call | Description |
|---|---|---|
| 1 | Check stock for the SKU | No point reserving what isn't there |
| 2 | Reserve the quantity | Holds the stock while the order is created |
| 3 | Create the order | Needs the reservation identifier from step 2 |

The agent makes one call and never sees the three.

To build it, you:

- Take three APIs and describe an ordering sequence over them in an
  [Arazzo](https://spec.openapis.org/arazzo/latest.html) specification.
- Generate an MCP server from that specification.
- Expose that server through the agent control plane as a governed MCP server.

## Learning objectives

By the end of this guide, you understand:

- Why a call sequence is better described once, as a workflow, than left for an
  agent to work out each time.
- How Arazzo syntax passes values between steps and decides when a step runs.
- Why one workflow becomes exactly one MCP tool, and where that tool's
  description and input schema come from.
- What the gateway adds once the MCP server is deployed: authentication and
  policies.

## Prerequisites

- The APIs the workflow calls, and their OpenAPI definitions.
- Docker, to build and run the generated server.
- [`arazzo-mcp-gen`](https://github.com/wso2/arazzo-mcp-generator), from the
  releases page. The archive holds a binary named for your platform, such as
  `arazzo-mcp-gen-darwin-arm64`. Rename it to `arazzo-mcp-gen` and put it on your
  `PATH`, for example with `sudo mv arazzo-mcp-gen-darwin-arm64 /usr/local/bin/arazzo-mcp-gen`.
- Node.js, which `arazzo-mcp-gen validate` uses to lint the Arazzo file.
- An agent control plane account. [Sign up for free](https://console.cloud.choreolabs.com/agent-management/).
- A self-hosted AI Gateway that shows **Active**.

## Step 1: Describe the sequence in Arazzo

Create a directory named `order-workflow`. It is a directory, not a file. Save
the Arazzo file and the three OpenAPI definitions inside it, so that the layout
looks like this:

```text
order-workflow/
├── order-workflow.arazzo.yaml
├── inventory-openapi.yaml
├── reservations-openapi.yaml
└── orders-openapi.yaml
```

The commands in this guide run from the directory that contains `order-workflow`.
Save the OpenAPI definitions with the file names that `sourceDescriptions` uses.

!!! note
    Give the Arazzo file a `.yaml` or `.yml` extension. Without an extension, the
    generator accepts the file, but the generated server fails when it starts.

The Arazzo file names the APIs, declares the inputs the sequence takes, and
lists the steps that run:

```yaml
arazzo: "1.0.0"

info:
  title: Place an Order
  summary: Check stock, reserve it, and create the order.
  description: Places an order for a customer after checking and reserving stock.
  version: "1.0.0"

sourceDescriptions:
  - name: inventoryApi
    url: inventory-openapi.yaml
    type: openapi
  - name: reservationsApi
    url: reservations-openapi.yaml
    type: openapi
  - name: ordersApi
    url: orders-openapi.yaml
    type: openapi

workflows:
  - workflowId: placeAnOrder
    summary: Check stock for a SKU, reserve it, and create an order.
    description: >
      Use this when a customer wants to buy a product. Provide the SKU, the
      quantity, and the customer identifier. The workflow returns the order
      identifier and its status, or ends without ordering if stock is short.
    inputs:
      type: object
      required: [sku, quantity, customerId]
      properties:
        sku:
          type: string
          description: The product identifier to order.
        quantity:
          type: integer
          description: How many units the customer wants.
        customerId:
          type: string
          description: The customer placing the order.

    steps:
      - stepId: checkAvailability
        description: Check how many units are in stock.
        operationId: checkStock
        parameters:
          - name: sku
            in: path
            value: $inputs.sku
        successCriteria:
          - condition: $statusCode == 200
          - condition: $response.body#/available >= $inputs.quantity
        outputs:
          available: $response.body#/available
        onFailure:
          - name: notEnoughStock
            type: end

      - stepId: reserveStock
        description: Reserve the requested quantity.
        operationId: reserveStock
        requestBody:
          contentType: application/json
          payload:
            sku: $inputs.sku
            quantity: $inputs.quantity
        successCriteria:
          - condition: $statusCode == 201
        outputs:
          reservationId: $response.body#/reservationId

      - stepId: createOrder
        description: Create the order against the reservation.
        operationId: createOrder
        requestBody:
          contentType: application/json
          payload:
            reservationId: $steps.reserveStock.outputs.reservationId
            customerId: $inputs.customerId
        successCriteria:
          - condition: $statusCode == 201
        outputs:
          orderId: $response.body#/orderId
          status: $response.body#/status

    outputs:
      orderId: $steps.createOrder.outputs.orderId
      status: $steps.createOrder.outputs.status
```

Each step in `steps` names an operation by its `operationId`, says what counts as
success, and captures the values later steps need.

### Add the OpenAPI definitions

The workflow calls three APIs, and the generator reads their OpenAPI definitions
from the same directory. The following three small definitions describe the APIs
that this walkthrough uses. If you have your own APIs, save their definitions
with the same file names and `operationId` values, or change the names in the
Arazzo file.

`inventory-openapi.yaml`:

```yaml
openapi: 3.0.3
info:
  title: Inventory
  version: "1.0.0"
servers:
  - url: https://inventory.example.com
paths:
  /stock/{sku}:
    get:
      operationId: checkStock
      parameters:
        - name: sku
          in: path
          required: true
          schema:
            type: string
      responses:
        "200":
          description: Units in stock.
          content:
            application/json:
              schema:
                type: object
                properties:
                  available:
                    type: integer
```

`reservations-openapi.yaml`:

```yaml
openapi: 3.0.3
info:
  title: Reservations
  version: "1.0.0"
servers:
  - url: https://reservations.example.com
paths:
  /reservations:
    post:
      operationId: reserveStock
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                sku:
                  type: string
                quantity:
                  type: integer
      responses:
        "201":
          description: Stock reserved.
          content:
            application/json:
              schema:
                type: object
                properties:
                  reservationId:
                    type: string
```

`orders-openapi.yaml`:

```yaml
openapi: 3.0.3
info:
  title: Orders
  version: "1.0.0"
servers:
  - url: https://orders.example.com
paths:
  /orders:
    post:
      operationId: createOrder
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                reservationId:
                  type: string
                customerId:
                  type: string
      responses:
        "201":
          description: Order created.
          content:
            application/json:
              schema:
                type: object
                properties:
                  orderId:
                    type: string
                  status:
                    type: string
```

Replace the `servers` URLs with the addresses where each API runs. The
container that you build in Step 3 calls these addresses, so they must be
reachable from inside the container.

Three syntax patterns pass data and direct execution between steps:

- `$inputs.sku` passes a caller-supplied value into a step.
- `$steps.reserveStock.outputs.reservationId` passes a value from an earlier step
  into a later one. This is what the agent no longer has to track.
- `onFailure` with `type: end` stops the workflow when a step's `successCriteria`
  aren't met. If stock is short, the workflow ends without reserving or ordering,
  and `orderId` and `status` come back empty. An `onSuccess` action with
  `criteria` runs only when its criteria match. Otherwise execution continues
  with the next step.

Validate before generating anything:

```bash
arazzo-mcp-gen validate -f ./order-workflow
```

!!! tip
    The workflow's `summary` becomes the tool description an AI model reads when
    it chooses a tool. Write it as guidance to a colleague, and keep it
    self-contained: the workflow `description` and the input `description`
    fields aren't exposed.

## Step 2: Generate the MCP server

```bash
arazzo-mcp-gen mcp-server generate -f ./order-workflow -p 5001 -o ./artifacts
```

This produces `mcp_server.py`, a `Dockerfile`, and a built Docker image, and it
prints the image name, which is `place-an-order-mcp-server` for this workflow.
Each workflow becomes one tool, so `placeAnOrder` becomes `place_an_order`.

## Step 3: Run the MCP server

```bash
docker run -d --name order-mcp -p 5001:5001 place-an-order-mcp-server
```

!!! note
    On macOS, the AirPlay Receiver uses port 5000, so these examples use port 5001.

Confirm it answers:

```bash
curl -X POST http://localhost:5001/mcp \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"probe","version":"1.0"}}}'
```

!!! warning "The server must be reachable from the internet"
    The console connects to this URL to fetch the tool list, and the gateway
    calls it at runtime, so a server on `localhost` won't work. The console
    shows `HTTP error! status: 403` for a `localhost` address.
    To give it a public address, deploy the image on Choreo. See
    [Develop a service with Docker](https://wso2.com/choreo/docs/develop-components/develop-services/develop-a-service-with-docker/).
    To test a server that runs on your machine, use a tunnel, as described in the
    next section.

### Expose a local server with ngrok

A tunnel such as [ngrok](https://ngrok.com/) gives a local server a public
`https` address. ngrok needs a free account and an authtoken. See the
[ngrok setup instructions](https://ngrok.com/docs/getting-started/).

1. Start a tunnel to the port of the server:

    ```bash
    ngrok http 5001
    ```

2. Copy the `https` forwarding address that ngrok prints, and add `/mcp` to the
   end, for example `https://<your-tunnel>.ngrok-free.dev/mcp`. Use this address
   as the **MCP Server Endpoint URL** in the next step.

Keep ngrok running while you use the server. The tunnel makes the server public,
so use it for testing only, and stop it when you finish.

## Step 4: Register the MCP server

1. In the left navigation menu, under **Resources**, select **MCP servers**.
2. Select **Register MCP server**.
3. Enter the following values:

    | Field | What to enter |
    |---|---|
    | **Name** | A name for the server, such as `Place an Order` |
    | **Version** | Pre-filled, editable |
    | **Context** | The base path for the server endpoint, such as `/place-an-order` |
    | **Description** | What the server exposes |

4. Under **Endpoints**, select **Add endpoint**.
5. In **MCP Server Endpoint URL**, enter your MCP server URL, ending in `/mcp`.
   The console connects to it and lists the tools it finds. Wait for
   `place_an_order` to appear before continuing.

    If your MCP server requires credentials, enter them under **Advanced
    Configurations** as headers before this step. The console uses them to fetch
    the tools.

6. Under **Deployment Configuration**, select the environment that your gateway belongs to. Open the gateway list that appears, and select your self-hosted gateway. The list defaults to the managed gateway, so change it.
7. Select **Add endpoint**, and then select **Create**.

## Step 5: Check the tool

The server's **Overview** tab lists the capabilities it exposes. One tool,
`place_an_order`, with the description you wrote in the workflow. Expand **Tools**
to see it. The **Manage Tools** chip shows `1 allowed · 0 disabled`.

Nothing here is typed into a form. The tool, its description and its schema all
come from the Arazzo specification.

## Step 6: Check the deployment

A server isn't reachable until it's deployed. Registering the server with a
gateway selected deploys it to that gateway.

1. Open the server's **Overview** tab.
2. Check the **Deployment** chip.

**Expected result:** The chip shows `Development · Deployed`.

The server endpoint follows this format:

```text
https://{gateway-host}/{server-context}/mcp
```

That endpoint is what an AI agent connects to. Every call passes through the
gateway, where authentication and policies apply, before the
workflow runs its three API calls.

## Step 7: Call the tool through the gateway

!!! warning "An MCP server requires an API key by default"
    The **Security** tab defaults to **API Key**, with the key in the `X-API-Key`
    header. The console issues keys to the agents that use the server as a tool.
    To test with `curl`, set **Method** to **None** on the **Security** tab,
    select **Switch method** to confirm, and select **Save**. Set it back to
    **API Key** when you finish.

Ask the gateway endpoint what tools it exposes:

```bash
curl -sk -X POST https://{gateway-host}/{server-context}/mcp \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}'
```

The command returns one tool named `place_an_order`, with `sku`, `quantity`, and
`customerId` as its required inputs. The schema comes from the Arazzo
specification.

## Troubleshooting

| Issue | Resolution |
|---|---|
| **Add endpoint** stays unavailable, or the console can't fetch the tool list | The URL must end in `/mcp` and be reachable from the internet. A `localhost` address fails with `HTTP error! status: 403`. Use a tunnel such as ngrok, as described in Step 3. If the server needs credentials, set them as headers under **Advanced Configurations**. |
| `arazzo-mcp-gen` reports an unresolved operation | An `operationId` in the workflow doesn't match any operation in the referenced OpenAPI definition. |
| A later step receives an empty value | The earlier step's `outputs` block doesn't capture the field, or the JSON pointer doesn't match the response body. |
| The tool returns an error | A step didn't reach its API. Check that the `servers` URL in each OpenAPI definition is reachable from inside the container. |
| The tool returns `orderId` and `status` as `None` | The workflow ended early, for example because stock was short, or a step didn't capture its output. Check the step `outputs` and `successCriteria`. |
| `HTTP 401` with `Valid API key required` | The server's **Security** method is **API Key**. Send an API key in the `X-API-Key` header, or set the method to **None** for testing. |
| The server exists but calls fail | Confirm that the **Overview** tab shows `Deployed` and that the URL uses the gateway's Public URL and the server's context. |
| The workflow ends without creating an order | Expected when stock is short. The `successCriteria` on the stock check fail, and `onFailure` ends the workflow. The result has empty `orderId` and `status`. |
| macOS blocks `arazzo-mcp-gen` | The released binaries aren't signed. Run `xattr -d com.apple.quarantine /usr/local/bin/arazzo-mcp-gen`, using the path where you saved the binary. |

## Next steps

- **Apply policies to the MCP server.** Use the **Manage Tools** tab for access
  control, and the **Policies** and **Rewrite** tabs for rate limiting and
  request changes.
- **Add more workflows.** Each one becomes another tool.

## Try the sample

The companion sample runs this setup locally using a self-hosted gateway, so you
can generate an MCP server from an Arazzo workflow and call it through a gateway
without a cloud account.

[View the sample on GitHub](https://github.com/wso2/api-platform/tree/main/samples/rest-to-mcp).
