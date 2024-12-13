## Introduction

Storacha is a decentralized hot storage protocol built atop Decentralized Storage Networks (DSNs). It aims to offer a marketplace for high-performance (hot) storage and retrieval services, complementing existing archival (cold) storage solutions such as Filecoin. By leveraging a token-based economy (the $Storacha token) and robust cryptoeconomic incentives, Storacha seeks to create a sustainable, open, and composable environment where supply-side service providers (nodes) and demand-side users (business customers) interact in a trust-minimized manner.

Key system goals:

1. **Market Efficiency:** Allow supply and demand for hot storage and retrieval services to meet in a decentralized marketplace.
2. **Incentive Alignment:** Ensure that service providers are rewarded for meeting quality-of-service (QoS) standards, and that dishonest or low-performance providers are penalized.
3. **Scalability & Stability:** Transition from initial token-based inflationary rewards toward a steady-state economy driven primarily by user fees over time.
4. **Secure & Verifiable Operations:** Use cryptographic proofs, on-chain commitments, and random spot checks to ensure correct node behavior and prevent fraud.

---

## System Architecture

### Stakeholder Types

- **Active Supply Participants:**

  - **Object Storage Nodes (OSNs):** Store customer data and serve it on-demand. They earn rewards for reliably storing and retrieving data.
  - **Retrieval Query Nodes (RANs):** Serve retrieval requests from customers quickly, often caching data for improved latency. They earn rewards based on bytes served and cache hit rates.
  - **Indexing Nodes (INs):** Maintain an index of where content is stored and serve indexing queries. They earn rewards for availability and correctness.
  - **Fisherman Nodes (FNs):** Verify correct behavior of OSNs, RANs, and INs through random checks. They earn a share of slashed collateral when they detect fraud.

- **Demand-Side Participants:**

  - **Customers (Businesses):** Pay for storage and retrieval services on behalf of their end-users. They fund sessions that specify load parameters (storage, read/write bandwidth, duration).
  - **End Users:** The ultimate consumers of the data. Their requests drive retrieval operations.

- **Passive Participants:**
  - **Token Holders, Foundation/Treasury:** Benefit from fee allocations and token value appreciation. The Foundation may fund R&D, cover dispute insurance, and govern parameter adjustments.

### Core System Components

1. **Storage Layer:**  
   OSNs commit storage capacity and maintain available, retrievable data.
2. **Retrieval Layer:**  
   RANs handle requests, caching frequently accessed content, and ensuring low-latency data delivery.

3. **Indexing Layer:**  
   INs maintain and serve directory information about which OSNs hold which data.

4. **Verification Layer:**  
   FNs and cryptographic proofs confirm that data is correctly stored, served, and indexed. They verify logs and issue challenges to detect dishonest behavior.

5. **Economic Layer (Tokenomics):**  
   The $Storacha token aligns incentives, provides collateralization for service nodes, and serves as a medium for rewards and, optionally, payment. Users may pay fees in stablecoins or $Storacha, with stablecoin pricing ensuring predictable costs.

---

## Economic Mechanisms

### Token Supply and Allocation

- **Maximum Supply:**  
  Up to 100 billion $Storacha tokens can ever be created.
- **Allocations:**  
  A portion is set aside for node incentives, the Treasury/Foundation, early contributors, and investors. Approximately 23% of tokens are earmarked for incentive emissions to nodes (over time).

### Incentive Structure

- **Dual Component Rewards:**

  - **Deterministic (Base) Minting:** A time-based, decaying issuance that bootstraps early network participation.
  - **KPI-Based Minting:** Rewards tied to Key Performance Indicators, such as bytes stored (OSNs), bytes read (RANs), and indices served (INs). Each node type’s KPI-based component is independent, ensuring that rewards track the real “work” done.

- **Staking Requirements:**  
  Nodes must stake $Storacha tokens to participate, providing collateral that can be slashed if they behave dishonestly. Minimum stake grows with network usage and token supply, ensuring skin-in-the-game and deterring Sybil attacks. Rewards earned by nodes are auto-staked, locking them in and reinforcing honest participation.

