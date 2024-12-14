# Storacha Cryptoeconomics Litepaper

## Abstract

Decentralized storage networks (DSNs) look to introduce an algorithmic and competitive market for cloud-based storage services as a credible alternative to current data storage offerings. The Storacha protocol aims to build on the economic primitives of foundational DSN’s to implement robust hot storage features on top of existing archival capabilities. This marketplace will be facilitated by the protocol’s native token `$Storacha`, which will be engineered to bootstrap productive activity and protocol development and facilitate value flows amongst service providers and users. We present a high-level system design for the protocol’s incentive model and cryptoeconomic constructions.

## Token Allocation

A maximum of N= 100,000,000,000 `$Storacha` tokens can ever be created. The figure below summarizes the token allocations amongst key stakeholder groups.

## Incentivized Actors

Storacha will have a number of protocol-incentivized actors contributing to its distributed storage and retrieval protocol. These groups are defined below:

### Object Storage Nodes

Store a blob of data of arbitrary size for a specified amount of time. They must make it available for retrieval and commit relevant logs of their activity.

### Retrieval Query Nodes

Find and serve retrieval queries and cache results. They read from indexers and object storage nodes on a cache miss and commit logs of bytes served.

### Indexing Nodes

Index which storage node contains which content and serve indices upon request.

### Fishermen Nodes (run by external network: Station)

Verify in random checks that the above incentivized nodes are honestly performing their specified functions.

### Treasury

The figure above details a high-level overview of protocol-mediated value flows between these incentivized actor groups and protocol users.

## Minting, Collateral, and Slashing/Challenger Modules

The below sections discuss the Minting, Collateral, and Slashing/Challenger Modules in greater detail.

### Minting and Rewards

Many blockchains will mint service provider tokens on a simple, deterministic decay model. However, this can disproportionately reward early nodes relative to the unit of work they provide. Therefore, the protocol should aim to adequately reward early participants whilst also indexing reward disbursement to the network's work output and utility.

Per the Token Allocation given in Figure 1, the Storacha protocol expects to release a maximum of 23% of its total project token supply to its incentivized nodes/service providers. We denote `M` as the total asymptotic maximum number of tokens to be emitted as rewards for the protocol's incentivized nodes. This minting supply can be directed based on the fundamental units of work for the protocol.

Storacha will implement a KPI-based minting schema in the following manner (briefly summarized below).

```math
M(t) = MS(t) + MB(t)
```

where `M(t)` is the total number of tokens emitted as expected block rewards up until time `t`. `MS(t)` is the number of tokens emitted via simple minting and is deterministic. `MB(t)` is the number of tokens emitted via some KPI-based minting schema. Note,

```math
M = MS + MB
```

where `MB = α * M` and `0 < α < 1`.

Storacha can implement this mechanism in order to better direct rewards in a cooperative game theoretic fashion. However, the Storacha protocol will reward a number of different actors and their respective functions. Whereas other DSNs that have implemented this schema have only one fundamental unit of work (bytes sealed and stored), the Storacha protocol will reward a number of work units, enumerated below:

- **Bytes stored** (Object Storage Nodes)
- **Bytes read** (Retrieval Query Nodes)
- **Number of indices served/stored** (Indexing Nodes)

Given that there are a number of different work units, a set of independent KPI-based minting functions specific to each actor type may be able to maintain the simplicity of each individual KPI-based mechanism but still productively direct incentives. We can denote these simply as:

- `KPI1(t)`
- `KPI2(t)`
- `KPI3(t)`

Where `KPI1(t)` is indexed to bytes written/stored, `KPI2(t)` is indexed to bytes read/served over some average duration, and `KPI3(t)` to data indexing.

Each node type will be disbursed rewards relative to their respective KPI function. We introduce `wi` to denote the percentage of `M` each protocol incentive-based actor type is expected to receive, where ∑`wi` = 1. This also implies a parameterization exercise for `wi` each node type, which should be a function of the relative economic value/cost of each fundamental work unit.

