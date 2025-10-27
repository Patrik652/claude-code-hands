"""
Workflow Generator - Convert captured actions to reusable YAML workflows
Analyzes recorded sessions and generates optimized workflow definitions
"""

import yaml
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
from .capture import RecordingSession, CapturedAction

logger = logging.getLogger(__name__)


class WorkflowGenerator:
    """
    Generates YAML workflows from captured recordings

    Features:
    - Convert recordings to YAML
    - Extract variables
    - Detect loops and patterns
    - Add conditional logic
    - Optimize redundant actions
    """

    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize workflow generator

        Args:
            config: Generator configuration
        """
        self.config = config or {}

        # Generation settings
        self.optimize = self.config.get('optimize', True)
        self.extract_variables = self.config.get('extract_variables', True)
        self.detect_loops = self.config.get('detect_loops', True)

        logger.info("Workflow Generator initialized")

    def generate_workflow(
        self,
        session: RecordingSession,
        workflow_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate workflow from recording session

        Args:
            session: Recording session
            workflow_name: Optional workflow name

        Returns:
            Workflow definition dictionary
        """
        workflow_name = workflow_name or session.name

        # Initialize workflow structure
        workflow = {
            'name': workflow_name,
            'description': f'Generated from recording session: {session.session_id}',
            'version': '1.0',
            'metadata': {
                'generated_from': session.session_id,
                'generated_at': session.ended_at,
                'action_count': len(session.actions),
                **session.metadata
            },
            'variables': {},
            'steps': []
        }

        # Extract variables if enabled
        if self.extract_variables:
            workflow['variables'] = self._extract_variables(session.actions)

        # Convert actions to steps
        steps = self._convert_actions_to_steps(session.actions, workflow['variables'])

        # Detect and handle loops
        if self.detect_loops:
            steps = self._detect_and_optimize_loops(steps)

        # Optimize if enabled
        if self.optimize:
            steps = self._optimize_steps(steps)

        workflow['steps'] = steps

        logger.info(f"Generated workflow '{workflow_name}' with {len(steps)} steps")
        return workflow

    def _extract_variables(self, actions: List[CapturedAction]) -> Dict[str, Any]:
        """
        Extract common values as variables

        Args:
            actions: List of captured actions

        Returns:
            Variable definitions
        """
        variables = {}

        # Track parameter values across actions
        value_counts: Dict[str, List] = {}

        for action in actions:
            for param_name, param_value in action.parameters.items():
                # Only consider strings and numbers
                if isinstance(param_value, (str, int, float)):
                    key = f"{action.action_type}_{action.tool_name}_{param_name}"
                    if key not in value_counts:
                        value_counts[key] = []
                    value_counts[key].append(param_value)

        # Extract variables for values that appear multiple times
        var_counter = 1
        for key, values in value_counts.items():
            if len(values) > 1:
                # Get most common value
                most_common = max(set(values), key=values.count)

                # Create variable
                var_name = f"var_{var_counter}"
                variables[var_name] = {
                    'value': most_common,
                    'description': f'Extracted from {key}',
                    'type': type(most_common).__name__
                }
                var_counter += 1

        return variables

    def _convert_actions_to_steps(
        self,
        actions: List[CapturedAction],
        variables: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Convert captured actions to workflow steps

        Args:
            actions: Captured actions
            variables: Extracted variables

        Returns:
            List of workflow steps
        """
        steps = []

        for idx, action in enumerate(actions, 1):
            step = {
                'step': idx,
                'action': f"{action.action_type}.{action.tool_name}",
                'parameters': self._substitute_variables(action.parameters, variables),
            }

            # Add optional fields
            if action.result:
                step['expected_result'] = self._simplify_result(action.result)

            if not action.success:
                step['on_error'] = 'continue'  # Or 'stop', 'retry'

            if action.duration_ms and action.duration_ms > 1000:
                step['timeout'] = int(action.duration_ms * 1.5)  # 1.5x observed duration

            steps.append(step)

        return steps

    def _substitute_variables(
        self,
        parameters: Dict[str, Any],
        variables: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Replace parameter values with variable references

        Args:
            parameters: Original parameters
            variables: Available variables

        Returns:
            Parameters with variable substitutions
        """
        substituted = parameters.copy()

        for param_name, param_value in parameters.items():
            # Check if value matches any variable
            for var_name, var_def in variables.items():
                if param_value == var_def['value']:
                    substituted[param_name] = f"${{{var_name}}}"
                    break

        return substituted

    def _simplify_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simplify result for workflow definition

        Args:
            result: Full result

        Returns:
            Simplified result
        """
        # Only keep essential fields
        essential_fields = ['status', 'success', 'element_count', 'found', 'visible']

        simplified = {}
        for field in essential_fields:
            if field in result:
                simplified[field] = result[field]

        return simplified

    def _detect_and_optimize_loops(self, steps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Detect repeating patterns and convert to loops

        Args:
            steps: Workflow steps

        Returns:
            Optimized steps with loops
        """
        # Simple pattern detection (can be enhanced)
        optimized = []
        i = 0

        while i < len(steps):
            # Check for repeating sequences
            pattern_length = self._find_pattern_length(steps, i)

            if pattern_length > 1:
                # Found a pattern
                pattern_steps = steps[i:i + pattern_length]
                repeat_count = self._count_pattern_repeats(steps, i, pattern_length)

                # Create loop step
                loop_step = {
                    'step': len(optimized) + 1,
                    'action': 'loop',
                    'iterations': repeat_count,
                    'steps': pattern_steps
                }

                optimized.append(loop_step)
                i += pattern_length * repeat_count
            else:
                # No pattern, add step as-is
                optimized.append(steps[i])
                i += 1

        return optimized

    def _find_pattern_length(self, steps: List[Dict], start_idx: int) -> int:
        """Find length of repeating pattern starting at index"""
        max_pattern_length = min(10, (len(steps) - start_idx) // 2)

        for pattern_length in range(1, max_pattern_length + 1):
            if self._is_pattern_repeating(steps, start_idx, pattern_length):
                return pattern_length

        return 1  # No pattern found

    def _is_pattern_repeating(self, steps: List[Dict], start_idx: int, pattern_length: int) -> bool:
        """Check if pattern repeats"""
        if start_idx + pattern_length * 2 > len(steps):
            return False

        pattern = steps[start_idx:start_idx + pattern_length]
        next_sequence = steps[start_idx + pattern_length:start_idx + pattern_length * 2]

        # Compare actions (not exact parameters)
        return all(
            p['action'] == n['action']
            for p, n in zip(pattern, next_sequence)
        )

    def _count_pattern_repeats(self, steps: List[Dict], start_idx: int, pattern_length: int) -> int:
        """Count how many times pattern repeats"""
        count = 0
        idx = start_idx

        while idx + pattern_length <= len(steps):
            if self._is_pattern_repeating(steps, idx, pattern_length):
                count += 1
                idx += pattern_length
            else:
                break

        return max(count, 1)

    def _optimize_steps(self, steps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Optimize workflow steps

        Args:
            steps: Original steps

        Returns:
            Optimized steps
        """
        optimized = []
        prev_step = None

        for step in steps:
            # Remove redundant consecutive actions
            if prev_step and self._is_redundant(prev_step, step):
                logger.debug(f"Removing redundant step: {step['action']}")
                continue

            # Merge similar actions if possible
            if prev_step and self._can_merge(prev_step, step):
                merged = self._merge_steps(prev_step, step)
                optimized[-1] = merged
                prev_step = merged
            else:
                optimized.append(step)
                prev_step = step

        return optimized

    def _is_redundant(self, step1: Dict, step2: Dict) -> bool:
        """Check if two steps are redundant"""
        # Same action with same parameters
        return (
            step1['action'] == step2['action'] and
            step1.get('parameters') == step2.get('parameters')
        )

    def _can_merge(self, step1: Dict, step2: Dict) -> bool:
        """Check if two steps can be merged"""
        # For now, don't merge - can be enhanced
        return False

    def _merge_steps(self, step1: Dict, step2: Dict) -> Dict:
        """Merge two steps"""
        # Implementation for merging similar steps
        return step1

    def save_workflow(self, workflow: Dict[str, Any], output_path: Path) -> Path:
        """
        Save workflow to YAML file

        Args:
            workflow: Workflow definition
            output_path: Output file path

        Returns:
            Path to saved file
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            yaml.dump(workflow, f, default_flow_style=False, sort_keys=False)

        logger.info(f"Saved workflow to {output_path}")
        return output_path

    def generate_and_save(
        self,
        session: RecordingSession,
        output_path: Path,
        workflow_name: Optional[str] = None
    ) -> Path:
        """
        Generate and save workflow in one step

        Args:
            session: Recording session
            output_path: Output path
            workflow_name: Optional workflow name

        Returns:
            Path to saved workflow
        """
        workflow = self.generate_workflow(session, workflow_name)
        return self.save_workflow(workflow, output_path)
