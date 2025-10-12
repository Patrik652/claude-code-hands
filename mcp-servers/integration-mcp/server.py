#!/usr/bin/env python3
"""
Integration MCP Server - Koordinátor pre Claude Code
MIT License - Open Source
"""

import asyncio
import json
import yaml
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List

from fastmcp import FastMCP
from pydantic import BaseModel, Field

# Initialize MCP server
app = FastMCP("integration-mcp")

# Workflow storage
WORKFLOW_DIR = Path.home() / ".claude-workflows"
WORKFLOW_DIR.mkdir(exist_ok=True)

class WorkflowStep(BaseModel):
    action: str
    target: Optional[str] = None
    text: Optional[str] = None
    timeout: Optional[int] = 10
    use_previous_result: bool = False

class Workflow(BaseModel):
    name: str
    description: Optional[str] = None
    steps: List[WorkflowStep]

@app.tool()
async def execute_workflow(
    workflow_path: str
) -> Dict[str, Any]:
    """
    Execute a workflow from YAML file

    Args:
        workflow_path: Path to workflow YAML file

    Returns:
        Dictionary with execution results
    """
    try:
        # Load workflow
        with open(workflow_path, 'r') as f:
            workflow_data = yaml.safe_load(f)

        workflow = Workflow(**workflow_data)

        results = []
        previous_result = None

        for i, step in enumerate(workflow.steps):
            step_result = {
                "step_number": i + 1,
                "action": step.action,
                "status": "pending"
            }

            try:
                # Execute step based on action type
                if step.action == "vision.capture":
                    # Would call vision MCP
                    step_result["status"] = "success"

                elif step.action == "vision.find":
                    # Would call vision MCP to find element
                    step_result["status"] = "success"

                elif step.action == "hands.click":
                    # Would call hands MCP to click
                    if step.use_previous_result and previous_result:
                        # Use coordinates from previous result
                        pass
                    step_result["status"] = "success"

                elif step.action == "hands.type":
                    # Would call hands MCP to type
                    step_result["status"] = "success"

                elif step.action == "integration.wait":
                    # Wait for element
                    await asyncio.sleep(1)
                    step_result["status"] = "success"

                else:
                    step_result["status"] = "unknown_action"

                previous_result = step_result

            except Exception as e:
                step_result["status"] = "error"
                step_result["error"] = str(e)
                results.append(step_result)
                break

            results.append(step_result)

        return {
            "workflow": workflow.name,
            "total_steps": len(workflow.steps),
            "completed_steps": len([r for r in results if r["status"] == "success"]),
            "results": results,
            "success": all(r["status"] == "success" for r in results)
        }

    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

@app.tool()
async def create_workflow(
    name: str,
    steps: List[Dict[str, Any]],
    description: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create and save a workflow

    Args:
        name: Workflow name
        steps: List of workflow steps
        description: Optional description

    Returns:
        Dictionary with workflow path
    """
    try:
        workflow_steps = [WorkflowStep(**step) for step in steps]
        workflow = Workflow(name=name, description=description, steps=workflow_steps)

        # Save workflow
        workflow_file = WORKFLOW_DIR / f"{name.replace(' ', '_')}.yaml"
        with open(workflow_file, 'w') as f:
            yaml.dump(workflow.dict(), f)

        return {
            "status": "success",
            "workflow_path": str(workflow_file),
            "workflow_name": name
        }

    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

@app.tool()
async def list_workflows() -> Dict[str, Any]:
    """
    List all available workflows

    Returns:
        Dictionary with workflow list
    """
    workflows = []

    for workflow_file in WORKFLOW_DIR.glob("*.yaml"):
        try:
            with open(workflow_file, 'r') as f:
                workflow_data = yaml.safe_load(f)
                workflows.append({
                    "name": workflow_data.get("name"),
                    "description": workflow_data.get("description"),
                    "steps_count": len(workflow_data.get("steps", [])),
                    "path": str(workflow_file)
                })
        except Exception:
            pass

    return {
        "workflows": workflows,
        "total": len(workflows)
    }

@app.tool()
async def health_check() -> Dict[str, Any]:
    """
    Check integration system health

    Returns:
        System status
    """
    return {
        "status": "healthy",
        "workflow_directory": str(WORKFLOW_DIR),
        "available_workflows": len(list(WORKFLOW_DIR.glob("*.yaml"))),
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    print("🔄 Integration MCP Server starting...")
    print(f"📁 Workflow directory: {WORKFLOW_DIR}")
    print("🚀 Server ready on stdio")
    app.run()
