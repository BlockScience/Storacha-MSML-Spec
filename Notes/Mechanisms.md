## 1. Base Minting/Inflation Mechanism

**Name:** Base Minting/Inflation Mechanism  
**Description:** Controls time-based (deterministic) token issuance to incentivized nodes, especially in early stages of the network, ensuring they receive baseline rewards even before robust demand-side revenues materialize.

### Constraints

- Must adhere to a maximum token supply cap
- Emission schedule should decrease over time to avoid perpetual high inflation

### Logic

- Periodically emit a predefined amount of tokens
- Token emission rate reduces as time progresses, often following a decay function

### Domain

- Protocol-level, affecting all incentivized nodes (OSNs, RANs, INs, and indirectly FNs)

### Parameters Used

- Initial emission rate
- Half-life or decay parameters
- Epoch length

### Updates

- Increases total token supply at each emission interval
- Updates node reward balances proportionally to their share of network participation

---

## 2. KPI-Based Minting Mechanisms

**Name:** KPI-Based Minting Mechanisms  
**Description:** Allocates rewards based on measurable work done (bytes stored, served, indices maintained), aligning incentives with actual network utility.

### Constraints

- Reliable KPI measurement is required
- Total KPI-based rewards are limited and must not exceed predetermined caps

### Logic

- Define KPI functions (e.g., for storage: bytes stored over a period)
- Calculate each node’s share of total KPI and allocate rewards accordingly

### Domain

- OSNs (bytes stored), RANs (bytes served), INs (indices served/stored), and potentially FNs (based on number of checks)

### Parameters Used

- Weight factors `w_i` for each node type
- KPI scaling parameters
- Normalization factors

### Updates

- Periodically updates node token balances based on their proportional contribution to total network work

---

## 3. Staking and Collateral Commitment Mechanism

**Name:** Staking and Collateral Commitment Mechanism  
**Description:** Requires nodes to lock tokens as collateral to ensure honest participation and deter malicious behavior. Rewards earned are often auto-staked, with portions locked/unlocked over time.

### Constraints

- Minimum stake increases with network usage and token supply
- Nodes must stake before participating and earning rewards

### Logic

- Compute minimum required collateral as a function of token supply and committed capacity
- Automatically stake rewards, partially locking them to ensure long-term alignment

### Domain

- OSNs, RANs, INs must meet staking requirements

### Parameters Used

- Staking formula parameters (e.g., function of circulating supply, pledged capacity)
- Unlock periods
- Locked/unlocked proportions

### Updates

- Adjusts a node’s staked balance as capacity or network size changes
- Updates locked/unlocked stake portions as time passes and conditions are met

---

## 4. Slashing/Challenger Mechanism

**Name:** Slashing/Challenger Mechanism  
**Description:** Penalizes dishonest or underperforming nodes by reducing their collateral stake. Fisherman nodes issue challenges, and if proven correct, the offender is slashed.

### Constraints

- Requires verifiable proofs of misconduct
- Must have a dispute resolution process and possibly insurance/compensation funds for false positives

### Logic

- Fishermen randomly check logs, data, or proofs
- On detecting a violation (e.g., serving wrong content), initiate a slash

### Domain

- Applies to OSNs, RANs, INs; Fishermen nodes enforce honesty checks

### Parameters Used

- Offense severity parameters
- Slash amounts or percentages
- Challenge intervals
- Dispute resolution criteria

### Updates

- Decreases collateral of guilty nodes
- Increases Fishermen’s and Treasury/Foundation holdings by slashed amounts
- May trigger compensation from an insurance fund if a slash is overturned upon dispute

---

## 5. Session-Based Pricing Mechanism

**Name:** Session-Based Pricing Mechanism  
**Description:** Calculates user fees based on projected storage, retrieval rates, and session duration. This ensures that users pay proportionally to resource usage.

### Constraints

- Requires accurate estimations of resource consumption
- Must remain stable and predictable, potentially denominated in a stable currency

### Logic

- Compute price `P = T * (Σ L_i * C_i) * F(f)` where:
  - `L_i` are loads (e.g., bytes stored)
  - `C_i` are costs
  - `F(f)` is a frequency factor
- Optionally apply duration-based discounts

### Domain