As a result, each node type will have its own bespoke Minting Function:

```math
Mi(t) = wi * MS(t) + MBi(t)
```

where `MBi(t)` is a function of the relevant `KPIi(t)` function. The general minting expression for the economy `M(t)` is now as follows:

```math
M(t) = MS(t) + ∑MBi(t)
```

Each service provider node should then receive rewards proportional to its individual contribution to the total work done across all service providers of the same type (with the units of work denoted by the respective KPI function). So, an individual provider's cumulative rewards `Ri` over time `T` should be:

```math
Ri(T) = ∫₀ᵀ wi(t) Wi(T) dt
```

### Collateral and Slashing Penalties

Storacha actors must commit resources in order to participate in the economy, both via hardware dedication for storage/retrieval and through staked `$Storacha` tokens. Whereas the protocol utilizes inflationary rewards as a positive incentive for honest participation, it can utilize stake to penalize malicious, dishonest, and adverse behavior via slashing.

Each node type will have a minimum pledge amount `pi` required to provide storage/retrieval services and receive inflationary network rewards. This minimum pledge should be dynamic and a monotonically increasing function of tokens `S` in circulation as well as work capacity committed. Whenever more tokens are present in circulation, the minimum pledge to commit additional work capacity should increase accordingly.

```math
pi(t) = Fi(S(t), w(t))
```

where `w(t)` is the additional amount of work capacity committed at time `t`.

This minimum pledge `pi` is a prerequisite for any node type to participate and store/serve data in the Storacha economy. However, nodes can increase their stake in order to increase the amount of resource provisioning they supply to the network (and therefore, their rewards). This implies that the total collateral committed `C` for a service provider will be as follows:

```math
C(t) = ∫₀ᵀ pi(t) dt
```

This collateral is also utilized to protect and ensure each node's verifiable on-chain commitments.

The protocol (via cryptographic proofs), Fisherman nodes, and/or trusted nodes check these offenses, which verify in random checks that the incentivized nodes are honestly performing their specified functions. Upon a successful challenge, a node will be slashed out of its existing collateral balance where the slashing Penalty `Pi` is a function of the offense type `o` and committed work `w`.

```math
Pi = F(o, w)
```

These slashed funds are then split between the Storacha Treasury and the Fisherman node which uncovered the slashable offense.

## Token Value Capture and User Payments

Previous sections of the document explore Storacha's sources and sinks from a service provider's perspective. In this note, we begin an initial exploration of the main components of Storacha's token value accrual model via demand-side pressure from users. Inflationary pressure is introduced via token rewards for incentivized actors. Deflationary pressures, or "sinks," serve as value accrual mechanisms by which all existing token holders benefit.

Understanding the demand-side sinks is directly tied to defining Storacha's business model: What product is it selling that eventually users will be paying to consume? Also, who are these direct users paying for the product?

We summarize the following below:

- Storacha's most direct users are businesses that demand hot storage and retrieval services for their respective customers.
- The resources that are orchestrated and sold by the Storacha protocol for these users are (bytes) and bandwidth (bytes read/written per some unit of time).
- Traditionally, protocol revenue is collected via transaction fees (use of blockspace as a scarce commodity). However, blockspace is not the resource that Storacha sells. Therefore, we propose that usual transaction fees is not the most appropriate way to collect revenue, but propose instead a new Session fee for both storage and retrieval.

### Session Pricing

Here we describe a session-based pricing model, in which a session is defined as a duration for which a user demands protocol services. Suppose each business that wants to use the Storacha first needs to inform the protocol of their projected protocol resource usage (storage, retrieval, write). The expected Storage Load, `S`, Read Rate, `R`, and Write Rate, `W`, in units of [bytes]/[time], and an expected Session duration, `T`, in units of [time], which is the amount of time for which the session will maintain this Storage load and read/write load.

Each service (Storage, Read, and Write) places some resource burden on the protocol and its service providers. We can denote the cost of storage, read, and write as `Cs`, `CR`, `CW`.

