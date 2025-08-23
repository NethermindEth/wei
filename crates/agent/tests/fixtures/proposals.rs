// Fixed proposal strings with proper Rust syntax

pub fn get_proposals() -> Vec<&'static str> {
// Proposal 1 - Arbitrum Hackathon Continuation Program
let proposal_1 = r#"Abstract
Arbitrum lacks an efficient mechanism to swap funds for projects, which has led to multiple challenges for service providers around token price changes. Specifically, the Hackathon Continuation Program is currently underfunded by $89,980 USD due to token price drop before RnDAO received any funds.

Beyond usual market risks, the program faced prolonged market risks due to delays as we worked with the Arbitrum Foundation on an improved fund management system for DAO-led investments, creating a valuable process template for the Arbitrum ecosystem, but exposing us to this situation.

This proposal suggests using a portion of the Domain Allocator (i.e. Questbook grant program) funds left over from the season 1 (a bit over $200k, due to be returned to the DAO) to "top up" the Hackathon Continuation Program and allow it to continue as approved by the DAO.

We'll also propose an option in the vote for the remaining funds from the Domain Allocator season 1, to be sent to the Treasury Management Committee to increase their stablecoin pool. Said pool could be used by service providers in the future to cover shortfalls as per a process to be designed by the TMC (see their first draft here).

Rationale
What's the current status and why did the shortfall happen?
The Hackathon Continuation Program is divided into two phases, with separate payments for each. The MSS holds enough funds to complete payments for projects in Phase 1 of the program and has some USDC remaining for Phase 2 but not enough to complete the program.

The complexity of this specific initiative (the first investment program setup via the DAO) meant we needed to figure out a system for fund management for investments. The initial approach proposed would have required additional bureaucracy (register RnDAO signers and the RnDAO multisig setup for project investments as part of the AF) and so, in cooperation with the Foundation, we devised an improved approach that would see RnDAO scheduling payments directly on the MSS while the MSS signers would approve payments.

The system devised can be used moving forward to facilitate future investment programs, unlocking a valuable milestone for the DAO to test investments and improve the ROI of ecosystem development programs. However, the money requested was to be paid in stables, and the conversion didn't happen immediately.
Seeing the market drop, in coordination with the AF, RnDAO tried to delay the swapping of funds as long as possible to allow for a market recovery; unfortunately, the price didn't recover in time, and it was required to swap at a reduced token price to meet the program obligations for Phase 1. Leading to a budget shortfall for Phase 2.

Advancing the program is time-sensitive, as the projects are now expecting the funding and support to progress. Any further delays could cause them to fail or migrate to other ecosystems.

Is this a precedent?

The funds left over from Season 1 of the Domain Allocator programs are due to be returned to the DAO. Authorising a transfer to the MSS for usage in the Hackathon Continuation Program (HCP) (while the rest of the funds are sent to the DAO/AF) would be a one-time action that would provide timely reassurance to the HCP projects. Given that the rest of the funds would be returned, this approach would not become a recurring mechanism in the DAO.

What about the Domain Allocator programs?

Both programs follow the same objective of supporting builders in Arbitrum.

The approach proposed in this proposal was suggested by @jojo as a viable route, given the small sums needed and the availability of the funds.

What about the Treasury Management Committee and the checking account?

The TMC V 1.2 proposal sets $ 15 million USD equivalent to be converted to Stables and serve as a reserve for service providers. The TMC has proposed a mechanism based on using the yield of this reserve, which will take time to accrue. As such, the proposed strategy can cover a short-term gap in the proposed mechanism.

Calculation of the exact amount:

As per the AF post (Hackathon Continuation Program - #149 by Arbitrum), 2 Arb were left after Phase 1. However, having eliminated one project that underdelivered from Phase 1, we have saed an additional $12k (held in the MSS). Bringing the shortfall for Phase 2 to: $101,980 - $12,000 = $89,980 USD.

Specifications
This proposal authorises the transfer of $89,980 USD of the leftover funds from the Season 1 Domain Allocator program's SAFE, to the Arbitrum Foundation, and from the AF to the MSS for the Hackathon Continuation Program.
This transfer route was selected for compliance reasons.

Addtionally, an option to send the leftover funds (after covering the 89k needed for the Hackathon Continuation program) to the Arbiturm Foundation and from there to the Treasury Management Committee.

Budget
No additional funds from the DAO are needed. Just the authorisation to use the leftover from Domain Allocator season 1.

Voting options
A. only top-up the HCP: top-up the HCP and leftover funds to the DAO
B. yes to both: top-up the HCP and leftover funds to the TMC
C. againts:all funds to the DAO (don't top-up the HCP nor TMC)
D. abstain"#;

// Proposal 2 - Arbitrum Events Budget
let proposal_2 = r#"Non-Constitutional
Key Changes Made on July 23, 2025
The 2025 Events Budget will no longer be dissolved, and instead funds will be moved to a yield bearing account managed by the Arbitrum Foundation/treasury managers. The Events Budget process will remain as currently structured until the end of 2025.

Abstract
Entropy proposes transferring the DAO's 2025 Events Budget (~1.04M USDC) to the ATMC, which will top-up the budget allocated to onchain treasury managers focused on stablecoin strategies. The Events Budget will continue to operate as designed through the end of 2025, but instead be earning yield as it sits idle.
We also propose to send the ~1.5M USDC left over from the ARDC v2, which was recently denied an extension, to be sent to the ATMC to further top-up the budget allocation to onchain treasury managers. This modifies the recently passed proposal which defined the next step as the "AF returning all unused funds to the treasury", which would forfeit yield until another onchain proposal process in its entirety is carried out.
Lastly, we propose sending any remaining funds from the ADPC Security Subsidies budget to the ATMC, which will again be used to top-up the onchain treasury managers budget.
The proposal will be moved to a vote on July 24th, and if passed, funds from the ARDC V2 and 2025 Events Budget will be transferred within 7 days from their current addresses to this address where the ~4.95M USDC for the ATMC currently resides. Following the completion of the ADPC Security Subsidies, whatever USDC remains will also be sent to the same address designated for onchain stablecoin strategies managed by DAO approved treasury managers.
Motivation & Rationale
2025 Events Budget
While Entropy believes events are a vertical that should for the most part fall under the Foundation's scope and that smaller events should be funded by the D.A.O. grants program, the community has requested that this issue be taken up separately rather than being consolidated into a larger Snapshot vote. As such, we have modified this proposal to simply move the 2025 Events Budget into a yield bearing account with the ATMC to top up the stablecoin strategy allocation to treasury managers.

The Events Budget remains intact and will continue to follow the process outlined per the original proposal through 2025. Once 2025 comes to an end, the Stablecoins will remain allocated to the ATMC rather than being returned to the DAO treasury to ensure they continue to earn yield.

ARDC V2
The ARDC v2 Extension proposal recently came to a close, which resulted in the collective NOT being extended. The instructions per the proposal were defined as "(The) AF returning all unused funds to the treasury". However, now that the funds have already been converted from ARB into stablecoins, there is no sense in sending these funds back to the treasury to sit idle, and forcing another proposer to go through the entire onchain governance process to ensure they are earning yield for the DAO.

ADPC Security Subsidies
670,543.5 USDC was transferred from the MSS to an Arbitrum Foundation controlled address as a part of the MSS wind down. Entropy Advisors is engaged in ongoing discussions with the Arbitrum Foundation in regards to what portion of these funds have already been committed to service providers versus what is remaining/owed to the DAO. We propose sending any remaining ADPC Security Subsidy funds to the ATMC as well once the AF pays out any outstanding contractual obligations. We do not want this process to stall this proposal, as doing so would potentially result in the ARDC v2 funds being returned to the DAO treasury. Instead, we seek the DAO's approval to reallocate these funds to the treasury managers deploying onchain stablecoin strategies once the situation has been sorted.

Specifications
The 2025 Events Budget currently holds 1,044,095.59 USDC. If approved, the entirety of that balance will be moved to the Foundation controlled wallet that is designated for onchain stablecoin strategies managed by DAO approved treasury managers. The Events Budget process will remain unchanged for authors who wish to pull from this allocation of stablecoins to host an event.

The ARDC V2 currently holds 1,503,604.08 USDC and 112,245.95 ARB. The ARDC has finished and posted its final deliverable, the Arbitrum Ecosystem Mapping Report. Final invoices will now be obtained from the two research service providers, Castle Capital and DeFiLlama, and USDC payments initiated with the Arbitrum Foundation. Once these payments have been sent, the remaining USDC balance will be moved by the Foundation to the wallet designated for onchain stablecoin strategies. The remaining ARB will be returned to the DAO's treasury.

As mentioned above, once the Arbitrum Foundation pays out any outstanding contractual obligations related to the ADPC Security Subsidies program, the remaining USDC will be sent to the ATMC. The ATMC will update the DAO once this has occurred on its dedicated forum thread.

The 15M ARB allocated to stablecoin strategies was recently converted into ~4.95M USDC, but this proposal would increase this allocation to ~7.5-8M USDC. These funds will either be split pro-rata amongst various treasury managers already approved by the DAO, or allocated according to the newly introduced ATMC procedures i.e., allocation recommendation from Entropy followed by OAT approval. These funds have been idle for several months, which could have otherwise been earning yield. This proposal is a part of a larger effort to strengthen the Arbitrum DAO's financial position to enable long-term sustainable growth/increasing revenue.

Timeline
July 14th: Forum post
July 24th - July 31st : Snapshot vote
By August 7th: If passed, funds will be transferred to the stablecoin strategy address within 7 days"#;

// Proposal 3 - Increasing LOL Easy Track Limits
let proposal_3 = r#"Increasing LOL Easy Track Limits to align with Grant Requests
Closed

TLDR
The LOL Easy Track Motions have a limit of 100k DAI per motion. This proposal seeks to increase this limit to 250k DAI per motion to align with the grant requests that are being submitted to the LOL Committee.

Motivation
The LOL Committee has been receiving grant requests that exceed the current 100k DAI limit. This proposal seeks to increase the limit to 250k DAI per motion to align with the grant requests that are being submitted to the LOL Committee.

Specification
The LOL Easy Track Motions have a limit of 100k DAI per motion. This proposal seeks to increase this limit to 250k DAI per motion to align with the grant requests that are being submitted to the LOL Committee.

Copyright
Copyright and related rights waived via CC0."#;

// Proposal 4 - Lido Ecosystem BORG Foundation
let proposal_4 = r#"TLDR
The Lido Ecosystem BORG Foundation (the "Foundation") proposes changing the Easy Track limits for the Reimbursement and Reward Committee (RCC) to 100,000 DAI per motion (from 50,000 DAI) and 500,000 DAI per month (from 250,000 DAI).

Motivation
The Foundation has been operating for 6 months now and has been using the Easy Track system to reimburse contributors for their work. The current limits are 50,000 DAI per motion and 250,000 DAI per month. These limits are becoming restrictive as the Foundation grows and more contributors are onboarded. The Foundation proposes increasing these limits to 100,000 DAI per motion and 500,000 DAI per month.

Specification
The Foundation proposes changing the Easy Track limits for the Reimbursement and Reward Committee (RCC) to 100,000 DAI per motion (from 50,000 DAI) and 500,000 DAI per month (from 250,000 DAI).

Copyright
Copyright and related rights waived via CC0."#;

// Proposal 5 - Increase Snapshot Proposal Threshold
let proposal_5 = r#"l;dr
This proposal seeks to increase the Snapshot proposal threshold to 5,000 ~ 15,000 LDO to prevent spam and ensure that only serious proposals are submitted. The current threshold of 0.5% of the total voting power is too low and has resulted in a large number of low-quality proposals.

Motivation
The current threshold for submitting a Snapshot proposal is 0.5% of the total voting power. This is too low and has resulted in a large number of low-quality proposals. This proposal seeks to increase the threshold to 5,000 ~ 15,000 LDO to prevent spam and ensure that only serious proposals are submitted.

Specification
This proposal seeks to increase the Snapshot proposal threshold to 5,000 ~ 15,000 LDO to prevent spam and ensure that only serious proposals are submitted. The current threshold of 0.5% of the total voting power is too low and has resulted in a large number of low-quality proposals.

Copyright
Copyright and related rights waived via CC0."#;

// Proposal 6 - Orbit Program Renewal
let proposal_6 = r#"[ARFC] Orbit Program Renewal - Q2 2025
Author: ACI (Aave Chan Initiative)
Date: 2025-07-03
Summary
Proposing the renewal of the Orbit program for recognized delegates, compensating them with GHO, associated with their governance activity during Q2 2025 ( From 2025-04-01, last date, until 2025-06-30).

Motivation
Orbit recognizes the added value of the Delegates in the decentralization & diversity of the Aave DAO. This compensation allows them to focus on Aave and keep their contribution efforts to our governance. The ACI proposes the extension of Orbit for a new quarter, Q2 2025, from 2025-04-01 to 2025-06-30.

As a reminder, a new cutoff had been set on previous renewal, starting at AIP 224, to apply again previous rules of a minimum of 20k voting power and 85% vote ratio on all Snapshots and AIP to be considered elegible to Orbit.

Specification
Period Coverage: Q2 2025 from 2025-04-01 2025 to 2025-06-30
Eligible Platforms:
EzR3al: 0x8659d0bb123da6d16d9394c7838ba286c2207d0e
stablelabs: 0xecc2a9240268bc7a26386ecb49e1befca2706ac9
IgnasDefi: 0x3DDC7d25c7a1dc381443e491Bbf1Caa8928A05B0
Budget: 45,000 GHO (aEthLidoGHO)
Relevant Links:
ACI's Orbit tracker
Additional considerations:

As a reminder, Service Providers will not be considered elegible to Orbit Program.

Funds are distributed based on 90 days, as seen on budget.

Next Steps
Gather community feedback on this ARFC.
If consensus is achieved, escalate this proposal to the ARFC snapshot stage.
If the ARFC snapshot outcome is YAE, proceed to the AIP stage for implementation and funding allocation in cooperation with Aave Finance service providers via an ad-hoc AIP vote or bundled in one of their treasury management AIPs.
Disclosure
The ACI is independent and has not received any form of compensation from related parties for the drafting of this proposal.

Copyright
Copyright and related rights waived under Creative Commons Zero (CC0)"#;

let proposal_8 = r#"GIP-128 Should GnosisDAO fund Gnosis Ltd with $30m/ year?
Passed

0xbE96...795B
In GnosisDAO · 1mo ago · #cd71a




This proposal requests a grant with an annual budget of $30 million in stablecoins, disbursed quarterly, to fund the operations of Gnosis Ltd — now formally a quasi-foundation — as the primary builder of Gnosis infrastructure and ecosystem products.

Gnosis Ltd played a foundational role in the Gnosis ecosystem: it conducted the original GNO token sale in 2017, and in 2021, divested 150k ETH, 8 million GNO, and several third-party token positions into the newly formed GnosisDAO. Since then, it has operated without requesting funding, relying on its retained assets.

As of early 2025, Gnosis Ltd has successfully completed its legal transformation into a quasi foundation (a Company Ltd by guarantee without share capital), eliminating the dual equity-token structure and converting the entity into a purely purpose driven organization, with the objective to further the Gnosis ecosystem and decentralised technologies more generally. With the transition complete and reserves running low, this proposal marks its first funding request to the DAO.

While many entities contribute, Gnosis Ltd is still the primary development and operations entity in the Gnosis ecosystem. It builds and maintains the core infrastructure that powers Gnosis Chain, and develops and supports major products, onboarding, BD, and governance tooling for the community.

This proposal ensures continuity and momentum for critical initiatives, while maintaining full alignment with the DAO's long-term interests.

Scope of Work & Budget Breakdown
The requested grant will cover Gnosis Ltd's forecasted expenditure for a 12-month period, starting July 1, 2025. Disbursements will occur quarterly, with each installment totaling $7.5M in stablecoins. Funds will be sent to Gnosis Ltd's Gnosis Safe.

Below is a high-level breakdown of Gnosis Ltd's budget for the next 12 months. There are currently 127 team members and we're expecting to onboard 25 more in the coming year.

Product Development $15.5m
Gnosis Pay $8.0m
Circles $1.5m
Gnosis (fka metri) $3.1m
Gnosis Business (fka HQ) $2.9m

Gnosis Chain and Core Infrastructure $3.6m
Personnel (chain, bridges, devops, audits, analytics) $1.95m
Hosting and cloud providers $0.65m
Security audits and bug bounties $0.3m
Gnosisscan $0.4m
Safe network support $0.18m
tenderly network support $0.1m
dune network support $0.02m

BD and DevRel $3.85m
Personnel $0.85m
Integrations (CEX, stablecoins, onramps) $2.5m
Event sponsorships $0.4m
Open internet clubs $0.1m

Marketing and design $2.035m
Personnel $1.05m
Marketing spent $0.835m
PR agency $0.15m

Gnosis Labs $0.4m
Personnel $0.4m

HR & ops $0.45m
Personnel $0.45m

Legal $1.625m
Personnel $1.025m
External advisory $0.6m

Finance $0.59m
Personnel $0.41m
External advisory $0.11m
Software $0.07m

Personnel overhead $1.5m
Travel, equipment, software, offices

Management $0.45m
M/S/F $0.15m each

Reporting and Accountability
Gnosis Ltd will publish quarterly reports detailing spend and progress across all budget categories.

No additional oversight structures are proposed; DAO token holders retain ultimate accountability through governance.

Future funding will depend on DAO review of outcomes and updated proposals.

Gnosis Ltd seeded the DAO. This proposal ensures the DAO can continue to rely on it. Onwards and upwards! :rocket:"#;

let proposal_9 = r#"Ecosystem Proposal - Zen Card
Closed

0xb6Ba...6903
In Metis · 1y ago · #2d694




Zen Card is an NFC hardware wallet developed by Ninety Eight with the mission of redefining the needs for security and management of everyone's cryptocurrency assets. Zen Card now supports 100+ networks, including EVMs and non-EVM chains.

Zen Card Docs

Our Specialties

Zen Card allows quick connections with Coin98 Super Wallet to sign transactions by simply tapping the card on a smartphone. Its split-key technology ensures the highest level of crypto asset security within the Web3 landscapes.

Here are some key features that make Zen Card the must-have NFC hardware wallet:

Supporting over 100 blockchains and continuously expanding to future chains
Innovative key storage mechanism which minimizes hacking risks and maximizes security
Ultra-portable design as a bank card that allows you to carry your digital wealth securely wherever you go
Empowering users with complete control over their keys and assets, unlocking the full potential of decentralized finance (DeFi)
Securing your coins and tokens from third-party meddling.
Plus, Zen Card can double up as a smart electronic business card for seamless networking in the Web3 realm
Benefits for Users
Zen Card allows quick connections with Coin98 Super Wallet to sign transactions by simply tapping the card on any NFC-supported devices. Users can securely transfer and receive their METIS tokens and other tokens on the Metis network using our Zen Card. Furthermore, users can access and interact with their preferred dApps on Metis with more security than ever. Stay tuned for more surprises that await you once the proposal is approved.

Benefits for Metis Ecosystem
We've already integrated the Metis chain into Zen Card, this will allow our Zen Card users to explore and interact with Metis seamlessly. Additionally, we can help Metis establish a stronger presence in Asia, particularly in Southeast Asia. Once the proposal is approved, we can work together on exclusive marketing campaigns specifically designed for Metis users and its ecosystem, which could potentially attract thousands of new users.

Roadmap
Now that we've completed the integration and announcement on our end, we're eager to be featured on the Metis Ecosystem page. Once approved by the Governance, we can potentially launch an exclusive social giveaway called 'Web3 For Everyone' for Metis users.
At Zen Card, we strongly believe that Web3 fosters a new era where everyone, regardless of background or identity, enjoys equitable access and opportunities. This mission matches with the idea that anyone, anywhere, can thrive in a decentralized economy from Metis. From this giveaway, Metis users will be rewarded with Zen Card GMVN Limited Edition.

Summary
Zen Card has integrated with Metis and various dApps of the blockchain. By now, Metis users can securely store and manage crypto assets as well as seamless connection with these dApps on Metis. We're submitting this proposal in the hopes of gaining approval from Metis governance. After receiving approval, we intend to launch a campaign with Metis called 'Web3 For Everyone' to engage with community, expand Metis ecosystem, and bring in thousands of new users to DeFi.

Official Links
Website: zencard.io
Twitter: x.com/ZenCardio"#;

let proposal_10 = r#"AIP-555: Rebranding ApeCoin: Transition from Ape Skull to New Gorilla Logo
 Passed

0xFA98...bC28 admin
In ApeCoin DAO · 9mo ago · #17e3f




PROPOSAL DESCRIPTION
This AIP proposes to change the current ApeCoin logo from the ape skull to the new gorilla logo. This rebranding initiative aims to refresh the ApeCoin identity, aligning it with the evolving vision and values of the ApeCoin ecosystem while also enhancing its visual appeal and recognition within the broader crypto community. This AIP also aims to make a more clear distinction between the BAYC community and the DAO community. With the launch of ApeChain, the DAO now has its north star and I believe it is important for it to have its own unique brand/ identity. Updating the logo achieves that objective while also signaling that both the DAO and ApeChain is the place to ape for all, and not just BAYC.

image

image

image

BENEFIT TO APECOIN ECOSYSTEM
Unique Branding that fits the culture of the DAO and ApeChain and is more clearly differentiated from BAYC.

Enhanced Recognition comes from the unique branding across the wider crypto ecosystem and world.

OVERALL COST
Total amount requested from the ApeCoin Ecosystem Fund = $0.

Upon approval, The Foundation would be expected to update the logo across all ApeCoin platforms, including the website, social media, marketing materials and any third parties showcasing the token, and make an official announcement regarding the logo change to the community and stakeholders.

PROPOSAL
Link to the full proposal: (https://forum.apecoin.com/t/aip-555-rebranding-apecoin-transition-from-ape-skull-to-new-gorilla-logo/26726/1)

The AIP implementation is administered by the Ape Foundation. Implementation may be immaterially or materially altered to optimise for security, usability, to protect APE holders, and otherwise to effect the intent of the AIP. Any material deviations from an AIP, as initially approved, will be disclosed to the APE holder community."#;

let proposal_11 = r#"Add USDe to Moonwell Core Market on Base and Optimism
 Passed

azgardadmin.eth
In Moonwell Governance · 7mo ago · #7790b



I'm excited to propose adding USDe (Ethena USD), the stablecoin from Ethena Protocol, to Moonwell's core lending markets on Base and Optimism. This move will enhance market utility, encourage ecosystem growth, and provide users with a decentralized, stable asset that aligns with our protocol's mission.

General Information
Token: USDe (Ethena USD)

Description: USDe is the stablecoin of the Ethena Protocol, designed to maintain a soft peg to the U.S. dollar. It integrates seamlessly within the DeFi ecosystem, combining stability, flexibility, and decentralization. Key features include:

Simple USDe Conversions: The USDe/USD converter allows easy and unrestricted 1:1 conversions between USD and USDe, ensuring fluid liquidity movement.
Participation in Ethena Savings Rate: USDe holders can earn rewards through the Ethena Savings Rate, offering a decentralized, non-custodial savings option without losing control of their funds.
Benefits to the Moonwell Community
Enhanced Stablecoin Liquidity: Adding USDe will expand our stablecoin offerings, creating more lending and borrowing opportunities. This addition will make Moonwell the largest source of multiple stablecoins in the market.
Increased Protocol Engagement: By integrating USDe, we can attract users from the Ethena Protocol ecosystem, including those looking to leverage the Ethena Savings Rate for stable returns.
Decentralization Alignment: As a new version of traditional stablecoins, USDe represents a permissionless, non-custodial alternative that aligns with decentralized finance principles.
Reduced Systemic Risk: Backed by surplus collateral and supporting secure 1:1 conversions, USDe offers a stable, reliable asset that reduces risks associated with over-leveraged or under-collateralized stablecoins.
Effortless Integration: Adding USDe to Moonwell doesn't require new code development. All necessary functionalities and mechanisms are already in place within our current infrastructure, making the addition of USDe smooth and efficient.
Resources and Socials
Ethena Website: Ethena Website
Ethena Social Channels:
Twitter: @ethena_labs 210k followers
Market Risk Assessment
Market Metrics:

Market Cap: $5.8B (across all networks)
Vol/Mkt Cap (24h): 1.1%
Maximum Supply: Unlimited USDe
24 Hour Trading Volume: $64M
Liquidity on Decentralized Exchanges:

Curve (Ethereum): $20,000,000
Decentralization
Token Contract:
Base: 0x5d3a1Ff2b6BAb83b63cd9AD0787074081a52ef34
Optimism: 0x5d3a1Ff2b6BAb83b63cd9AD0787074081a52ef34
Blacklist Functionality: No.
Token Standard: ERC-20 USDe Stablecoin
Smart Contract Risks
Codebase and Onchain Activity:

Total Transactions: 36K on Base , 58K on Optimism
Age of Token in Days: 229 days on Base and 323 days on Optimism
Security Posture: https://docs.ethena.fi/resources/audits
Upgradability:
Is it Upgradeable: No.
summary of the Ethena Protocol documentation:
Key Features
USDe (Synthetic Dollar): USDe maintains a soft peg to the U.S. dollar through delta-hedging mechanisms. It's designed to be censorship-resistant and fully-backed by crypto assets.
sUSDe (Internet Bond): sUSDe is a reward-accruing asset derived from staked asset returns and the funding/basis spread available in perpetual and futures markets.
Delta Hedging: USDe's peg stability is achieved by executing automated delta-neutral hedges with respect to the underlying backing assets.
Permissionless Minting: Users can acquire USDe in external liquidity pools, and approved parties can mint and redeem USDe on-demand.
Benefits
Decentralization: USDe is non-custodial and permissionless, aligning with decentralized finance principles.
Stability: The delta-hedging mechanism helps maintain a relatively stable value.
Revenue Generation: Ethena Protocol generates revenue from staked ETH assets and the funding/basis spread from delta-hedging derivatives positions.
Risks
Market Conditions: The stability of USDe can be affected by market conditions and the performance of the backing assets.
Counterparty Risk: While minimized, there is still some counterparty risk associated with derivatives exchanges.
Oracle Assessment
Oracle Price Feed Addresses:

USDe-USD, Base Feed Address: 0x790181e93e9F4Eedb5b864860C12e4d2CffFe73B
USDe-USD, Optimism Feed Address: 0xEEDF0B095B5dfe75F3881Cb26c19DA209A27463a
Relevant Documentation: Base Optimism
Tier: Low Market Risk
Proposal Author Information
Name: AsgardAdmin
Github: https://github.com/AzgardMultiSig
Delegate Address: 0xC4c1e942c6B97EE736d15E6edE71dBc323200c3d
Relationship with Token: I have no personal or professional relationship with the USDe token.

Conclusion
Adding USDe as a core lending market will boost stablecoin utility and drive liquidity growth on Moonwell. By supporting USDe, we can offer users new financial opportunities while promoting stability and innovation within our protocol.

I'm opening this proposal to the community for review, discussion, and feedback to ensure its success and alignment with our vision for a secure and decentralized onchain financial future."#;

let proposal_12 = r#"[RCC-3] October 1, 2022 - October 31, 2022 Budget Request
 Passed

zuzu_eeka
In Lido · 3y ago · #57c8e





The final standalone period for RCC funding, following on from Q2 2022, has begun on October 1, 2022 and will end on October 31, 2022. We are preparing the grounds for a final funding proposal as a followup to this post that will run the DAO as a whole starting on November 1, 2022. We will publish more details over the coming days.

Lido will be moving to a continuous funding model starting on November 1, 2022, which has created a 1 month gap for operations financed out of RCC. The following request will bridge the gap for operating expenses for the month of October (many expenses are due at the end of the month). A total of 50k LDO will be requested to cover September overdue LDO compensation and October LDO compensation.

This budget, on a monthly basis, is substantially larger than previous RCC asks for a few key reasons:

Deployment of marketing expenses in a busy month
Transfer of Audits and Bug Bounties from LEGO to RCC
Deployment of GCP and Github Funding
Contingency funding for operating expenses (not immediately drawn)
Details on the following link: https://research.lido.fi/t/rcc-3-october-1-2022-october-31-2022-budget-request/3055

Proposal Actions
DAI 732,710 will be supplied to the RCC multisig wallet 0xDE06d17Db9295Fa8c4082D4f73Ff81592A3aC437 from the DAI treasury to allow the RCC to fulfill its operational needs
235,543 DAI for headcount related expenses including base compensation and travel for 20 contributors
497,167 DAI for operating expenses, of which
267,833 DAI related to marketing expenditures
165,000 DAI related to audits and bug bounties
50,000 DAI related to software subscriptions
Remainder in other operating expenses
LDO 50,311 will be supplied to the RCC multisig wallet 0xDE06d17Db9295Fa8c4082D4f73Ff81592A3aC437 from the LDO treasury for October and backdated LTI compensation
10,310.34 LDO two months of vesting for one contributor (one month is overdue)
40,000 LDO for a one-year vesting cliff for one contributor
If requested, DAI 400k will be made available to the RCC multisig 0xDE06d17Db9295Fa8c4082D4f73Ff81592A3aC437from the DAI treasury in the event of threats to business continuity during the upcoming funding rounds
If not necessary, the DAI 400k will not be drawn at all
If drawn, unused funds will be returned before 31-Dec-2022"#;

// Create an array with all proposal variables
let proposals = vec![
    proposal_1,
    proposal_2,
    proposal_3,
    proposal_4,
    proposal_5,
    proposal_6,
    proposal_8,
    proposal_9,
    proposal_10,
    proposal_11,
    proposal_12,
];

proposals
}