- Interactions between users/customers and the protocol’s resource provisioning

### Parameters Used

- Storage/read/write cost parameters
- Discount functions
- Frequency scaling factors

### Updates

- Sets required upfront payment for sessions
- Adjusts user balances and protocol fee pools based on actual usage and session length

---

## 6. Fee Allocation Mechanism

**Name:** Fee Allocation Mechanism  
**Description:** Distributes collected fees among various stakeholders such as the Treasury/Foundation, service providers, and possibly token holders (via burns or direct dividends).

### Constraints

- Allocation ratios must sum to 1
- Policy may evolve as network matures (less reliance on inflation, more on fees)

### Logic

- On each fee collection event, split fees according to predefined fractions
- Direct portions to treasury, node reward pools, and possibly burn some to reduce supply

### Domain

- Protocol-level economics, affecting all stakeholders

### Parameters Used

- Fee split ratios (`v_i`)
- Burn percentages
- Treasury allocation parameters

### Updates

- Transfers allocated funds to respective accounts
- Potentially decreases total supply if burning is employed

---

## 7. Session Duration Discount Mechanism

**Name:** Session Duration Discount Mechanism  
**Description:** Provides cost incentives for longer sessions by applying discount factors over time, encouraging stable, long-term usage.

### Constraints

- Discounts must not undermine cost coverage
- Longer sessions should still be profitable for providers

### Logic

- Apply a discount function `d(t)` to progressively reduce per-unit costs as `T` grows

### Domain

- Customer-facing pricing layer

### Parameters Used

- Discount rate or function parameters
- Session length `T`

### Updates

- Reduces computed session fees for longer durations
- Adjusts payment requirements accordingly

---

## 8. Underestimation Fee/Collateral Mechanism

**Name:** Underestimation Fee/Collateral Mechanism  
**Description:** Ensures that if a customer uses more resources than initially estimated, additional fees can be charged from locked collateral or the session may be terminated.

### Constraints

- Must have sufficient collateral or the session ends
- Requires usage monitoring to detect overages

### Logic

- Compare actual usage with estimates
- If usage exceeds paid capacity, deduct additional fees from collateral or halt service

### Domain

- User sessions and protocol’s resource enforcement layer

### Parameters Used

- Overage fee rates
- Collateral thresholds
- Termination conditions

### Updates

- Increases fees collected if over-limit usage occurs
- Potentially terminates the session if collateral is insufficient

---

## 9. Governance & Parameter Tuning Mechanism

**Name:** Governance & Parameter Tuning Mechanism  
**Description:** Allows community or designated authorities to adjust protocol parameters (inflation rates, fee splits, staking requirements) over time.

### Constraints

- Subject to on-chain voting, proposal thresholds, and time delays
- Parameter ranges are typically bounded

### Logic

- Parameters are modified through governance proposals and voting
- Once accepted, updated parameters are applied

### Domain

- Protocol-level, impacting all economic and operational layers

### Parameters Used

- Governance rules (quorum, supermajorities)
- Adjustable economic parameters (`w_i`, `v_i`, inflation rates)

### Updates

- Alters system parameters stored on-chain
- Changes how other mechanisms compute rewards, fees, and stakes

---

## 10. Fisherman Verification Mechanism

**Name:** Fisherman Verification Mechanism  
**Description:** Fisherman nodes randomly challenge and verify the correctness of logs, data availability, and retrieval performance of other nodes.

### Constraints

- Must have unbiased random selection of nodes to check
- Requires cryptographic proofs and on-chain verification

### Logic

- Periodically select nodes and request proofs of correct behavior
- If a node fails, initiate the slashing process

### Domain

- Interactions between Fishermen and OSNs, RANs, INs

### Parameters Used

- Sampling frequency
- Challenge complexity
- Verification difficulty

### Updates

- Triggers slashing if misconduct is proven
- Helps maintain network honesty and reliability

---

## 11. Treasury/Reserve Mechanism

**Name:** Treasury/Reserve Mechanism  
**Description:** Accumulates funds from fees, slashing, or allocated rewards to support ecosystem growth, insurance/dispute settlements, and R&D.

### Constraints

- Controlled spending via governance
- Transparent accounting required

### Logic