- **Slashing Penalties:**  
  Nodes that commit offenses (serving wrong content, log fraud, unavailability, etc.) can lose some or all of their staked tokens. Slashed funds are split between the Treasury and the Fisherman node that detected the malfeasance.

### Session-Based Pricing

- **Fee Determination:**  
  Customers pay session fees based on projected resource usage over a chosen duration: storage load (bytes), read/write rates (bytes/second), and expected number of requests. Prices may incorporate discounts for longer sessions and scale with network utilization.

- **Stable Denomination:**  
  Fees are denominated in stable, fiat-pegged units (e.g., USD) for predictability. Customers can pay in stablecoins or $Storacha. Conversions occur at market rates, ensuring that fundamental cost modeling remains stable.

- **Revenue Allocation (Fee Splits):**  
  Collected fees are allocated among the Treasury, service providers, and token holders (possibly via token burning). Over time, the system aims to reduce reliance on inflationary rewards and increase revenue sourced from fees.

---

## Technical Constructs and Verification

### On-Chain Commitments

All incentivized nodes submit merkleized logs on-chain each epoch, which include data about bytes stored or served. A challenge period allows Fisherman nodes or others to dispute fraudulent claims before finalizing rewards.

### Cryptographic Proofs

- **Proof of Retrieval:** Ensures that RANs and OSNs actually served the requested data correctly.
- **Proof of Data Possession:** Ensures that OSNs indeed hold the data they claim to store.
- **Random Checks by Fisherman Nodes:** On-chain or semi-on-chain verifications challenge nodes to prove correctness. If a node fails, it is subject to slashing.

### Reputation Systems (Optional Initial Phase)

While not mandatory at network launch, reputation metrics—like TTFB (Time to First Byte), TTLB (Time to Last Byte), uptime, and past slashes—may be used to rank nodes, influence routing decisions, and guide which nodes earn more traffic and rewards.

---

## Governance and Parameter Tuning

Storacha’s parameters—inflation rates, fee splits, staking requirements, slashing penalties, and KPI weighting—can be adjusted via governance processes. This allows flexibility to respond to market conditions, usage patterns, and learnings from simulations and real-world operations.

Key governance decisions include:

- Adjusting inflation down as customer payments scale up.
- Tweaking fee allocation vectors to ensure long-term sustainability without over-inflation.
- Altering minimum staking requirements to balance security and accessibility.

---

## Market Dynamics and Stability

### From Bootstrap to Maturity

Initially, the network issues a higher portion of inflationary rewards to incentivize early node participation and capacity building. As the network matures, customer fees become increasingly important, enabling a phase-out of heavy inflation and stabilizing token supply growth. Eventually, node profitability should depend primarily on user-paid fees rather than token issuance.

### Discouraging Self-Dealing

The system aims to prevent manipulative behaviors (e.g., nodes generating fake requests) by capping token rewards per epoch, verifying logs, and employing Fisherman nodes to detect collusion or fake traffic. Stake and slashing ensure the cost of cheating outweighs potential benefits.

### Sybil Resistance and Free Tiers

Limited free-tier sessions might be offered to attract early users. However, careful caps and controls are needed to prevent Sybil exploits. Staking minimums, rate-limiting free accounts, and reputation-based throttling are potential solutions.

---

## Modeling and Simulation

Before final parameter selection and launch, the Storacha team plans simulations to validate the system’s economic soundness:

- **Token Issuance and Inflation Modeling:**  
  Project issuance curves over 10+ years under various growth scenarios.

- **Utilization and Capacity Dynamics:**  
  Evaluate how changes in network usage (e.g., storing 1 Exabyte of data, achieving 100 Tbps capacity) affect node profitability, token circulation, and fee prices.

- **Market Cycles and Token Price Stability:**  
  Test sensitivity to token price swings and economic downturns, ensuring that node profitability and user fees remain stable.

- **Transition Points:**  
  Identify the point where fee-based revenues surpass token issuance, ensuring that bootstrapping periods are well-calibrated.
