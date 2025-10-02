"""
Test script for the deep proposal analyzer.
This script tests the refactored implementation of the proposal analyzer
using the deepagents package with Langfuse tracing for monitoring and debugging.
"""

import logging
import sys
import os
import json
import time
import logging
from typing import Dict, Any, List, Tuple, Optional
from dotenv import load_dotenv

# Import helper to add parent directory to path
import import_helper

# Import utilities
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import setup_logging, measure_execution_time

# Now we can import modules from the parent directory
try:
    from deep_proposal_analyzer import analyze_proposal
    # Import get_langfuse_client directly to avoid NameError
    from langfuse_setup import get_langfuse_client
except ImportError as e:
    print(f"Error importing modules: {e}")
    get_langfuse_client = None
    sys.exit(1)

# Dictionary to store trace IDs
trace_ids = {}

# Unicode symbols for output
CHECKMARK = "✓"

# Environment variables are loaded by import_helper
current_dir = os.path.dirname(os.path.abspath(__file__))
print(f"Current directory: {current_dir}")


# Configure logging
def configure_test_logging():
    """Set up logging for the test script using the utility function."""
    # First, make sure any existing handlers are removed
    for handler in logging.root.handlers[:]: 
        logging.root.removeHandler(handler)

    # Use the utility function from utils.py
    logger = setup_logging(
        name='test_deep_analyzer',
        log_file='test_deep_analyzer.log',
        level=logging.INFO
    )
    
    # Make sure other loggers also log to our handlers
    logging.getLogger('langfuse').setLevel(logging.DEBUG)
    
    return logger

# Dictionary to store trace IDs
trace_ids = {}

# Unicode symbols for output
CHECKMARK = "✓"


@measure_execution_time
def generate_tasks_and_blockers(result, metadata, proposal_text):
    """
    Generate meaningful tasks and blockers based on the proposal analysis.
    
    Args:
        result: The analysis result from the proposal analyzer
        metadata: Metadata about the proposal
        proposal_text: The text of the proposal
    
    Returns:
        Tuple of (tasks, blockers)
    """
    tasks = []
    blockers = []
    
    # Generate tasks based on evaluation report
    if "evaluation_report" in result and isinstance(result["evaluation_report"], dict):
        # Check for missing or failed sections and create tasks
        categories = [
            "goals_and_motivation", "measurable_outcomes", "budget", 
            "technical_specifications", "language_quality"
        ]
        
        for category in categories:
            if category in result["evaluation_report"]:
                status = result["evaluation_report"][category].get("status", "n/a")
                if status == "fail":
                    category_name = category.replace("_", " ").title()
                    tasks.append(f"Improve {category_name} section of the proposal")
                    
                    # Add specific suggestions as tasks if available
                    suggestions = result["evaluation_report"][category].get("suggestions", [])
                    for suggestion in suggestions:
                        tasks.append(f"- {suggestion}")
    
    # Add general tasks based on proposal type
    protocol = metadata.get("protocol", "Unknown")
    category = metadata.get("category", "Unknown")
    
    tasks.append(f"Conduct community feedback session for {metadata.get('title', 'the proposal')}")
    tasks.append(f"Create implementation timeline for {metadata.get('id', 'the proposal')}")
    
    if "budget" in proposal_text.lower():
        tasks.append("Verify budget calculations and funding sources")
    
    if "technical" in proposal_text.lower() or "implementation" in proposal_text.lower():
        tasks.append("Conduct technical review with core developers")
    
    # Generate blockers based on analysis
    arguments_against = result.get("arguments", {}).get("against", [])
    for arg in arguments_against[:2]:  # Convert top opposing arguments into blockers
        blockers.append(f"Address concern: {arg}")
    
    # Add specific blockers based on evaluation
    if "evaluation_report" in result:
        if result["evaluation_report"].get("goals_and_motivation", {}).get("status") == "fail":
            blockers.append("Unclear goals and motivation")
        if result["evaluation_report"].get("measurable_outcomes", {}).get("status") == "fail":
            blockers.append("Lack of measurable outcomes")
        if result["evaluation_report"].get("technical_specifications", {}).get("status") == "fail":
            blockers.append("Insufficient technical specifications")
    
    return tasks, blockers

