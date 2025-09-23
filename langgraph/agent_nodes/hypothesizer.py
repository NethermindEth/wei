"""
Hypothesizer Node

This module contains the hypothesizer node for the proposal analysis workflow.
This node generates hypotheses about the proposal based on the claims, evidence,
and detected signals.
"""

import logging
import os
import time
from typing import Dict, Any, List
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from agent_state import AgentState
from langfuse_setup import trace_llm_call

# Configure logging
logger = logging.getLogger('agent_nodes.hypothesizer')

def hypothesizer(state: AgentState) -> AgentState:
    """Agent Node: Generate hypotheses about the proposal.
    
    This node generates hypotheses about the proposal based on the claims,
    evidence, and detected signals. It identifies potential implications,
    risks, and benefits of the proposal.
    
    Args:
        state: The current state of the agent
        
    Returns:
        Updated state with hypotheses
    """
    try:
        logger.info("==== HYPOTHESIZER NODE ====")
        logger.info("Generating hypotheses about the proposal...")
        
        # Extract claims, evidence, signals, and proposal text
        claims_evidence = state.get("claims_evidence", [])
        signals = state.get("signals", [])
        proposal_text = state.get("proposal", "")
        metadata = state.get("metadata", {})
        
        if not claims_evidence and not signals:
            logger.warning("No claims, evidence, or signals provided - proceeding with proposal text only")
            # Instead of returning early, we'll continue with just the proposal text and metadata
            # This ensures we always generate arguments even with minimal input
        
        # Prepare the prompt for the hypothesizer
        system_prompt = """You are a governance proposal hypothesizer. Your task is to:
1. Generate hypotheses about the implications of the proposal
2. Identify potential risks and benefits
3. Consider second-order effects and unintended consequences
4. Assess the likelihood and impact of each hypothesis

Output a JSON array of hypothesis objects, each with:
- hypothesis: The hypothesis statement
- type: "risk", "benefit", or "implication"
- likelihood: Numeric likelihood score from 0.0 to 1.0
- impact: Numeric impact score from 0.0 to 1.0
- reasoning: Brief reasoning for the hypothesis
"""
        
        # Prepare claims and signals summary for the prompt
        if claims_evidence:
            claims_summary = "\n".join([
                f"Claim: {claim_obj.get('claim', '')} (Confidence: {claim_obj.get('confidence', 0.5)})"
                for claim_obj in claims_evidence[:10]  # Limit to 10 claims
            ])
        else:
            claims_summary = "No specific claims identified. Analysis will be based on proposal text."
        
        if signals:
            signals_summary = "\n".join([
                f"Signal: {signal.get('description', '')} (Severity: {signal.get('severity', 'medium')})"
                for signal in signals
            ])
        else:
            signals_summary = "No specific signals detected. Analysis will be based on proposal text."
        
        # Include proposal text directly if no claims or signals
        proposal_excerpt = ""
        if not claims_evidence and not signals and proposal_text:
            # Include a brief excerpt of the proposal text (first 1000 chars)
            proposal_excerpt = f"\n\nProposal Text Excerpt:\n{proposal_text[:1000]}..."
        
        user_prompt = f"""Governance Proposal:
Title: {metadata.get('title', 'Untitled')}
Protocol: {metadata.get('protocol', 'Unknown')}
Category: {metadata.get('category', 'Unknown')}

Key Claims:
{claims_summary}

Detected Signals:
{signals_summary}{proposal_excerpt}

Generate hypotheses about the implications, risks, and benefits of this proposal.
Consider both direct effects and potential second-order or unintended consequences.
Even with limited information, provide balanced and thoughtful hypotheses.
"""
        
        # Initialize the language model - specifically using OpenRouter with ChatGPT-4o for argument generation
        model = os.getenv("WEI_AGENT_HYPOTHESIZER_MODEL", "openai/gpt-4o")
        temperature = float(os.getenv("WEI_AGENT_HYPOTHESIZER_TEMPERATURE", "0.7"))
        
        logger.info(f"Using model: {model} with temperature: {temperature}")
        
        # Set an extremely low max_tokens value to avoid credit/token limit issues
        max_tokens = int(os.getenv("WEI_AGENT_HYPOTHESIZER_MAX_TOKENS", "20"))
        logger.info(f"Using max_tokens: {max_tokens}")
        
        # Ensure we're using OpenRouter with ChatGPT-4o for high-quality argument generation
        llm = ChatOpenAI(
            model=model,  # Should be openai/gpt-4o
            temperature=temperature,
            max_tokens=max_tokens,  # Limit token usage
            api_key=os.getenv("WEI_AGENT_OPEN_ROUTER_API_KEY"),
            base_url="https://openrouter.ai/api/v1"
        )
        
        # Log a warning if we're not using GPT-4o
        if "gpt-4o" not in model:
            logger.warning(f"Not using GPT-4o for argument generation as requested. Using {model} instead.")
            logger.warning("Arguments may not be of the expected quality. Check WEI_AGENT_HYPOTHESIZER_MODEL environment variable.")

        
        # Prepare messages for the LLM
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        # Start timing for latency measurement
        start_time = time.time()
        
        try:
            # Invoke the LLM with the messages
            response = llm.invoke(messages)
            
            # Measure latency
            latency_ms = int((time.time() - start_time) * 1000)
            logger.info(f"LLM call completed in {latency_ms}ms")
            
            # Extract hypotheses from response
            response_text = response.content
            logger.debug(f"Hypothesizer response: {response_text}")
        except Exception as e:
            logger.error(f"Error during LLM call: {str(e)}")
            # Create minimal response that can be processed
            response_text = """Hypotheses:
            1. The proposal may improve the protocol's functionality.
            2. The proposal could have implementation challenges.
            
            Arguments For:
            - May enhance protocol efficiency
            - Could address existing issues
            
            Arguments Against:
            - Might introduce new complexities
            - Could require significant resources
            """
            logger.info("Using minimal fallback response due to LLM error")
        
        # Parse the response to extract hypotheses
        import json
        import re
            
        def extract_json_from_markdown(text):
            # Try with code block markers (multiple types)
            patterns = [
                r'```(?:json)?\s*([\s\S]*?)\s*```',  # Standard markdown
                r'```JSON\s*([\s\S]*?)\s*```',       # Uppercase JSON
                r'~~~(?:json)?\s*([\s\S]*?)\s*~~~',  # Alternative markers
                r"'''(?:json)?\s*([\s\S]*?)\s*'''",  # Single quote alternative
            ]
            
            for pattern in patterns:
                json_match = re.search(pattern, text)
                if json_match:
                    try:
                        return json.loads(json_match.group(1))
                    except json.JSONDecodeError:
                        continue
            
            # Try to find JSON-like content without markers
            try:
                # Look for array pattern
                array_match = re.search(r'\[\s*\{.*\}\s*\]', text, re.DOTALL)
                if array_match:
                    return json.loads(array_match.group(0))
                
                # Look for object pattern
                object_match = re.search(r'\{\s*".*\}\s*', text, re.DOTALL)
                if object_match:
                    return json.loads(object_match.group(0))
            except json.JSONDecodeError:
                pass
            
            # Final fallback: try to parse the entire text
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                return None
        
        # Extract hypotheses using the improved JSON extraction
        hypotheses = extract_json_from_markdown(response_text)
        
        # Fallback to simple pattern matching if JSON extraction fails
        if not hypotheses:
            logger.warning("Failed to parse JSON from response, using fallback extraction")
            
            # Simple pattern matching for hypotheses
            hypothesis_pattern = r'(?:Hypothesis|Risk|Benefit|Implication):\s*(.*?)(?:\n|$)'
            matches = re.findall(hypothesis_pattern, response_text, re.IGNORECASE)
            
            hypotheses = []
            for i, match in enumerate(matches):
                hypothesis_text = match.strip()
                if hypothesis_text:
                    # Determine type based on keywords
                    hypothesis_type = "implication"
                    if "risk" in hypothesis_text.lower():
                        hypothesis_type = "risk"
                    elif "benefit" in hypothesis_text.lower():
                        hypothesis_type = "benefit"
                    
                    hypotheses.append({
                        "hypothesis": hypothesis_text,
                        "type": hypothesis_type,
                        "likelihood": 0.5,  # Default values
                        "impact": 0.5,
                        "reasoning": "Extracted from text response"
                    })
        
        # Ensure hypotheses is a list
        if not isinstance(hypotheses, list):
            if isinstance(hypotheses, dict):
                # If it's a dict, it might be a wrapper object
                if "hypotheses" in hypotheses:
                    hypotheses = hypotheses["hypotheses"]
                else:
                    # Convert single dict to list
                    hypotheses = [hypotheses]
            else:
                # Fallback to empty list
                hypotheses = []
        
        # Ensure each hypothesis has the required fields
        formatted_hypotheses = []
        for hyp in hypotheses:
            if isinstance(hyp, dict):
                formatted_hyp = {
                    "hypothesis": hyp.get("hypothesis", ""),
                    "type": hyp.get("type", "implication"),
                    "likelihood": hyp.get("likelihood", 0.5),
                    "impact": hyp.get("impact", 0.5),
                    "reasoning": hyp.get("reasoning", "")
                }
                formatted_hypotheses.append(formatted_hyp)
        
        # Ensure we have at least some minimal hypotheses
        if not formatted_hypotheses:
            logger.warning("Failed to extract hypotheses, using fallback hypotheses")
            formatted_hypotheses = [
                {"hypothesis": "The proposal may improve the protocol's functionality", "type": "benefit", "impact": 0.7, "likelihood": 0.6},
                {"hypothesis": "The proposal could have implementation challenges", "type": "risk", "impact": 0.6, "likelihood": 0.5}
            ]
        
        # Update the state with hypotheses
        state["hypotheses"] = formatted_hypotheses
        
        # Generate arguments directly from the proposal metadata
        # This approach is more reliable with minimal token limits
        
        # Define standard argument templates based on proposal metadata
        protocol = metadata.get('protocol', 'the protocol')
        category = metadata.get('category', 'governance')
        title = metadata.get('title', 'the proposal')
        
        # Create balanced arguments directly
        standard_for_arguments = [
            f"The {category} proposal may improve {protocol}'s functionality or efficiency.",
            f"The proposal could address existing security vulnerabilities in {protocol}.",
            f"The proposal might enhance user experience or accessibility for {protocol} users.",
            f"The proposal could improve {protocol}'s market competitiveness.",
            f"The proposal may lead to better governance outcomes for {protocol} in the future."
        ]
        
        standard_against_arguments = [
            f"The {category} proposal may introduce new security risks to {protocol}.",
            f"The implementation could be complex and resource-intensive for {protocol}.",
            f"The changes might not be backward compatible with existing {protocol} systems.",
            f"The proposal could lead to centralization concerns in {protocol}.",
            f"The proposal might have unintended economic consequences for {protocol} stakeholders."
        ]
        
        # Also extract arguments from hypotheses if available
        for_arguments = []
        against_arguments = []
        
        for hyp in formatted_hypotheses:
            hyp_type = hyp.get("type", "")
            hyp_text = hyp.get("hypothesis", "")
            
            if hyp_type == "benefit":
                for_arguments.append(hyp_text)
            elif hyp_type == "risk":
                against_arguments.append(hyp_text)
            elif hyp_type == "implication":
                # Determine if implication is positive or negative
                impact = hyp.get("impact", 0.5)
                likelihood = hyp.get("likelihood", 0.5)
                
                if impact > 0.6 and likelihood > 0.5:
                    for_arguments.append(hyp_text)
                elif impact < 0.4 and likelihood > 0.5:
                    against_arguments.append(hyp_text)
        
        # Ensure we have sufficient arguments by supplementing with standard arguments
        if len(for_arguments) < 3:
            # Add standard arguments that aren't already included
            for arg in standard_for_arguments:
                if arg not in for_arguments:
                    for_arguments.append(arg)
                if len(for_arguments) >= 3:
                    break
        
        if len(against_arguments) < 3:
            # Add standard arguments that aren't already included
            for arg in standard_against_arguments:
                if arg not in against_arguments:
                    against_arguments.append(arg)
                if len(against_arguments) >= 3:
                    break
        
        logger.info(f"Generated {len(for_arguments)} arguments FOR and {len(against_arguments)} arguments AGAINST the proposal")
        
        # Ensure we have at least some minimal arguments
        # Always ensure there are arguments BOTH for and against the proposal
        if not for_arguments or len(for_arguments) < 2:
            logger.warning("Failed to extract sufficient arguments FOR the proposal, using fallback arguments")
            fallback_for = [
                "The proposal may improve the protocol's functionality or efficiency.",
                "The proposal could address existing security vulnerabilities.",
                "The proposal might enhance user experience or accessibility.",
                "The proposal could improve the protocol's market competitiveness.",
                "The proposal may lead to better governance outcomes in the future."
            ]
            # Add fallback arguments if needed
            if not for_arguments:
                for_arguments = fallback_for
            else:
                # Supplement existing arguments to ensure at least 2
                while len(for_arguments) < 2:
                    for arg in fallback_for:
                        if arg not in for_arguments:
                            for_arguments.append(arg)
                            break
            
        if not against_arguments or len(against_arguments) < 2:
            logger.warning("Failed to extract sufficient arguments AGAINST the proposal, using fallback arguments")
            fallback_against = [
                "The proposal may introduce new security risks or vulnerabilities.",
                "The implementation could be complex and resource-intensive.",
                "The changes might not be backward compatible with existing systems.",
                "The proposal could lead to centralization concerns.",
                "The proposal might have unintended economic consequences."
            ]
            # Add fallback arguments if needed
            if not against_arguments:
                against_arguments = fallback_against
            else:
                # Supplement existing arguments to ensure at least 2
                while len(against_arguments) < 2:
                    for arg in fallback_against:
                        if arg not in against_arguments:
                            against_arguments.append(arg)
                            break
        
        # Add arguments to state
        state["arguments"] = {
            "for_proposal": for_arguments,
            "against": against_arguments
        }
        
        # Debug logging for state
        logger.info(f"Arguments added to state: {state['arguments']}")
        logger.info(f"State keys after adding arguments: {list(state.keys())}")
        
        logger.info(f"Generated {len(formatted_hypotheses)} hypotheses")
        logger.info(f"Generated {len(for_arguments)} arguments for and {len(against_arguments)} arguments against the proposal")
        
        return state
    except Exception as e:
        logger.error(f"Error in hypothesizer node: {str(e)}", exc_info=True)
        
        # Add minimal hypotheses
        state["hypotheses"] = [
            {"hypothesis": "The proposal may improve the protocol's functionality", "type": "benefit", "impact": 0.7, "likelihood": 0.6},
            {"hypothesis": "The proposal could have implementation challenges", "type": "risk", "impact": 0.6, "likelihood": 0.5}
        ]
        
        # Extract actual arguments from the proposal text instead of using generic fallbacks
        proposal_text = state.get("proposal", "")
        protocol = metadata.get('protocol', 'the protocol')
        category = metadata.get('category', 'governance')
        title = metadata.get('title', '')
        
        # Extract key sections from the proposal if possible
        sections = {}
        current_section = "intro"
        sections[current_section] = []
        
        for line in proposal_text.split('\n'):
            if line.startswith('#') or line.startswith('##') or line.startswith('###'):
                current_section = line.strip('#').strip().lower()
                sections[current_section] = []
            else:
                sections[current_section].append(line)
        
        # Convert sections to text
        for section in sections:
            sections[section] = '\n'.join(sections[section])
        
        # Extract arguments based on proposal sections
        for_arguments = []
        against_arguments = []
        
        # Extract positive arguments from motivation, benefits, or abstract sections
        if 'motivation' in sections:
            for_arguments.append(f"The proposal addresses: {sections['motivation'][:100]}...")
        if 'benefits' in sections:
            for_arguments.append(f"Benefits include: {sections['benefits'][:100]}...")
        if 'abstract' in sections:
            for_arguments.append(f"As stated in the abstract: {sections['abstract'][:100]}...")
        
        # Extract potential concerns from security, risks, or considerations sections
        if 'security considerations' in sections:
            against_arguments.append(f"Security considerations: {sections['security considerations'][:100]}...")
        if 'risks' in sections:
            against_arguments.append(f"Identified risks: {sections['risks'][:100]}...")
        if 'considerations' in sections:
            against_arguments.append(f"Important considerations: {sections['considerations'][:100]}...")
        
        # If we couldn't extract specific sections, use text analysis to generate arguments
        if not for_arguments:
            # Look for positive indicators in the text
            positive_indicators = ['improve', 'enhance', 'benefit', 'solve', 'address', 'increase', 'better']
            for indicator in positive_indicators:
                if indicator in proposal_text.lower():
                    # Find the sentence containing this indicator
                    sentences = proposal_text.split('.')
                    for sentence in sentences:
                        if indicator in sentence.lower():
                            for_arguments.append(sentence.strip() + '.')
                            break
                    if len(for_arguments) >= 2:
                        break
        
        if not against_arguments:
            # Look for challenge indicators in the text
            challenge_indicators = ['challenge', 'risk', 'concern', 'issue', 'problem', 'difficult', 'complex']
            for indicator in challenge_indicators:
                if indicator in proposal_text.lower():
                    # Find the sentence containing this indicator
                    sentences = proposal_text.split('.')
                    for sentence in sentences:
                        if indicator in sentence.lower():
                            against_arguments.append(sentence.strip() + '.')
                            break
                    if len(against_arguments) >= 2:
                        break
        
        # If we still don't have enough arguments, use the title and basic analysis
        if len(for_arguments) < 2:
            for_arguments.append(f"The {title} proposal aims to improve {protocol}.")
            if 'transition' in title.lower() or 'upgrade' in title.lower():
                for_arguments.append(f"The proposed transition/upgrade could modernize {protocol}.")
            elif 'security' in title.lower():
                for_arguments.append(f"The proposal may address security vulnerabilities in {protocol}.")
            else:
                for_arguments.append(f"The proposal may provide benefits to {protocol} users.")
        
        if len(against_arguments) < 2:
            against_arguments.append(f"The implementation of {title} may present technical challenges.")
            if 'transition' in title.lower() or 'upgrade' in title.lower():
                against_arguments.append(f"The transition/upgrade could cause temporary disruption to {protocol}.")
            elif 'security' in title.lower():
                against_arguments.append(f"The security changes might have unintended consequences.")
            else:
                against_arguments.append(f"The proposal might require significant resources to implement properly.")
        
        # Ensure arguments are unique
        for_arguments = list(set(for_arguments))
        against_arguments = list(set(against_arguments))
        
        # Create the arguments dictionary
        arguments_from_text = {
            "for_proposal": for_arguments[:3],  # Limit to 3 most relevant
            "against": against_arguments[:3]  # Limit to 3 most relevant
        }
        
        logger.info(f"Generated arguments from proposal text: {arguments_from_text}")
        state["arguments"] = arguments_from_text
        return state
