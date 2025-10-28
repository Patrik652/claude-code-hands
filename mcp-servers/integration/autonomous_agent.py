"""
Autonomous Agent - Intelligent AI agent with vision, memory, and learning
Can analyze situations, learn from past experiences, and execute complex workflows
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any
from .orchestrator import AIOrchestrator

logger = logging.getLogger(__name__)


class AutonomousAgent:
    """
    Intelligent autonomous agent that combines all system capabilities

    Features:
    - Analyzes situations using AI vision
    - Searches memory for similar past experiences
    - Makes intelligent decisions based on context
    - Executes appropriate actions
    - Learns from results
    - Handles errors gracefully
    - Adapts behavior over time
    """

    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize autonomous agent

        Args:
            config: Agent configuration
        """
        self.config = config or {}

        # Initialize orchestrator
        self.orchestrator = AIOrchestrator(self.config.get('orchestrator', {}))

        # Agent settings
        self.confidence_threshold = self.config.get('confidence_threshold', 0.7)
        self.max_retries = self.config.get('max_retries', 3)
        self.learning_enabled = self.config.get('learning_enabled', True)

        # State
        self.current_task = None
        self.task_history = []

        logger.info(f"Autonomous Agent initialized (confidence_threshold={self.confidence_threshold})")

    async def analyze_and_act(
        self,
        screenshot_path: str,
        goal: str,
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Analyze current situation and take appropriate action

        Args:
            screenshot_path: Path to screenshot
            goal: What we're trying to achieve
            context: Additional context

        Returns:
            Result of analysis and action
        """
        try:
            # 1. Analyze current situation with vision AI
            logger.info(f"Analyzing situation for goal: {goal}")
            analysis = await self._analyze_situation(screenshot_path, goal)

            # 2. Search memory for similar past experiences
            similar_experiences = await self._find_similar_experiences(goal, analysis)

            # 3. Decide on action based on analysis and memory
            action_plan = await self._decide_action(goal, analysis, similar_experiences, context)

            # 4. Execute action
            result = await self._execute_action_plan(action_plan)

            # 5. Learn from result if enabled
            if self.learning_enabled:
                await self._learn_from_result(goal, analysis, action_plan, result)

            return {
                'success': True,
                'goal': goal,
                'analysis': analysis,
                'action_plan': action_plan,
                'result': result,
                'learned': self.learning_enabled
            }

        except Exception as e:
            logger.error(f"Error in analyze_and_act: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def _analyze_situation(self, screenshot_path: str, goal: str) -> Dict[str, Any]:
        """
        Analyze current situation using vision AI

        Args:
            screenshot_path: Screenshot to analyze
            goal: Current goal

        Returns:
            Analysis results
        """
        prompt = f"""
        Analyze this screen in the context of the following goal: {goal}

        Please identify:
        1. What is currently visible on the screen
        2. What UI elements are available for interaction
        3. What actions would help achieve the goal
        4. Any obstacles or issues present
        5. Confidence level (0.0-1.0) for recommended actions
        """

        result = await self.orchestrator.execute_secure_action(
            action_type='vision',
            tool_name='analyze_screen',
            parameters={
                'screenshot_path': screenshot_path,
                'prompt': prompt
            }
        )

        if result.get('success'):
            return result.get('result', {})
        else:
            raise RuntimeError(f"Vision analysis failed: {result.get('error')}")

    async def _find_similar_experiences(
        self,
        goal: str,
        current_analysis: Dict
    ) -> List[Dict]:
        """
        Find similar past experiences in memory

        Args:
            goal: Current goal
            current_analysis: Current situation analysis

        Returns:
            List of similar memories
        """
        # Search for similar goals
        result = await self.orchestrator.execute_secure_action(
            action_type='memory',
            tool_name='search',
            parameters={
                'query': goal,
                'limit': 5
            }
        )

        if result.get('success'):
            memories = result.get('results', {})
            return memories.get('results', []) if hasattr(memories, 'get') else []
        else:
            logger.warning(f"Memory search failed: {result.get('error')}")
            return []

    async def _decide_action(
        self,
        goal: str,
        analysis: Dict,
        similar_experiences: List[Dict],
        context: Optional[Dict]
    ) -> Dict[str, Any]:
        """
        Decide what action to take based on analysis and past experiences

        Args:
            goal: Current goal
            analysis: Current situation analysis
            similar_experiences: Similar past experiences
            context: Additional context

        Returns:
            Action plan
        """
        # Extract confidence from analysis
        confidence = analysis.get('confidence', 0.5)

        # Check if we have successful past experiences
        successful_experiences = [
            exp for exp in similar_experiences
            if exp.get('success', False)
        ]

        action_plan = {
            'goal': goal,
            'confidence': confidence,
            'strategy': None,
            'actions': [],
            'fallback_actions': []
        }

        # Decision logic
        if confidence >= self.confidence_threshold and successful_experiences:
            # High confidence + past success = use proven approach
            action_plan['strategy'] = 'proven'
            action_plan['actions'] = self._extract_actions_from_memory(successful_experiences[0])
            logger.info(f"Using proven strategy (confidence: {confidence:.2f})")

        elif confidence >= self.confidence_threshold:
            # High confidence but no past success = try new approach based on analysis
            action_plan['strategy'] = 'exploratory'
            action_plan['actions'] = self._generate_actions_from_analysis(analysis)
            logger.info(f"Using exploratory strategy (confidence: {confidence:.2f})")

        else:
            # Low confidence = cautious approach with fallbacks
            action_plan['strategy'] = 'cautious'
            action_plan['actions'] = self._generate_cautious_actions(analysis)
            action_plan['fallback_actions'] = self._generate_fallback_actions(goal)
            logger.info(f"Using cautious strategy (confidence: {confidence:.2f})")

        return action_plan

    def _extract_actions_from_memory(self, memory: Dict) -> List[Dict]:
        """Extract actions from successful memory"""
        # Parse memory content to extract actions
        # This is simplified - real implementation would parse workflow data
        return [
            {
                'action_type': 'memory',
                'tool_name': 'replay_workflow',
                'parameters': {'memory_id': memory.get('id')}
            }
        ]

    def _generate_actions_from_analysis(self, analysis: Dict) -> List[Dict]:
        """Generate actions based on AI analysis"""
        # Extract recommended actions from analysis
        # This is simplified - real implementation would parse AI recommendations
        recommended_actions = analysis.get('recommended_actions', [])

        actions = []
        for action in recommended_actions:
            actions.append({
                'action_type': action.get('type', 'browser'),
                'tool_name': action.get('tool', 'click'),
                'parameters': action.get('parameters', {})
            })

        return actions

    def _generate_cautious_actions(self, analysis: Dict) -> List[Dict]:
        """Generate safe, cautious actions"""
        # Start with observation/information gathering
        return [
            {
                'action_type': 'vision',
                'tool_name': 'analyze_screen',
                'parameters': {
                    'prompt': 'Provide detailed analysis of all interactive elements'
                }
            }
        ]

    def _generate_fallback_actions(self, goal: str) -> List[Dict]:
        """Generate fallback actions if primary approach fails"""
        return [
            {
                'action_type': 'memory',
                'tool_name': 'search',
                'parameters': {
                    'query': f'alternative approaches for {goal}',
                    'limit': 3
                }
            }
        ]

    async def _execute_action_plan(self, action_plan: Dict) -> Dict[str, Any]:
        """
        Execute the action plan

        Args:
            action_plan: Plan to execute

        Returns:
            Execution results
        """
        results = []
        success = True

        for action in action_plan['actions']:
            try:
                result = await self.orchestrator.execute_secure_action(
                    action_type=action['action_type'],
                    tool_name=action['tool_name'],
                    parameters=action['parameters']
                )

                results.append(result)

                if not result.get('success', False):
                    success = False
                    logger.warning(f"Action failed: {action['tool_name']}")

                    # Try fallback if available
                    if action_plan.get('fallback_actions'):
                        logger.info("Attempting fallback actions")
                        fallback_result = await self._execute_fallback(
                            action_plan['fallback_actions']
                        )
                        results.append(fallback_result)

                    break

            except Exception as e:
                logger.error(f"Error executing action: {e}")
                success = False
                break

        return {
            'success': success,
            'strategy': action_plan['strategy'],
            'results': results
        }

    async def _execute_fallback(self, fallback_actions: List[Dict]) -> Dict:
        """Execute fallback actions"""
        for action in fallback_actions:
            result = await self.orchestrator.execute_secure_action(
                action_type=action['action_type'],
                tool_name=action['tool_name'],
                parameters=action['parameters']
            )

            if result.get('success'):
                return result

        return {'success': False, 'error': 'All fallback actions failed'}

    async def _learn_from_result(
        self,
        goal: str,
        analysis: Dict,
        action_plan: Dict,
        result: Dict
    ):
        """
        Learn from the result and update memory

        Args:
            goal: Goal that was attempted
            analysis: Situation analysis
            action_plan: Action plan that was executed
            result: Execution result
        """
        try:
            # Store workflow in memory
            await self.orchestrator.execute_secure_action(
                action_type='memory',
                tool_name='store_workflow',
                parameters={
                    'content': f"Goal: {goal}, Strategy: {action_plan['strategy']}",
                    'workflow_name': f"auto_{goal.replace(' ', '_')}",
                    'steps': action_plan['actions'],
                    'success': result.get('success', False),
                    'metadata': {
                        'confidence': action_plan.get('confidence'),
                        'strategy': action_plan.get('strategy')
                    }
                }
            )

            logger.info(f"Learned from result: goal={goal}, success={result.get('success')}")

        except Exception as e:
            logger.error(f"Failed to learn from result: {e}")

    async def execute_goal_autonomously(
        self,
        goal: str,
        initial_screenshot: Optional[str] = None,
        max_iterations: int = 10
    ) -> Dict[str, Any]:
        """
        Autonomously work towards a goal with multiple iterations

        Args:
            goal: Goal to achieve
            initial_screenshot: Initial screenshot (optional)
            max_iterations: Maximum iterations to attempt

        Returns:
            Final result
        """
        logger.info(f"Starting autonomous execution of goal: {goal}")

        iteration = 0
        current_screenshot = initial_screenshot
        goal_achieved = False
        history = []

        while iteration < max_iterations and not goal_achieved:
            iteration += 1
            logger.info(f"Iteration {iteration}/{max_iterations}")

            # Capture current state if no screenshot provided
            if not current_screenshot:
                # Would capture screenshot here
                current_screenshot = "/tmp/current_screen.png"

            # Analyze and act
            result = await self.analyze_and_act(
                screenshot_path=current_screenshot,
                goal=goal,
                context={'iteration': iteration}
            )

            history.append(result)

            # Check if goal is achieved
            goal_achieved = self._check_goal_achievement(goal, result)

            if goal_achieved:
                logger.info(f"Goal achieved after {iteration} iterations!")
                break

            # Prepare for next iteration
            current_screenshot = None  # Will capture fresh screenshot

        return {
            'success': goal_achieved,
            'goal': goal,
            'iterations': iteration,
            'history': history
        }

    def _check_goal_achievement(self, goal: str, result: Dict) -> bool:
        """
        Check if goal has been achieved

        Args:
            goal: Target goal
            result: Latest result

        Returns:
            True if goal achieved
        """
        # Simplified check - real implementation would be more sophisticated
        return result.get('success', False) and result.get('confidence', 0) > 0.8

    def get_agent_stats(self) -> Dict[str, Any]:
        """
        Get agent statistics

        Returns:
            Agent statistics
        """
        # Calculate success/failure counts from task history
        successful_actions = sum(1 for task in self.task_history if task.get('success', False))
        failed_actions = len(self.task_history) - successful_actions

        return {
            'total_decisions': len(self.task_history),
            'successful_actions': successful_actions,
            'failed_actions': failed_actions,
            'current_task': self.current_task,
            'learning_enabled': self.learning_enabled,
            'confidence_threshold': self.confidence_threshold,
            'orchestrator_status': self.orchestrator.get_status()
        }