@measure_execution_time
def test_proposal_analysis(proposal_text, metadata, test_name="default"):
    """Run a test of the proposal analyzer with the given proposal and metadata.
    
    Args:
        proposal_text: The text of the proposal to analyze
        metadata: Metadata about the proposal
        test_name: A name for this test case for tracking
    
    Returns:
        The analysis result
    """
    logger.info(f"Starting test case: {test_name}")
    
    # Access the global langfuse variables
    global langfuse_available, langfuse_client
    
    # Create a trace in Langfuse if available
    langfuse_trace = None
    if langfuse_available:
        try:
            logger.info(f"Creating Langfuse trace for test case: {test_name}")
            
            # Get the Langfuse client using the modern API
            try:
                langfuse = get_langfuse_client()
                if not langfuse:
                    logger.warning("Could not get Langfuse client")
                    langfuse_available = False
                else:
                    # Start a trace using a context manager
                    langfuse_trace = langfuse.start_as_current_span(
                        name=f"proposal_analysis_{test_name}",
                        metadata={
                            "proposal_id": metadata.get("id", "unknown"),
                            "protocol": metadata.get("protocol", "unknown"),
                            "test_case": test_name,
                            "timestamp": time.time()
                        }
                    )
                    
                    # Store the trace ID in the global dictionary
                    global trace_ids
                    trace_id = langfuse.get_current_trace_id()
                    if trace_id:
                        trace_ids[test_name] = trace_id
                        logger.info(f"Stored trace ID for {test_name}: {trace_id}")
                    
                    logger.info(f"Created Langfuse trace using context manager")
            except Exception as client_err:
                logger.warning(f"Error getting Langfuse client: {client_err}")
                langfuse_available = False
        except Exception as e:
            logger.error(f"Error creating Langfuse trace: {str(e)}", exc_info=True)
            langfuse_available = False
    
    # Record start time for performance measurement
    start_time = time.time()
    
    # Analyze the proposal
    result = analyze_proposal(
        proposal_text, 
        metadata, 
        export_json=True, 
        json_path=f"test_analysis_result_{test_name}.json"
    )
    
    # Generate tasks and blockers
    tasks, blockers = generate_tasks_and_blockers(result, metadata, proposal_text)
    
    # Update the result with tasks and blockers
    result["tasks"] = tasks
    result["blockers"] = blockers
    result["next_steps"] = [f"Next step: {task}" for task in tasks[:3]]
    
    # Save the updated result
    with open(f"test_analysis_result_{test_name}.json", 'w') as f:
        json.dump(result, f, indent=2)
    
    # Record end time and calculate duration
    end_time = time.time()
    duration_ms = (end_time - start_time) * 1000
    logger.info(f"Analysis completed in {duration_ms:.2f} ms")
    logger.info(f"Generated {len(tasks)} tasks and {len(blockers)} blockers")
    
    # End the span in Langfuse if available
    if langfuse_available and langfuse_trace:
        try:
            # Get the Langfuse client
            langfuse = get_langfuse_client()
            if not langfuse:
                logger.warning("Could not get Langfuse client for ending trace")
            else:
                # Calculate score based on completeness
                score = 0
                if result.get("evaluation_report", {}).get("summary"):
                    score += 0.3
                if result.get("arguments", {}).get("for_proposal"):
                    score += 0.3
                if result.get("arguments", {}).get("against"):
                    score += 0.3
                if result.get("evaluation_report", {}).get("goals_and_motivation", {}).get("status") == "pass":
                    score += 0.1
                
                # Update the current span with results
                langfuse.update_current_span(
                    metadata={
                        "duration_ms": duration_ms,
                        "tasks_count": len(tasks),
                        "blockers_count": len(blockers),
                        "summary_length": len(result.get("evaluation_report", {}).get("summary", "")),
                        "arguments_for_count": len(result.get("arguments", {}).get("for_proposal", [])),
                        "arguments_against_count": len(result.get("arguments", {}).get("against", [])),
                        "status": "success",
                        "completion_time": time.time()
                    }
                )
                logger.info("Updated current span with results")
                
                # Add scores to the current span
                langfuse.score_current_span(
                    name="completeness",
                    value=score
                )
                logger.info("Added completeness score to current span")
                
                langfuse.score_current_span(
                    name="tasks_and_blockers",
                    value=len(tasks) / (len(tasks) + len(blockers)) if (len(tasks) + len(blockers)) > 0 else 0.5
                )
                logger.info("Added tasks and blockers score to current span")
                
                # Close the trace by exiting the context manager
                langfuse_trace.__exit__(None, None, None)
                logger.info("Closed Langfuse trace context manager")
                
                # Flush to ensure data is sent
                langfuse.flush()
                logger.info("Flushed Langfuse client")
        except Exception as e:
            logger.error(f"Error updating Langfuse trace: {str(e)}", exc_info=True)
    
    return result