- Collect a portion of revenues and slashed funds in a treasury pool
- Disburse funds for community-approved initiatives or compensation

### Domain

- Protocol-level financial management

### Parameters Used

- Allocation ratios for treasury
- Policies for spending and insurance

### Updates

- Increases treasury balance as funds accumulate
- Decreases when spending proposals pass or compensation is paid out

---

## 12. Stable Pricing and Conversion Mechanism

**Name:** Stable Pricing and Conversion Mechanism  
**Description:** Maintains stable, fiat-referenced pricing for storage and retrieval to ensure cost predictability. Converts `$Storacha` payments to a stable equivalent using oracles.

### Constraints

- Requires reliable price oracles
- Must handle exchange rate fluctuations gracefully

### Logic

- When users pay in `$Storacha`, convert tokens to stable-value units (e.g., USD) at the current rate
- Fees are calculated in stable units to avoid volatility issues

### Domain

- Customer payment process and fee accounting layer

### Parameters Used

- Exchange rate oracle parameters
- Token price feed intervals

### Updates

- Adjusts the amount of `$Storacha` tokens required based on current exchange rates
- Stabilizes the effective cost for customers

---

## 13. Data Indexing & Routing Mechanism

**Name:** Data Indexing & Routing Mechanism  
**Description:** Ensures that retrieval queries can locate the correct Object Storage Nodes that hold requested data, improving efficiency and reliability.

### Constraints

- Indices must be correct and up-to-date
- Retrieval queries rely on indexing nodes to find content quickly

### Logic

- Indexing nodes maintain mappings from content identifiers to storage nodes
- Retrieval nodes consult indices to route requests efficiently

### Domain

- Interactions between INs, RANs, and OSNs

### Parameters Used

- Update intervals for indices
- Indexing storage capacity limits

### Updates

- Refreshes and maintains index tables, guiding retrieval requests
- Improves performance and reliability of data retrieval

---

## 14. Proof-of-Data-Possession & Proof-of-Retrieval Mechanisms

**Name:** Proof-of-Data-Possession & Proof-of-Retrieval Mechanisms  
**Description:** Provide cryptographic evidence that nodes actually hold the data they claim (PoDP) and have served it correctly (PoR).

### Constraints

- Proofs must be efficiently verifiable on-chain or off-chain with commitments
- Challenges must detect dishonest behavior with high probability

### Logic

- Nodes submit cryptographic proofs
- Fisherman nodes or the protocol verify proofs; failure leads to slashing

### Domain

- OSNs and RANs primarily, also relevant to indexing correctness

### Parameters Used

- Challenge complexity
- Proof sizes
- Cryptographic parameters

### Updates

- Confirms honest storage/retrieval to enable reward disbursement
- Detects fraud to trigger slashing if proofs fail

---

## 15. Node Reputation & Ranking Mechanism (Future/Optional)

**Name:** Node Reputation & Ranking Mechanism (Future/Optional)  
**Description:** Assigns reputation scores to nodes based on performance metrics (availability, latency, correctness), potentially influencing routing and rewards.

### Constraints

- Must have reliable and tamper-resistant metrics
- Avoids centralization by ensuring fairness in scoring

### Logic

- Aggregate performance data over time
- Compute reputation scores and possibly weight rewards or route requests accordingly

### Domain

- Protocol optimization for routing decisions and reward distribution

### Parameters Used

- Performance thresholds (TTFB, TTLB, uptime)
- Weighting schemes for metrics

### Updates

- Adjusts request routing, potentially influencing reward allocation indirectly
- Encourages sustained good behavior from nodes

---

## 16. Session Termination & Resource Enforcement Mechanism

**Name:** Session Termination & Resource Enforcement Mechanism  
**Description:** Ends sessions once prepaid resources are consumed or session duration expires, preventing free-riding.

### Constraints

- Must accurately track resource consumption vs. prepaid allocations
- Clear rules for when and how to terminate service

### Logic

- Monitor ongoing resource usage
- If usage exceeds prepaid amount or time is up, terminate session or require top-up

### Domain

- Customer sessions and node resource management

### Parameters Used

- Termination thresholds
- Grace periods
- Notification intervals

### Updates

- Halts resource provisioning once conditions are met
- Enforces economic balance between paid resources and consumption