The Session fee should increase monotonically with each load type and with the session duration, but not necessarily linearly in both. Suppose the price is based on the resource usage the session will impose on the collection of Storacha node providers, then this would look like:

```math
P = ∫₀ᵀ Cs S dt + ∫₀ᵀ CR R dt + ∫₀ᵀ CW W dt
```

which reduces simply to

```math
P = T * (Cs * S + CR * R + CW * W)
```

We then scale `P` by a function of the expected frequency `F(f)` of protocol requests and modify the pricing function above:

```math
P = F(f) * T * (Cs * S + CR * R + CW * W)
```

For the sake of brevity, we denote each resource load type as `Li` and each associated cost burden as `Ci`. The equation above can then be simplified to

```math
P = F(f) * T * ∑(Li * Ci)
```

However, longer sessions may be given a discount, for which we can introduce some discount function `d(t)`.

```math
P = ∑[Ci * 0T * Li * di(t) dt]
```

In particular, if we use some exponential discount factor `di(t) = (1 - i)^t`.

```math
P = F(f) * ∑[Ci * Li * (1 - i) * ((1 - i)T - 1)]
```

Note that because providers' costs are largely denominated in stable fiat currencies and users demand relative predictability in pricing, the protocol should be denominated in a fiat stable currency (e.g., USD). Users' payments can, however, be in either native `$Storacha` or a stablecoin equivalent. However, this should not markedly alter how value accrues to the protocol and/or to its participants.

### Underestimation Fees and Collaterals

Note that the pricing formula above is given in terms of the estimated "load" on the protocol and duration, which is an estimate that the user has to make at the start of the session.

The user may end up sending a higher transaction workload than was proposed. In this case, it would be necessary to add fees, given that the user underestimated their transaction workload.

When the transaction throughput is larger than expected, there are two options:

1. The session may be terminated by the Storacha protocol if there are no more funds available.
2. The users can lock an amount of collateral together with their session, from which underestimation fees may be drawn, and the session can continue running smoothly.

### Allocating Protocol Revenue

The goal of the revenue from these fees is to accrue value to token holders (or to the treasury). They could then either be burnt, to create deflation to benefit holders or distributed directly amongst token holders, service providers, and the Storacha Treasury.

We denote `vi` the portion of collected fees `F` that is distributed to each stakeholder group (treasury, service providers, and token holders via burning) where ∑`vi` = 1.

Therefore, each stakeholder group receives economic value from `vi * F` tokens. Note, if we choose to directly benefit token holders, then we may consider burning all funds received from session fees. However, this does not directly compensate service providers for work done. Given that the eventual goal is to reduce and eliminate node provider dependence on inflationary protocol rewards, there is a mathematical optimization problem here in determining the appropriate weight vector `v` to allocate session pricing revenue amongst economic actors.

## Conclusion

The Storacha protocol is a necessary component to realize a truly algorithmic, decentralized, and open market for cloud-based storage and retrieval services. The economic model is designed to sustainably and fairly reward service providers, whilst offering users competitive and stable price offerings for storage and retrieval services. The next steps in token model design and development will be to model, simulate, test, and parameterize the above cryptoeconomic constructions.

## Further Work, Simulation, Modeling and Parameterization

- Simulate how inflation will develop over a minimum of 10 years on the assumption that we will have 100 Tbps capacity with a utilization rate of 80% and store 1 Exabyte of data. Make variations of these assumptions. Assume one node can serve 1 Gbps and store X.
- Simulate network growth over 10 years with the impact on customer price, number of nodes on the network, node profitability, tokens issued per year, tokens staked, tokens circulating, tokens issued per unit of work.
- Simulate a minimum token price for node profitability per type of node per year assuming economic cycles.
- Simulate when the network needs to reach more rewards coming from customers vs token issuance.
- Simulate the amount of tokens the treasury can accumulate as part of network fees over time.