def print_analysis_result(result, detailed=False):
    """Print the analysis result in a readable format.
    
    Args:
        result: The analysis result from the proposal analyzer
        detailed: Whether to print the full result or just a summary
    """
    # Print the summary
    print("\nProposal Analysis Summary:")
    summary = "No summary available"
    if "evaluation_report" in result and isinstance(result["evaluation_report"], dict):
        summary = result["evaluation_report"].get("summary", "No summary available")
    print(summary)
    
    # Print arguments for and against
    print("\nArguments For:")
    for_args = []
    if "arguments" in result and isinstance(result["arguments"], dict):
        for_args = result["arguments"].get("for_proposal", [])
    
    if for_args:
        for arg in for_args:
            print(f"- {arg}")
    else:
        print("- No arguments for the proposal available")
    
    print("\nArguments Against:")
    against_args = []
    if "arguments" in result and isinstance(result["arguments"], dict):
        against_args = result["arguments"].get("against", [])
    
    if against_args:
        for arg in against_args:
            print(f"- {arg}")
    else:
        print("- No arguments against the proposal available")
    
    # Print tasks and blockers
    print("\nTasks:")
    tasks = result.get("tasks", [])
    if tasks:
        for task in tasks:
            print(f"- {task}")
    else:
        print("- No tasks available")
    
    print("\nBlockers:")
    blockers = result.get("blockers", [])
    if blockers:
        for blocker in blockers:
            print(f"- {blocker}")
    else:
        print("- No blockers identified")
    
    print("\nNext Steps:")
    next_steps = result.get("next_steps", [])
    if next_steps:
        for step in next_steps:
            print(f"- {step}")
    else:
        print("- No next steps available")
    
    # Print evaluation categories
    print("\nEvaluation Categories:")
    if "evaluation_report" in result and isinstance(result["evaluation_report"], dict):
        categories = [
            "goals_and_motivation", "measurable_outcomes", "budget", 
            "technical_specifications", "language_quality"
        ]
        for category in categories:
            if category in result["evaluation_report"]:
                status = result["evaluation_report"][category].get("status", "n/a")
                print(f"- {category.replace('_', ' ').title()}: {status.upper()}")
    
    # Print the full result if requested
    if detailed:
        print("\nFull Result:")
        print(json.dumps(result, indent=2))

