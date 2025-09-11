import { Eip } from './eip';
import { Proposal } from '../hooks/useProposals';

/**
 * Discriminated union type for proposal sources
 * This allows for type-safe handling of different proposal sources
 */
export type ProposalSource = 
  | { type: 'snapshot'; proposal: Proposal }
  | { type: 'eip'; eip: Eip };

/**
 * Type guard to check if a proposal source is a Snapshot proposal
 */
export function isSnapshotProposal(source: ProposalSource): source is { type: 'snapshot'; proposal: Proposal } {
  return source.type === 'snapshot';
}

/**
 * Type guard to check if a proposal source is an EIP
 */
export function isEipProposal(source: ProposalSource): source is { type: 'eip'; eip: Eip } {
  return source.type === 'eip';
}

/**
 * Convert a proposal source to a unified Proposal format
 */
export function toUnifiedProposal(source: ProposalSource): Proposal {
  if (isSnapshotProposal(source)) {
    return source.proposal;
  } else {
    const eip = source.eip;
    return {
      id: `eip-${eip.eip_number}`,
      title: `EIP-${eip.eip_number}: ${eip.title}`,
      body: eip.content || eip.description,
      author: Array.isArray(eip.author) ? eip.author.join(', ') : eip.author,
      space: {
        id: 'ethereum',
        name: 'Ethereum',
        avatar: 'https://ethereum.org/static/a110735dade3f354a46fc2446cd52476/f3a29/eth-home-icon.webp',
        verified: true
      },
      // Add metadata to identify as EIP
      eipData: {
        eip_number: eip.eip_number,
        status: eip.status,
        eip_type: eip.eip_type,
        category: eip.category,
        created: eip.created,
        content: eip.content,
        description: eip.description
      }
    };
  }
}
