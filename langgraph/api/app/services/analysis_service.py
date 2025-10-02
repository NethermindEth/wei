"""
Service for analysis operations.
"""

# Standard library imports
import uuid
from typing import Dict, List, Optional, Any

# Local application imports
from app.db.models import Analysis
from app.repositories.analysis_repository import AnalysisRepository
from app.schemas import AnalysisResponse, ProposalArguments
from app.services.langgraph.context import Context
from app.services.langgraph.graph import graph


class AnalysisService:
    """Service for analysis operations."""
    
    def __init__(self, repository: AnalysisRepository):
        """
        Initialize the service with a repository.
        
        Args:
            repository: The repository to use for database operations
        """
        self.repository = repository
    
    def analysis_to_response(self, analysis: Analysis) -> AnalysisResponse:
        """
        Convert an Analysis model to an AnalysisResponse.
        
        Args:
            analysis: The Analysis model to convert
            
        Returns:
            An AnalysisResponse object with data from the Analysis model
        """
        response = AnalysisResponse(
            id=analysis.id,
            proposal_id=analysis.proposal_id,
            result=analysis.result,
            confidence=analysis.confidence,
            details=analysis.details,
            created_at=analysis.created_at,
            updated_at=analysis.updated_at,
        )
        
        # Add arguments if available
        if hasattr(analysis, 'arguments') and analysis.arguments:
            response.arguments = ProposalArguments(**analysis.arguments)
        
        return response
    
    async def analyze_proposal(self, proposal_text: str, proposal_id: Optional[str] = None) -> AnalysisResponse:
        """
        Analyze a proposal and save the results.
        
        Args:
            proposal_text: The text of the proposal to analyze
            proposal_id: Optional ID for the proposal
            
        Returns:
            An AnalysisResponse with the analysis results
        """
        # Create context and runtime
        context = self._create_context()
        context.proposal_text = proposal_text
        runtime = self._create_runtime(context)
        
        # Use the graph for analysis
        result = await graph.ainvoke({
            "task": "analyze_proposal",
            "proposal_text": proposal_text
        }, runtime=runtime)
        
        # Extract the analysis result
        if "analysis_result" not in result:
            raise ValueError("Failed to analyze proposal: no analysis result returned")
            
        analysis_data = result["analysis_result"]
        arguments = result.get("arguments")
        
        # Create and save analysis record
        analysis = await self.repository.create(
            proposal_id=proposal_id or str(uuid.uuid4()),
            result=analysis_data.get("result", "unknown"),
            confidence=float(analysis_data.get("confidence", 0.5)),
            details=analysis_data.get("details", "No details provided"),
            arguments=arguments
        )
        
        # Convert to response model and return
        return self.analysis_to_response(analysis)
    
    async def get_proposal_arguments(self, proposal_text: str, max_arguments: int = 5) -> ProposalArguments:
        """
        Generate arguments for and against a proposal.
        
        Args:
            proposal_text: The text of the proposal
            max_arguments: Maximum number of arguments to generate per side
            
        Returns:
            A ProposalArguments object with the generated arguments
        """
        # Create context and runtime
        context = self._create_context(max_arguments=max_arguments)
        context.proposal_text = proposal_text
        runtime = self._create_runtime(context)
        
        # Use the graph for argument generation
        result = await graph.ainvoke(
            {"proposal_text": proposal_text, "task": "generate_arguments"}, 
            runtime=runtime
        )
        
        # Extract the arguments
        if "arguments" not in result:
            return ProposalArguments(
                for_proposal=["No supporting arguments were generated."],
                against=["No opposing arguments were generated."]
            )
            
        arguments = result["arguments"]
        
        # Process and clean up arguments
        from app.utils import extract_json_from_markdown
        
        # If arguments is a string (possibly JSON in markdown), try to parse it
        if isinstance(arguments, str):
            success, parsed_result = extract_json_from_markdown(arguments)
            if success and isinstance(parsed_result, dict):
                arguments = parsed_result
            else:
                arguments = {}
        
        # Extract and clean up arguments
        for_proposal = arguments.get("for_proposal", [])
        against = arguments.get("against", [])
        
        # Filter out placeholder or empty arguments
        if isinstance(for_proposal, list):
            for_proposal = [arg for arg in for_proposal if arg and not arg.lower().startswith("placeholder")]
        else:
            for_proposal = []
            
        if isinstance(against, list):
            against = [arg for arg in against if arg and not arg.lower().startswith("placeholder")]
        else:
            against = []
        
        # Ensure minimum arguments per side with fallback messages
        if not for_proposal:
            for_proposal = ["No supporting arguments were generated."]
            
        if not against:
            against = ["No opposing arguments were generated."]
        
        return ProposalArguments(
            for_proposal=for_proposal,
            against=against,
        )
    
    def _create_context(self, **kwargs) -> Context:
        """
        Create a Context object with standard configuration.
        
        Args:
            **kwargs: Additional keyword arguments to pass to the Context constructor
            
        Returns:
            A configured Context object
        """
        from app.config import (
            WEI_AGENT_AI_MODEL_PROVIDER, WEI_AGENT_AI_MODEL_NAME,
            WEI_AGENT_OPEN_ROUTER_API_KEY, WEI_AGENT_EXA_API_KEY
        )
        
        context = Context(
            model=f"{WEI_AGENT_AI_MODEL_PROVIDER}/{WEI_AGENT_AI_MODEL_NAME}",
            openrouter_api_key=WEI_AGENT_OPEN_ROUTER_API_KEY,
            exa_api_key=WEI_AGENT_EXA_API_KEY,
            **kwargs
        )
        return context
    
    def _create_runtime(self, context: Context):
        """
        Create a Runtime object with the given context.
        
        Args:
            context: The Context object to use for the runtime
            
        Returns:
            A configured Runtime object
        """
        from langgraph.runtime import Runtime
        return Runtime(context=context)
        
    async def get_analysis_by_id(self, id: uuid.UUID) -> AnalysisResponse:
        """
        Get an analysis by ID.
        
        Args:
            id: The ID of the analysis to retrieve
            
        Returns:
            An AnalysisResponse with the analysis data
            
        Raises:
            ValueError: If the analysis is not found
        """
        analysis = await self.repository.get_by_id(id)
        if not analysis:
            raise ValueError(f"Analysis with ID {id} not found")
            
        return self.analysis_to_response(analysis)
        
    async def get_analysis_by_proposal_id(self, proposal_id: str) -> AnalysisResponse:
        """
        Get the most recent analysis for a proposal.
        
        Args:
            proposal_id: The ID of the proposal
            
        Returns:
            An AnalysisResponse with the analysis data
            
        Raises:
            ValueError: If no analysis is found for the proposal
        """
        analysis = await self.repository.find_by_proposal_id(proposal_id)
        if not analysis:
            raise ValueError(f"No analysis found for proposal with ID {proposal_id}")
            
        return self.analysis_to_response(analysis)
        
    async def get_analyses_by_proposal_id(self, proposal_id: str) -> List[AnalysisResponse]:
        """
        Get all analyses for a proposal.
        
        Args:
            proposal_id: The ID of the proposal
            
        Returns:
            A list of AnalysisResponse objects
            
        Raises:
            ValueError: If no analyses are found for the proposal
        """
        analyses = await self.repository.find_all_by_proposal_id(proposal_id)
        if not analyses:
            raise ValueError(f"No analyses found for proposal with ID {proposal_id}")
            
        return [self.analysis_to_response(analysis) for analysis in analyses]
        
    async def get_analyses(self, 
                          limit: int = 100, 
                          offset: int = 0, 
                          result_filter: Optional[str] = None,
                          min_confidence: Optional[float] = None,
                          max_confidence: Optional[float] = None,
                          proposal_id: Optional[str] = None) -> List[AnalysisResponse]:
        """
        Get analyses with pagination and filtering.
        
        Args:
            limit: Maximum number of analyses to return
            offset: Number of analyses to skip
            result_filter: Optional filter for the result field
            min_confidence: Optional minimum confidence score
            max_confidence: Optional maximum confidence score
            proposal_id: Optional proposal ID filter
            
        Returns:
            A list of AnalysisResponse objects
        """
        analyses = await self.repository.find_all(
            limit=limit,
            offset=offset,
            result_filter=result_filter,
            min_confidence=min_confidence,
            max_confidence=max_confidence,
            proposal_id=proposal_id
        )
        
        return [self.analysis_to_response(analysis) for analysis in analyses]
        
    async def count_analyses(self,
                           result_filter: Optional[str] = None,
                           min_confidence: Optional[float] = None,
                           max_confidence: Optional[float] = None,
                           proposal_id: Optional[str] = None) -> int:
        """
        Count analyses with filtering.
        
        Args:
            result_filter: Optional filter for the result field
            min_confidence: Optional minimum confidence score
            max_confidence: Optional maximum confidence score
            proposal_id: Optional proposal ID filter
            
        Returns:
            The count of matching analyses
        """
        return await self.repository.count(
            result_filter=result_filter,
            min_confidence=min_confidence,
            max_confidence=max_confidence,
            proposal_id=proposal_id
        )
        
    async def custom_evaluate_proposal(self, proposal_text: str, custom_criteria: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate a proposal using custom criteria.
        
        Args:
            proposal_text: The text of the proposal
            custom_criteria: Dictionary of custom criteria to evaluate
            
        Returns:
            A dictionary with evaluation results
            
        Raises:
            ValueError: If the evaluation fails
        """
        # Create context and runtime
        context = self._create_context()
        context.proposal_text = proposal_text
        context.custom_criteria = custom_criteria
        runtime = self._create_runtime(context)
        
        # Use the graph for custom evaluation
        result = await graph.ainvoke(
            {
                "proposal_text": proposal_text, 
                "custom_criteria": custom_criteria,
                "task": "custom_evaluate"
            }, 
            runtime=runtime
        )
        
        # Extract the evaluation result
        if "custom_evaluation" not in result:
            raise ValueError("Failed to evaluate proposal: no evaluation result returned")
            
        evaluation = result["custom_evaluation"]
        
        # If evaluation is a string (possibly JSON in markdown), try to parse it
        from app.utils import extract_json_from_markdown
        if isinstance(evaluation, str):
            success, parsed_result = extract_json_from_markdown(evaluation)
            if success and isinstance(parsed_result, dict):
                evaluation = parsed_result
            else:
                raise ValueError(f"Failed to parse custom evaluation result: {evaluation[:100]}...")
        
        return {
            "summary": evaluation.get("summary", "No summary provided"),
            "response_map": evaluation.get("response_map", {}),
        }
        
    async def search_related_proposals(self, query: str) -> List[Dict[str, Any]]:
        """
        Search for related proposals.
        
        Args:
            query: The search query
            
        Returns:
            A list of related proposals
            
        Raises:
            ValueError: If the search fails or the query is invalid
        """
        if not query or len(query.strip()) < 3:
            raise ValueError("Search query must be at least 3 characters")
            
        # Create context and runtime
        context = self._create_context()
        context.search_query = query
        runtime = self._create_runtime(context)
        
        # Use the graph for search
        result = await graph.ainvoke(
            {"search_query": query, "task": "search_related_proposals"}, 
            runtime=runtime
        )
        
        # Extract and return the search results
        search_results = result.get("search_results", [])
        
        return search_results
        
    async def chat(self, message: str) -> str:
        """
        Chat with the Wei Agent.
        
        Args:
            message: The user's message
            
        Returns:
            The agent's response
            
        Raises:
            ValueError: If the chat fails
        """
        if not message or len(message.strip()) < 1:
            raise ValueError("Message cannot be empty")
            
        # Create context and runtime
        context = self._create_context()
        runtime = self._create_runtime(context)
        
        # Create messages
        from langchain_core.messages import HumanMessage
        messages = [HumanMessage(content=message)]
        
        # Use the graph for chat
        result = await graph.ainvoke({
            "task": "chat",
            "messages": messages
        }, runtime=runtime)
        
        # Extract the response
        if "messages" in result and len(result["messages"]) > 0:
            from langchain_core.messages import AIMessage
            last_message = result["messages"][-1]
            if isinstance(last_message, AIMessage):
                response = last_message.content
            else:
                response = str(last_message)
        else:
            response = "No response from the agent"
        
        return response