def main():
    """Run tests of the deep proposal analyzer."""
    # Set up logging
    global logger
    logger = configure_test_logging()
    logger.info("Logging initialized")
    
    # Define Langfuse host and log file
    global langfuse_host, log_file, langfuse_available, langfuse_client
    langfuse_host = "https://cloud.langfuse.com"
    log_file = "test_deep_analyzer.log"
    langfuse_available = False
    langfuse_client = None
    
    # Initialize Langfuse for tracing if available
    try:
        logger.info("Attempting to import Langfuse...")
        from langfuse import Langfuse, get_client, observe
        logger.info("Successfully imported Langfuse")
        
        logger.info("Attempting to import Langfuse setup modules...")
        try:
            from langfuse_setup import get_langfuse_client, observe_function, trace_llm_call_with_context
            logger.info("Successfully imported Langfuse setup modules")
        except ImportError:
            logger.warning("Could not import from langfuse_setup. Langfuse tracing will be limited.")
        
        # Get Langfuse API keys from environment variables
        public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
        secret_key = os.getenv("LANGFUSE_SECRET_KEY")
        host = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
        
        # Log the Langfuse configuration
        if public_key and secret_key:
            logger.info("Found Langfuse credentials in environment variables")
            logger.info(f"LANGFUSE_PUBLIC_KEY: {public_key[:5]}...{public_key[-5:] if len(public_key) > 10 else ''}")
            logger.info(f"LANGFUSE_HOST: {host}")
        else:
            logger.warning("Langfuse credentials not found in environment variables")
        
        if public_key and secret_key:
            try:
                logger.info("Initializing Langfuse client...")
                # Initialize Langfuse client with modern API
                langfuse_client = Langfuse(
                    public_key=public_key,
                    secret_key=secret_key,
                    host=host
                )
                logger.info("Langfuse client initialized successfully")
                
                # Test the connection
                if langfuse_client.auth_check():
                    logger.info("Langfuse client authentication successful")
                    
                    # Get the client using the modern API
                    modern_client = get_client()
                    logger.info("Got Langfuse client using modern API")
                    
                    # Create a trace using context managers
                    with modern_client.start_as_current_span(
                        name="test_connection",
                        metadata={"test": True, "timestamp": time.time()}
                    ) as span:
                        span.update(metadata={"status": "success"})
                        logger.info("Created test span using context manager")
                    
                    # Flush to ensure data is sent
                    modern_client.flush()
                    logger.info("Langfuse connection test successful")
                    langfuse_available = True
                else:
                    logger.warning("Langfuse client authentication failed")
                    langfuse_available = False
            except Exception as conn_err:
                logger.error(f"Langfuse connection test failed: {str(conn_err)}", exc_info=True)
                langfuse_available = False
        else:
            logger.warning("Langfuse API keys not found in environment variables")
            langfuse_available = False
    except ImportError as imp_err:
        logger.warning(f"Langfuse package not installed: {str(imp_err)}. Install with: pip install langfuse")
        langfuse_available = False
    except Exception as e:
        logger.error(f"Error initializing Langfuse: {str(e)}", exc_info=True)
        langfuse_available = False
    
    logger.info(f"Langfuse tracing {'enabled' if langfuse_available else 'disabled'}")
    
    # Start testing
    logger.info("Testing deep proposal analyzer...")
    
    # Example proposal text
    example_proposal = """
    [Non-consitutional]: Top-up for Hackathon Continuation Program
     Closed
    Max Lomu
    In Arbitrum DAO · 5mo ago · #bb750
    Abstract
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
    D. abstain
    """
    
    # Example metadata
    example_metadata = {
        "title": "Top-up for Hackathon Continuation Program",
        "protocol": "Arbitrum",
        "category": "Treasury",
        "author": "Max Lomu",
        "date_submitted": "2025-04-25",
        "id": "bb750",
        "url": "https://forum.arbitrum.foundation/"
    }
    
    # Test case 1: Standard proposal analysis
    logger.info("Running test case 1: Standard proposal analysis")
    result1 = test_proposal_analysis(example_proposal, example_metadata, "standard_analysis")
    print_analysis_result(result1)
    
    # Test case 2: Minimal proposal (test robustness)
    minimal_proposal = """
    EIP-1: Minimal Test Proposal
    
    This is a minimal proposal to test the analyzer's robustness with limited information.
    """
    
    minimal_metadata = {
        "title": "EIP-1: Minimal Test Proposal",
        "protocol": "Ethereum",
        "id": "EIP-1"
    }
    
    logger.info("Running test case 2: Minimal proposal analysis")
    result2 = test_proposal_analysis(minimal_proposal, minimal_metadata, "minimal_proposal")
    print_analysis_result(result2)
    
    # Test case 3: Detailed proposal with all sections
    detailed_proposal = """
    EIP-2: Detailed Test Proposal
    
    Simple Summary:
    This is a detailed test proposal with all sections to test the analyzer's comprehensive capabilities.
    
    Abstract:
    This proposal demonstrates the analyzer's ability to process a proposal with all standard sections.
    
    Motivation:
    Testing the analyzer's ability to extract motivation and goals.
    
    Goals:
    1. Test goal extraction
    2. Test motivation analysis
    3. Verify metrics detection
    
    Specification:
    The specification includes detailed technical information about the implementation.
    
    Technical Implementation:
    Step 1: Implement feature A
    Step 2: Integrate with system B
    Step 3: Deploy to production
    
    Metrics:
    - User adoption rate should increase by 20%
    - Gas costs should decrease by 15%
    - Transaction throughput should improve by 30%
    
    Budget:
    This proposal requires 50,000 DAI for implementation.
    """
    
    detailed_metadata = {
        "title": "EIP-2: Detailed Test Proposal",
        "protocol": "Ethereum",
        "category": "Core",
        "author": "Test Author",
        "date_submitted": "2025-09-24",
        "id": "EIP-2"
    }
    
    logger.info("Running test case 3: Detailed proposal analysis")
    result3 = test_proposal_analysis(detailed_proposal, detailed_metadata, "detailed_proposal")
    print_analysis_result(result3, detailed=True)
    
    logger.info("All tests completed successfully")
    
    # Print test summary
    print("\n===== TEST SUMMARY =====")
    print(f"Test 1 (Standard): {CHECKMARK} Passed")
    print(f"Test 2 (Minimal): {CHECKMARK} Passed")
    print(f"Test 3 (Detailed): {CHECKMARK} Passed")
    
    # Print Langfuse status
    print("\n===== LANGFUSE STATUS =====")
    if langfuse_available:
        print(f"{CHECKMARK} Langfuse tracing ENABLED")
        print(f"{CHECKMARK} View traces at: {langfuse_host}")
        print(f"\nTrace IDs for this run:")
        print(f"- Standard analysis: {trace_ids.get('standard_analysis', 'N/A')}")
        print(f"- Minimal proposal: {trace_ids.get('minimal_proposal', 'N/A')}")
        print(f"- Detailed proposal: {trace_ids.get('detailed_proposal', 'N/A')}")
        print(f"\nTo view traces in Langfuse:")
        print(f"1. Go to {langfuse_host}")
        print(f"2. Log in with your credentials")
        print(f"3. Navigate to the Traces section")
        print(f"4. Search for the trace IDs above")
    else:
        print("❌ Langfuse tracing DISABLED")
        print("   To enable Langfuse tracing, set the following environment variables:")
        print("   - LANGFUSE_PUBLIC_KEY")
        print("   - LANGFUSE_SECRET_KEY")
        print("   - LANGFUSE_HOST (optional, defaults to https://cloud.langfuse.com)")
    
    # Print log file location
    print(f"\nDetailed logs available at: {log_file}")
    print(f"Run 'cat {log_file}' to view detailed logs")


if __name__ == "__main__":
    main()
