import { Eip } from '../types/eip';
import { Proposal } from '../hooks/useProposals';

// Extended Proposal type that includes EIP metadata
export interface EipProposal extends Proposal {
  eip?: {
    eip_number: number;
    status: string;
    eip_type: string;
    category?: string;
    created: string;
  };
}

/**
 * Ethereum space ID constant
 */
export const ETHEREUM_SPACE_ID = 'ethereum';

/**
 * Ethereum space object
 */
export const ETHEREUM_SPACE = {
  id: ETHEREUM_SPACE_ID,
  name: 'Ethereum',
  avatar: 'https://ethereum.org/static/a110735dade3f354a46fc2446cd52476/f3a29/eth-home-icon.webp',
  verified: true
};

/**
 * Convert an EIP to a Proposal format
 */
export function eipToProposal(eip: Eip): EipProposal {
  return {
    id: `eip-${eip.eip_number}`,
    title: `EIP-${eip.eip_number}: ${eip.title}`,
    body: eip.content || eip.description,
    author: Array.isArray(eip.author) ? eip.author.join(', ') : eip.author,
    space: ETHEREUM_SPACE,
    // Add additional metadata to identify as EIP
    eip: {
      eip_number: eip.eip_number,
      status: eip.status,
      eip_type: eip.eip_type,
      category: eip.category,
      created: eip.created
    }
  };
}

/**
 * Convert multiple EIPs to Proposal format
 */
export function eipsToProposals(eips: Eip[]): Proposal[] {
  return eips.map(eipToProposal);
}

/**
 * Check if a proposal ID is an EIP
 */
export function isEipProposal(proposalId: string): boolean {
  return proposalId.startsWith('eip-');
}

/**
 * Extract EIP number from proposal ID
 */
export function getEipNumberFromProposalId(proposalId: string): number | null {
  if (!isEipProposal(proposalId)) {
    return null;
  }
  
  const eipNumber = parseInt(proposalId.replace('eip-', ''), 10);
  return isNaN(eipNumber) ? null : eipNumber;
}
